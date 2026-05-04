"""Model predictive control (MPC) for the grid current."""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import dq_2_alpha_beta
from soft4pes.control.common.controller import Controller
from soft4pes.control.mpc.common.mpc_base import MPCBase


class RLGridCurrCtr(MPCBase, Controller):
    """
    Model predictive control (MPC) for grid current. The converter is connected directly to the 
    grid.

    Parameters
    ----------
    solver : solver object
        Solver for an MPC algorithm.
    Np : int
        Prediction horizon steps.
    lambda_u : float
        Weighting factor for the control effort.
    disc_method : str, optional
        Discretization method for the state-space model ('forward_euler' or 
        'exact_discretization'). Default is 'forward_euler'.
    """

    def __init__(self, solver, Np, lambda_u, disc_method='forward_euler'):

        # Output matrix
        C = np.eye(2)
        Q = np.eye(2)

        Controller.__init__(self)
        MPCBase.__init__(self,
                         C=C,
                         Q=Q,
                         Np=Np,
                         lambda_u=lambda_u,
                         solver=solver,
                         disc_method=disc_method)

        self.vg = np.array([0, 0])

    def execute(self, sys, kTs):
        """
        Execute one control step of the MPC algorithm.
        
        Transforms the current reference from dq to alpha-beta frame using the grid voltage angle, 
        predicts grid voltage disturbance over the horizon, and solves the MPC optimization problem 
        to obtain the optimal control action.

        Parameters
        ----------
        sys : system object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        SimpleNamespace
            Output namespace with field `u_abc` containing the three-phase
            switch position or modulating signal.
        """

        self.get_ctr_state_space(sys, self.Ts)

        # Get the grid voltage and save it for future use
        vg = sys.get_grid_voltage(kTs)

        # Get the reference for current step
        ig_ref_dq = self.input.ig_ref_dq

        # Get the grid-voltage angle and calculate the reference in alpha-beta frame
        theta = np.arctan2(vg[1], vg[0])
        ig_ref = dq_2_alpha_beta(ig_ref_dq, theta)

        # Predict the current reference over the prediction horizon
        Ts_pu = self.Ts * sys.base.w
        y_ref_pred = self.make_reference_vector(sys.par.wg, Ts_pu, ig_ref)

        # Predict the grid voltage disturbance over the horizon
        d_pred = self.make_disturbance_vector(sys.par.wg, Ts_pu, vg)

        # Solve the control problem
        u_abc = self.solver(sys, self, y_ref_pred, d_pred)
        self.u_km1_abc = u_abc

        self.output = SimpleNamespace(u_abc=u_abc)

        return self.output
