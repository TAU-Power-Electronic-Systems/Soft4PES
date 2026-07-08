"""
Model predictive control (MPC) with optimized pulse pattern (OPP) 
for induction machine (IM) stator current control.
"""

from turtle import dot
from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.mpc.common.mpc_base import MPCBase
from soft4pes.control.opp.utils import load_switching_angles, read_switching_angles
from soft4pes.control.common.utils import wrap_theta
from soft4pes.utils.conversions import alpha_beta_2_abc, alpha_beta_2_dq, dq_2_abc, dq_2_alpha_beta

import os
import numpy as np
import scipy.io as sio


class GridOppCurrCtr(MPCBase, Controller):
    """
    MPC with OPPs for grid-connected inverter current control.

    The controller tracks the grid current in the alpha-beta frame. The current reference
    is calculated based on the power reference and grid voltage.


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
    d : int
        Number of switching angles.
    opp_file : str
        The name of the OPP data file.   
    m_tol : float, optional
        Tolerance for modulation index change to 
        update the switching angles and positions.

    Attributes
    ----------
    sys : object
        System model.
    m : float
        Current modulation index.
    angles : 1 x d ndarray
        Switching angles.
    positions : 1 x d ndarray
        Switching positions corresponding to the switching angles.
    lut : xarray Dataset
        Lookup table containing the switching angles and positions 
        for different modulation indices.
    d : int
        Number of switching angles.
    m_tol : float
        Tolerance for modulation index change to 
        update the switching angles and positions.
    opp_file : str
        The name of the OPP data file.  
    """

    def __init__(self,
                 solver,
                 Np,
                 lambda_u,
                 d,
                 opp_file,
                 m_tol=1e-3,
                 disc_method='exact_discretization'):

        # Additional attributes for the OPP-based MPC
        self.opp_data = SimpleNamespace(d=d,
                                        file=opp_file,
                                        m_tol=m_tol,
                                        m=None,
                                        angles=None,
                                        positions=None,
                                        lut_opp=None)

        # Nominal switching time instants
        self.t_nom = np.array([])
        self.U = np.array([]).reshape(3, 0)
        self.U_used = 0

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

    def set_sampling_interval(self, Ts):
        """
        Set the sampling interval and load the OPP data

        Parameters
        ----------
        Ts : float
            Sampling interval [s].
        """
        self.Ts = Ts

        # Load the OPP data
        self.opp_data.lut_opp = load_switching_angles(self.opp_data.file)

    def update_opp(self, m):
        """
        Update the switching angles and positions based on the modulation index.

        Parameters
        ----------
        m : float
            Modulation index.
        """

        # Read the switching angles and positions from the LUT
        # If the modulation index has changed significantly, update the angles and positions
        if self.opp_data.m is None or not np.isclose(
                m, self.opp_data.m, rtol=self.opp_data.m_tol):
            self.opp_data.m = m
            self.opp_data.angles = self.opp_data.lut_opp[
                'switching_angles'].sel(modulation_index=m,
                                        method='nearest').values
            self.opp_data.positions = self.opp_data.lut_opp[
                'switch_positions'].sel(modulation_index=m,
                                        method='nearest').values
            self.opp_data.harm_ref = self.opp_data.lut_opp['harm_ref'].sel(
                modulation_index=m, method='nearest').values

    def execute(self, sys, kTs):
        """
        Execute one control step of the MPC algorithm.
        
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

        # Get the transformation angle from the outer loop. If not available, use the grid voltage
        # angle.
        if getattr(self.input, "theta", None) is not None:
            theta = self.input.theta
        else:
            vg = sys.get_grid_voltage(kTs)
            theta = np.arctan2(vg[1], vg[0])

        # Get the reference for current step (converter current equals grid current)
        i_conv_ref_dq = alpha_beta_2_dq(self.input.ig_ref, theta)
        vg = sys.get_grid_voltage(kTs)
        vg_dq = alpha_beta_2_dq(vg, theta)

        # Compute the needed converter voltage vector
        v_conv_dq = (sys.par.R_fc +
                     sys.par.Rg) * i_conv_ref_dq + sys.par.wg * (
                         sys.par.X_fc + sys.par.Xg) * np.array(
                             [-i_conv_ref_dq[1], i_conv_ref_dq[0]]) + vg_dq

        # Converter voltage angle
        v_conv_ang = theta + np.arctan2(v_conv_dq[1], v_conv_dq[0])
        m = 2 / sys.conv.v_dc * np.linalg.norm(v_conv_dq)

        # Update the switching angles and positions based on the modulation index
        self.update_opp(m)

        # Read the switching events from the OPP
        t_new, U_new, u0 = read_switching_angles(self.opp_data.angles,
                                                 self.opp_data.positions,
                                                 v_conv_ang, self.Np * self.Ts,
                                                 sys.par.wg, sys)

        # Remove switching events that have already been used in the previous control step
        t_new = t_new[self.U_used:]
        U_new = U_new[:, self.U_used:]
        self.U_used = 0

        # Append saved switching events from the previous control step
        self.t_nom = np.concatenate((self.t_nom, t_new))
        self.U = np.hstack((self.U, U_new))

        # Number of switching events within the prediction horizon
        n = len(self.t_nom)

        # Run the controller if there are switching events within the prediction horizon
        if n > 0:
            U = self.U
            # Preallocate the reference vector for the prediction horizon
            horizon_vector = np.zeros(2 * n)
            d_vector = np.zeros(2 * n)

            for ell in range(n):
                theta_pred = sys.base.w * sys.par.wg * self.t_nom[ell]
                R_rot = np.array(
                    [[np.cos(theta_pred + theta), -np.sin(theta_pred + theta)],
                     [np.sin(theta_pred + theta),
                      np.cos(theta_pred + theta)]])
                horizon_vector[ell * 2:ell * 2 + 2] = R_rot.dot(i_conv_ref_dq)

                d_vector[ell * 2:ell * 2 + 2] = R_rot.dot(vg_dq)

                # Add harmonic reference
                theta_harm = wrap_theta(theta_pred + v_conv_ang - np.pi +
                                        np.pi / 2) + np.pi
                ref = self.opp_data.lut_opp['harm_ref'].sel(
                    modulation_index=self.opp_data.m,
                    theta_index=theta_harm,
                    method='nearest').values
                horizon_vector[
                    ell * 2:ell * 2 +
                    2] += ref * sys.conv.v_dc / 2 / sys.par.Xg / sys.par.wg

            y_ref_pred = horizon_vector

            t_opt = self.solver(sys, self, y_ref_pred, d_vector)

            # Save/remove switching instants and switch positions for the next control step
            t_opt_Ts = np.sum(t_opt < self.Ts)
            t_nom_Ts = np.sum(self.t_nom < self.Ts)
            t_diff = t_nom_Ts - t_opt_Ts

            if t_diff > 0:
                self.t_nom = np.linspace(1e-6, t_diff * 1e-6, t_diff)
                self.U = U[:, t_opt_Ts:t_nom_Ts]
            elif t_diff < 0:
                self.U_used = -t_diff
                self.t_nom = np.array([])
                self.U = np.array([]).reshape(3, 0)
            else:
                self.t_nom = np.array([])
                self.U = np.array([]).reshape(3, 0)

            if t_opt_Ts > 0:
                self.u_km1_abc = U[:, t_opt_Ts - 1]
        else:
            # Keep the previous switch position if there are no
            # switching events within the prediction horizon
            t_opt = np.array([0])
            U = self.u_km1_abc.reshape(3, 1)

        # Modulating signal
        u_abc = 2 / sys.conv.v_dc * dq_2_abc(v_conv_dq, theta)

        # Pad the switching time instants and switch positions to a fixed size for output
        t_nom_pad = 2 * np.ones(10)
        U_pad = np.zeros((3, 10))
        n = len(t_opt)
        t_nom_pad[:n] = t_opt
        U_pad[:, :n] = U

        self.output = SimpleNamespace(t_switch=t_nom_pad / self.Ts,
                                      switch_pos=np.transpose(U_pad),
                                      u_abc=u_abc)
        return self.output
