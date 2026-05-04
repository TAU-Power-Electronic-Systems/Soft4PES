"""Model predictive control (MPC) for induction machine (IM) stator current control."""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.mpc.common.mpc_base import MPCBase
from soft4pes.utils import dq_2_alpha_beta


class IMCurrCtr(MPCBase, Controller):
    """
    MPC for induction machine stator current control.
    
    The controller tracks the stator current in the alpha-beta frame. The current reference 
    is calculated based on the torque reference and rotor flux magnitude.

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

        # Output matrix, track the stator current
        C = np.block([np.eye(2), np.zeros((2, 2))])

        # Weighting matrix for the tracked variables
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
        
        Calculates the stator current reference from the torque reference, predicts it over 
        the horizon, and solves the MPC optimization problem to obtain the optimal control action.

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

        T_ref = self.input.T_ref

        # Calculate the reference stator current based on the torque and rotor flux magnitude
        # references. Rotor-field orientation is assumed.
        iS_ref_dq = sys.calc_stator_current(sys.psiR_mag_ref, T_ref)

        # Get the rotor flux angle and calculate the reference in alpha-beta frame
        theta = np.arctan2(sys.psiR[1], sys.psiR[0])
        iS_ref = dq_2_alpha_beta(iS_ref_dq, theta)
        self.input.iS_ref = iS_ref

        # Predict the current reference over the prediction horizon
        Ts_pu = self.Ts * sys.base.w
        y_ref_pred = self.make_reference_vector(sys.par.ws, Ts_pu, iS_ref)

        # Solve the control problem
        u_abc = self.solver(sys, self, y_ref_pred)
        self.u_km1_abc = u_abc

        self.output = SimpleNamespace(u_abc=u_abc)

        return self.output
