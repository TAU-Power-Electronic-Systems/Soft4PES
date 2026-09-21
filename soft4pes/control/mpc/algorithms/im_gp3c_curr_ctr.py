"""
Gradient-based Predictive Pulse Pattern Control (GP3C) for induction machine (IM) stator current control.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.mpc.common.mpc_base import MPCBase
from soft4pes.control.modulation.utils import get_opp_switching_instants
from soft4pes.utils.conversions import alpha_beta_2_abc, dq_2_alpha_beta


class IMGP3CCurrCtr(MPCBase, Controller):
    """
    Gradient-based Predictive Pulse Pattern Control (GP3C) for induction machine stator current control.
    
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
        Execute one control step of the algorithm.
        
        Formulates the stator current reference over the prediction horizon
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

        ws = self.input.ws
        angles = self.input.angles
        positions = self.input.positions
        harm_ref = self.input.harm_ref

        # Calculate the transformation angle
        theta = np.arctan2(sys.psiR[1], sys.psiR[0])

        # Calculate load angle
        gamma = np.arcsin(sys.par.D / sys.par.Xm * self.input.T_ref /
                          self.input.psiS_mag_ref / self.input.psiR_mag_ref /
                          sys.par.kT)

        # Get stator current reference
        iS_ref = self.input.iS_ref

        # Calculate converter voltage vector
        v_conv = dq_2_alpha_beta(
            np.array([1, 0]) * ws,
            theta + gamma + np.pi / 2) + sys.par.Rs * iS_ref

        # Compute angle and modulation index
        vs_ang = np.arctan2(v_conv[1], v_conv[0])

        # Get the switching time instants of the nominal OPP within the prediction horizon
        t_opp, U_opp = get_opp_switching_instants(angles, positions, vs_ang,
                                                  self.Np * self.Ts, ws, sys)

        # Remove/add used/saved switch positions from the previous control step
        self.read_modified_time_instants(t_opp, U_opp)

        # Number of switching events within the prediction horizon
        n = len(self.t_nom)

        # Run the controller if there are switching events within the prediction horizon
        if n > 0:
            # Create the reference vector for the stator current over the prediction horizon
            y_ref_pred = self.make_opp_reference_vector(
                sys, ws, iS_ref, harm_ref, vs_ang)

            # Disturbance vector
            d_vector = np.zeros(2 * n)

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

        # Modulating signal (plotting only)
        u_abc = 2 / sys.conv.v_dc * alpha_beta_2_abc(v_conv)

        # Pad the switching time instants and switch positions to a fixed size for output
        t_nom_pad = 2 * np.ones(20)
        U_pad = np.zeros((3, 20))
        n = len(t_opt)
        t_nom_pad[:n] = t_opt
        U_pad[:, :n] = U_opt

        self.output = SimpleNamespace(t_switch=t_nom_pad / self.Ts,
                                      switch_pos=np.transpose(U_pad),
                                      u_abc=u_abc)

        return self.output
