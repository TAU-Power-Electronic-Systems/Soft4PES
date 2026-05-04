"""Model predictive control (MPC) for grid-connected converters with LCL filter. The controller 
tracks only the filter capacitor voltage."""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import dq_2_alpha_beta
from soft4pes.control.common.controller import Controller
from soft4pes.control.mpc.common.mpc_base import MPCBase


class LCLGridVcCtr(MPCBase, Controller):
    """
    MPC for filter capacitor voltage tracking in LCL-filtered grid-connected systems.
    
    The controller tracks only the filter capacitor voltage reference in the alpha-beta frame. 
    Moreover, converter current limits have been included as soft constraints in the MPC problem. 

    The soft constraints are penalized in the cost function with a weight of 10e6, which ensures
    that the converter current limits are respected.

    Parameters
    ----------
    solver : solver object
        Solver for an MPC algorithm.
    Np : int
        Prediction horizon steps.
    lambda_u : float
        Weighting factor for the control effort.
    I_conv_max : float
        Maximum converter current [p.u.].
    disc_method : str, optional
        Discretization method for the state-space model ('forward_euler' or 
        'exact_discretization'). Default is 'exact_discretization'.
    """

    def __init__(self,
                 solver,
                 Np,
                 lambda_u,
                 I_conv_max,
                 disc_method='exact_discretization'):

        # Output matrix, track the capacitor voltage
        C = np.block([np.zeros((2, 2)), np.zeros((2, 2)), np.eye(2)])

        # Weighting matrix for the tracked variables
        Q = np.eye(2)

        # Output matrix for the converter current, which is constrained with soft constraints
        C_soft_constr = np.block(
            [np.eye(2), np.zeros((2, 2)),
             np.zeros((2, 2))])

        # Weights for the soft constraints and the maximum values for the abc-frame variables
        soft_constr_weights = 10e6
        soft_constraints_max = I_conv_max

        Controller.__init__(self)
        MPCBase.__init__(self,
                         C=C,
                         Q=Q,
                         Np=Np,
                         lambda_u=lambda_u,
                         solver=solver,
                         C_soft_constr=C_soft_constr,
                         soft_constr_weights=soft_constr_weights,
                         soft_constraints_max=soft_constraints_max,
                         disc_method=disc_method)

    def execute(self, sys, kTs):
        """
        Execute one control step of the MPC algorithm.
        
        Transforms the capacitor voltage reference from dq to alpha-beta frame, predicts grid 
        voltage disturbance over the horizon, and solves the MPC optimization problem with soft 
        constraints to obtain the optimal control action.

        Parameters
        ----------
        sys : system object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        SimpleNamespace
            Output namespace with field `u_abc` containing the converter three-phase switch
            position or modulating signal.
        """

        self.get_ctr_state_space(sys, self.Ts)

        # Get the grid voltage and save it for future use
        vg = sys.get_grid_voltage(kTs)
        Ts_pu = self.Ts * sys.base.w
        d_pred = self.make_disturbance_vector(sys.par.wg, Ts_pu, vg)

        # Get the reference at step k
        vc_ref_dq = self.input.vc_ref_dq

        # Get the grid-voltage angle and calculate the reference in alpha-beta frame
        theta = np.arctan2(vg[1], vg[0])
        vc_ref = dq_2_alpha_beta(vc_ref_dq, theta)

        # Predict the output (capacitor voltage) reference within the horizon
        y_ref_pred = self.make_reference_vector(sys.par.wg, Ts_pu, vc_ref)

        # Solve the control problem
        u_abc = self.solver(sys, self, y_ref_pred, d_pred)
        self.u_km1_abc = u_abc

        self.output = SimpleNamespace(u_abc=u_abc)

        return self.output
