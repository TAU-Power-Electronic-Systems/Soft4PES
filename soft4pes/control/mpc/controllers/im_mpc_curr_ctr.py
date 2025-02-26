""" Model predictive current control for an induction machine."""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.utils import dq_2_alpha_beta


class IMMpcCurrCtr(Controller):
    """
    Model predictive current control for an induction machine. The controller aims to track
    the stator current in the alpha-beta frame. The current reference is calculated based on the
    torque reference.

    Parameters
    ----------
    solver : solver object
        Solver for an MPC algorithm.
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon.

    Attributes
    ----------
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon steps.
    u_km1_abc : 1 x 3 ndarray of floats
        Previous (step k-1) three-phase switch position or modulating signal.
    state_space : SimpleNamespace 
        The state-space model of the system.
    solver : solver object
        Solver for MPC.
    C : 2 x 4 ndarray of ints
        Output matrix.
    """

    def __init__(self, solver, lambda_u, Np):
        super().__init__()
        self.lambda_u = lambda_u
        self.Np = Np
        self.u_km1_abc = np.array([0, 0, 0])
        self.state_space = SimpleNamespace()
        self.solver = solver

        # Output matrix
        self.C = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])

    def execute(self, sys, conv, kTs):
        """
        Perform MPC.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        1 x 3 ndarray of floats
            Three-phase switch position or modulating signals.
        """

        self.state_space = sys.get_discrete_state_space(conv.v_dc, self.Ts)

        T_ref = self.input.T_ref

        # Calculate the reference stator current based on the torque and rotor flux magnitude
        # references
        iS_ref_dq = sys.calc_stator_current(sys.psiR_mag_ref, T_ref)

        # Get the rotor flux angle and calculate the reference in alpha-beta frame
        theta = np.arctan2(sys.x[3], sys.x[2])
        iS_ref = dq_2_alpha_beta(iS_ref_dq, theta)
        self.input.iS_ref = iS_ref

        # Predict the current reference over the prediction horizon
        # Make a rotation matrix
        Ts_pu = self.Ts * sys.base.w
        delta_theta = sys.par.ws * Ts_pu
        R_ref = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                          [np.sin(delta_theta), np.cos(delta_theta)]])

        # Predict the reference by rotating the current reference
        y_ref = np.zeros((self.Np + 1, 2))
        y_ref[0, :] = iS_ref
        for ell in range(self.Np):
            y_ref[ell + 1, :] = np.dot(R_ref, y_ref[ell, :])

        # Solve the control problem
        uk_abc = self.solver(sys, conv, self, y_ref)
        self.u_km1_abc = uk_abc

        self.output = SimpleNamespace(uk_abc=uk_abc)

        return self.output

    def get_next_state(self, sys, xk, uk_abc, k):
        """
        Get the next state of the system.

        Parameters
        ----------
        sys : system object
            The system model.
        xk : 1 x 4 ndarray of floats
            The current state of the system.
        uk_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        k : int
            The solver prediction step.

        Returns
        -------
        1 x 4 ndarray of floats
            The next state of the system.
        """

        return np.dot(self.state_space.A, xk) + np.dot(self.state_space.B,
                                                       uk_abc)
