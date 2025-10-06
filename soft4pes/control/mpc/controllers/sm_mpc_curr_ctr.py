""" Model predictive current control for a permanent magnet synchronous machine (PMSM)."""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.utils.conversions import alpha_beta_2_dq, dq_2_alpha_beta


class SMMpcCurrCtr(Controller):
    """
    Model predictive current control for a permanent magnet synchronous machine (PMSM). 
    The controller aims to track the stator current reference, provided by the outer loop or user.

    Parameters
    ----------
    solver : solver object
        Solver for an MPC algorithm.
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon steps.
    disc_method : str, optional
        Discretization method for the state-space model. Default is 'forward_euler'.

    Attributes
    ----------
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon steps.
    disc_method : str
        Discretization method for the state-space model.
    u_km1_abc : 1 x 3 ndarray of floats
        Previous (step k-1) three-phase switch position or modulating signal.
    state_space : SimpleNamespace 
        The state-space model of the system.
    solver : solver object
        Solver for MPC.
    C : 2 x 2 ndarray of ints
        Output matrix.
    """

    def __init__(self, solver, lambda_u, Np, disc_method='forward_euler'):
        super().__init__()
        self.lambda_u = lambda_u
        self.Np = Np
        self.disc_method = disc_method
        self.u_km1_abc = np.array([0, 0, 0])
        self.state_space = None
        self.solver = solver

        # Output matrix
        self.C = np.array([[1, 0], [0, 1]])

    def execute(self, sys, kTs):
        """
        Perform MPC.

        Parameters
        ----------
        sys : system object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        1 x 3 ndarray of floats
            Three-phase switch position or modulating signals.
        """

        iS_ref_dq = self.input.iS_ref_dq
        self.input.iS_ref_dq = iS_ref_dq
        iS_ref = dq_2_alpha_beta(iS_ref_dq, sys.theta_el)

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
        u_abc = self.solver(sys, self, y_ref)
        self.u_km1_abc = u_abc

        self.output = SimpleNamespace(u_abc=u_abc)

        return self.output

    def get_next_state(self, sys, xk, u_abc, k):
        """
        Get the next state of the system.

        Parameters
        ----------
        sys : system object
            The system model.
        xk : 1 x 2 ndarray of floats
            The current state of the system.
        u_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        k : int
            The solver prediction step.

        Returns
        -------
        1 x 2 ndarray of floats
            The next state of the system.
        """

        # Assume that the electrical rotor angle varies slowly, and the model is constant over the
        # prediction horizon
        sys.cont_state_space = sys.get_continuous_state_space()
        self.state_space = sys.get_discrete_state_space(
            self.Ts, self.disc_method)

        xk_dq = alpha_beta_2_dq(xk, sys.theta_el)
        x_kp1_dq = np.dot(self.state_space.A, xk_dq) + np.dot(
            self.state_space.B1, u_abc) + self.state_space.B2

        return dq_2_alpha_beta(x_kp1_dq, sys.theta_el)
