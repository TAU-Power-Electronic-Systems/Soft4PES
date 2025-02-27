"""
Model predictive control (MPC) for the control of the capacitor voltage. 
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import dq_2_alpha_beta
from soft4pes.control.common.controller import Controller


class LCLVcMpcCtr(Controller):
    """
    Model predictive control (MPC) for the control of the capacitor voltage.

    Parameters
    ----------
    solver : solver object
        Solver for an MPC algorithm.
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon steps.
    I_conv_max : float
        Maximum converter current [p.u.].
    xi_I_conv : float
        Slack variable weight for the current constraint.

    Attributes
    ----------
    solver : solver object
        Solver for MPC.
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon.
    u_km1_abc : 1 x 3 ndarray of floats
        Previous (step k-1) three-phase switch position or modulating signal.
    state_space : SimpleNamespace
        The state-space model of the system.
    vg : 1 x 2 ndarray of floats
        Grid voltage [p.u.].
    R : 1 x 1 ndarray of floats
        Weight matrix for the soft constraints.
    c : 1 x 1 ndarray of floats
        State constraints.
    C_constr : 2 x 6 ndarray of ints
        Output matrix for the constrained states.
    C : 2 x 6 ndarray of ints
        System output matrix.
    Q : 2 x 2 ndarray of ints
        Weighting matrix for the output variables.
    """

    def __init__(self, solver, lambda_u, Np, I_conv_max=1.2, xi_I_conv=1e6):
        super().__init__()
        self.solver = solver
        self.lambda_u = lambda_u
        self.Np = Np
        self.u_km1_abc = np.array([0, 0, 0])
        self.state_space = SimpleNamespace()
        self.vg = np.array([0, 0])

        # Weight matrix for the constraints (R) and vector for state constraints (c)
        self.R = np.array([[xi_I_conv]])
        self.c = np.array([[I_conv_max]])

        # Output matrix for the constrained states
        self.C_constr = np.block(
            [np.eye(2), np.zeros((2, 2)),
             np.zeros((2, 2))])

        # Output matrix (C) and weighting matrix (Q) for the output variables
        self.C = np.block([[np.zeros((2, 2)), np.zeros((2, 2)), np.eye(2)]])
        self.Q = np.eye(2)

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
        SimpleNamespace
            SimpleNameSpace containing the converter three-phase switch position or modulating 
            signal.
        """

        # Get the discrete state-space model of the system
        self.state_space = sys.get_discrete_state_space(conv.v_dc, self.Ts)

        # Get the grid voltage and save it for future use
        self.vg = sys.get_grid_voltage(kTs)

        # Get the reference at step k
        vc_ref_dq = self.input.vc_ref_dq

        # Get the grid-voltage angle and calculate the reference in alpha-beta frame
        theta = np.arctan2(self.vg[1], self.vg[0])
        vc_ref = dq_2_alpha_beta(vc_ref_dq, theta)

        # Make a rotation matrix
        Ts_pu = self.Ts * sys.base.w
        delta_theta = sys.par.wg * Ts_pu
        R_rot = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                          [np.sin(delta_theta), np.cos(delta_theta)]])

        # Predict the output (capacitor voltage) reference within the horizon based on the reference
        # value at step k
        y_ref = np.zeros((self.Np + 1, 2))
        y_ref[0, :] = vc_ref
        for ell in range(self.Np):
            y_ref[ell + 1, :] = np.dot(R_rot, y_ref[ell, :])

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
        xk : 1 x 6 ndarray of floats
            The current state of the system.
        uk_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        k : int
            The solver prediction step.

        Returns
        -------
        1 x 6 ndarray of floats
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
