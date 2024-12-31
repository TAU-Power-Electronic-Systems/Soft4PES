""" Model predictive current control (MPC) for RL grid."""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import dq_2_alpha_beta
from soft4pes.control.common.controller import Controller


class RLGridMpcCurrCtr(Controller):
    """
    Model predictive control (MPC) for RL grid. The controller aims to track
    the grid current in the alpha-beta frame.

    Parameters
    ----------
    solver : solver object
        Solver for an MPC algorithm.
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon steps.

    Attributes
    ----------
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon.
    u_km1_abc : 1 x 3 ndarray of floats
        Previous (step k-1) three-phase switch position or modulating signal.
    state_space : SimpleNamespace 
        The state-space model of the system.
    solver : solver object
        Solver for MPC.
    vg : 1 x 2 ndarray of floats
        Grid voltage [p.u.].
    C : 2 x 2 ndarray of ints
        Output matrix.
    """

    def __init__(self, solver, lambda_u, Np):
        super().__init__()
        self.lambda_u = lambda_u
        self.Np = Np
        self.u_km1_abc = np.array([0, 0, 0])
        self.state_space = SimpleNamespace()
        self.solver = solver
        self.vg = np.array([0, 0])

        # Output matrix
        self.C = np.array([[1, 0], [0, 1]])

    def execute(self, sys, conv, kTs):
        """
        Perform MPC and save the controller data.

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

        # Get the discrete state-space model of the system
        self.state_space = sys.get_discrete_state_space(conv.v_dc, self.Ts)

        # Get the grid voltage and save it for future use
        self.vg = sys.get_grid_voltage(kTs)

        # Get the reference for current step
        i_ref_dq = self.input.i_ref_dq

        # Get the grid-voltage angle and calculate the reference in alpha-beta frame
        theta = np.arctan2(self.vg[1], self.vg[0])
        ig_ref = dq_2_alpha_beta(i_ref_dq, theta)

        # Predict the current reference over the prediction horizon
        # Make a rotation matrix
        Ts_pu = self.Ts * sys.base.w
        delta_theta = sys.par.wg * Ts_pu
        R_ref = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                          [np.sin(delta_theta), np.cos(delta_theta)]])

        # Predict the reference by rotating the current reference
        y_ref = np.zeros((self.Np + 1, 2))
        y_ref[0, :] = ig_ref
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
        xk : 1 x 2 ndarray of floats
            The current state of the system.
        uk_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        k : int
            The solver prediction step.

        Returns
        -------
        1 x 2 ndarray of floats
            The next state of the system.
        """

        # Get the grid voltage at step k by rotating it
        Ts_pu = self.Ts * sys.base.w
        delta_theta = k * sys.par.wg * Ts_pu
        R = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                        [np.sin(delta_theta), np.cos(delta_theta)]])

        vg_k = np.dot(R, self.vg)

        return np.dot(self.state_space.A, xk) + np.dot(
            self.state_space.B1, uk_abc) + np.dot(self.state_space.B2, vg_k)
