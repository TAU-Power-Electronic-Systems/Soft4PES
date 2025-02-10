"""
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import dq_2_alpha_beta
from soft4pes.control.common.controller import Controller


class LCLVcMpcCtr(Controller):

    def __init__(self, solver, lambda_u, Np, I_conv_max=1.2, xi_I_conv=1e6):
        super().__init__()
        self.lambda_u = lambda_u
        self.Np = Np
        self.u_km1_abc = np.array([0, 0, 0])
        self.state_space = SimpleNamespace()
        self.solver = solver
        self.vg = np.array([0, 0])

        # self.R = np.array([[xi_I_conv]])
        self.R = 1e6 * np.eye(2)
        # self.c = np.array([[I_conv_max]])
        self.c = np.array([1.2, 1.2]).reshape(-1, 1)
        # self.C_lim = np.block([np.eye(2), np.zeros((2, 2)), np.zeros((2, 2))])
        self.C_lim = np.block([[np.eye(2),
                                np.zeros((2, 2)),
                                np.zeros((2, 2))],
                               [np.zeros((2, 2)),
                                np.zeros((2, 2)),
                                np.eye(2)]])
        self.C = np.block([[np.zeros((2, 2)), np.zeros((2, 2)), np.eye(2)]])

        self.Q = np.eye(2)

    def execute(self, sys, conv, kTs):

        # Get the discrete state-space model of the system
        self.state_space = sys.get_discrete_state_space(conv.v_dc, self.Ts)

        # Get the grid voltage and save it for future use
        self.vg = sys.get_grid_voltage(kTs)

        # Get the reference for current step
        vc_ref_dq = self.input.vc_ref_dq

        # Get the grid-voltage angle and calculate the reference in alpha-beta frame
        theta = np.arctan2(self.vg[1], self.vg[0])
        vc_ref = dq_2_alpha_beta(vc_ref_dq, theta)

        # Predict the capacitor voltage reference over the prediction horizon
        # Make a rotation matrix
        Ts_pu = self.Ts * sys.base.w
        delta_theta = sys.par.wg * Ts_pu
        R_ref = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                          [np.sin(delta_theta), np.cos(delta_theta)]])

        # Predict the reference by rotating the current reference
        y_ref = np.zeros((self.Np + 1, 2))
        y_ref[0, :] = vc_ref
        for ell in range(self.Np):
            y_ref[ell + 1, :] = np.dot(R_ref, y_ref[ell, :])

        # Solve the control problem
        uk_abc = self.solver(sys, conv, self, y_ref)
        slack = uk_abc[3 * self.Np:]
        uk_abc = uk_abc[:3]
        self.u_km1_abc = uk_abc

        self.output = SimpleNamespace(uk_abc=uk_abc, slack=slack)

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
