"""
Gradient-based Predictive Pulse Pattern Control (GP3C) for a grid connected system.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.mpc.common.mpc_base import MPCBase
from soft4pes.control.modulation.utils import get_opp_switching_instants
from soft4pes.utils.conversions import alpha_beta_2_dq


class GridGP3CCurrCtr(MPCBase, Controller):
    """
    GP3C for a grid connected system.

    The controller tracks the stator current reference in the alpha-beta frame.

    Parameters
    ----------
    solver : solver object
        Solver for the MPC algorithm.
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
        C = np.eye(2)

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
        Execute one control step of the algorithm.
        
        Formulates the grid current reference over the prediction horizon
        and solves the MPC optimization problem.

        Parameters
        ----------
        sys : system object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        SimpleNamespace
            The optimal switching time instants and the corresponding switch positions.
        """

        angles = self.input.angles
        positions = self.input.positions
        harm_ref = self.input.harm_ref

        # Get the transformation angle from the outer loop. If not available, use the grid voltage
        # angle.
        if getattr(self.input, "theta", None) is not None:
            theta = self.input.theta
        else:
            vg = sys.get_grid_voltage(kTs)
            theta = np.arctan2(vg[1], vg[0])

        # Get the reference for current step (converter current equals grid current)
        iG_ref = self.input.ig_ref
        i_conv_ref_dq = alpha_beta_2_dq(iG_ref, theta)
        vg = sys.get_grid_voltage(kTs)
        vg_dq = alpha_beta_2_dq(vg, theta)

        # Compute the needed converter voltage vector
        v_conv_dq = (sys.par.R_fc +
                     sys.par.Rg) * i_conv_ref_dq + sys.par.wg * (
                         sys.par.X_fc + sys.par.Xg) * np.array(
                             [-i_conv_ref_dq[1], i_conv_ref_dq[0]]) + vg_dq

        # Converter voltage angle
        v_conv_ang = theta + np.arctan2(v_conv_dq[1], v_conv_dq[0])

        # Get the switching time instants of the nominal OPP within the prediction horizon
        t_opp, U_opp = get_opp_switching_instants(angles, positions,
                                                  v_conv_ang,
                                                  self.Np * self.Ts,
                                                  sys.par.wg, sys)

        # Remove/add used/saved switch positions from the previous control step
        self.read_modified_time_instants(t_opp, U_opp)

        # Number of switching events within the prediction horizon
        n = len(self.t_nom)

        # Run the controller if there are switching events within the prediction horizon
        if n > 0:
            # Create the reference vector for the grid current over the prediction horizon
            y_ref_pred = self.make_opp_reference_vector(
                sys, sys.par.wg, iG_ref, harm_ref, v_conv_ang)

            # Disturbance vector
            d_vector_pred = self.make_opp_reference_vector(
                sys, sys.par.wg, vg, None, 0)
            d_vector = np.concatenate((vg, d_vector_pred))

            self.M = self.get_gradient_matrix(self, sys, sys.x, d_vector)

            t_opt = self.solver(sys, self, y_ref_pred, d_vector)
            U_opt = self.U_nom

            # Write the modified switching time instants and switch positions for the next control step
            self.write_modified_time_instants(self.Ts, t_opt)
        else:
            # Keep the previous switch position if there are no
            # switching events within the prediction horizon
            t_opt = np.array([0])
            U_opt = self.u_km1_abc.reshape(3, 1)

        # Pad the switching time instants and switch positions to a fixed size for output
        t_nom_pad = 2 * np.ones(20)
        U_pad = np.zeros((3, 20))
        n = len(t_opt)
        t_nom_pad[:n] = t_opt
        U_pad[:, :n] = U_opt

        self.output = SimpleNamespace(t_switch=t_nom_pad / self.Ts,
                                      switch_pos=np.transpose(U_pad),
                                      u_abc=np.zeros(3))

        return self.output
