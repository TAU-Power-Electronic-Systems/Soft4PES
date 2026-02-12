"""Model predictive control (MPC) for the stator current of a permanent magnet synchronous machine 
(PMSM)."""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.mpc.common.mpc_base import MPCBase
from soft4pes.utils.conversions import dq_2_alpha_beta


class PMSMCurrCtr(MPCBase, Controller):
    """
    MPC for PMSM stator current control.
    
    The controller tracks the stator current reference in the alpha-beta frame. The PMSM model is 
    time-varying due to rotor position dependency, requiring state-space model updates at each 
    control step.

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

    def execute(self, sys, kTs):
        """
        Execute one control step of the MPC algorithm.
        
        Transforms the current reference from dq to alpha-beta frame using the electrical angle,
        predicts permanent magnet flux disturbance over the horizon, and solves the MPC 
        optimization problem to obtain the optimal control action.

        Parameters
        ----------
        sys : system object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        SimpleNamespace
            Output namespace with field `u_abc` containing the three-phase switch position or 
            modulating signal.
        """

        self.get_ctr_state_space(sys, self.Ts)

        # Get the current reference in the alpha-beta frame
        iS_ref_dq = self.input.iS_ref_dq
        self.input.iS_ref_dq = iS_ref_dq
        iS_ref = dq_2_alpha_beta(iS_ref_dq, sys.theta_el)

        # Predict the current reference over the prediction horizon
        Ts_pu = self.Ts * sys.base.w
        y_ref_pred = self.make_reference_vector(sys.par.ws, Ts_pu, iS_ref)

        # Predict the disturbance (permanent magnet flux) over the horizon
        d_pred = self.make_disturbance_vector(sys.par.ws, Ts_pu, sys.psi_PM)

        # Solve the control problem
        u_abc = self.solver(sys, self, y_ref_pred, d_pred)
        self.u_km1_abc = u_abc

        self.output = SimpleNamespace(u_abc=u_abc)
        return self.output
