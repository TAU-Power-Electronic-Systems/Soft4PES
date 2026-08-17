"""
Model predictive control (MPC) with optimized pulse pattern (OPP) 
for induction machine (IM) stator current control.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.mpc.common.mpc_base import MPCBase
from soft4pes.control.opp.utils import load_switching_angles, read_switching_angles
from soft4pes.control.common.utils import wrap_theta
from soft4pes.utils.conversions import alpha_beta_2_abc, dq_2_alpha_beta


class IMOppCurrCtr(MPCBase, Controller):
    """
    MPC with OPPs for induction machine stator current control.
    
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
                 opp_file,
                 m_tol=1e-3,
                 disc_method='forward_euler'):

        # Additional attributes for the OPP-based MPC
        self.opp_data = SimpleNamespace(file=opp_file,
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

    def make_opp_reference_vector(self, sys, ws, iS_ref, v_ang):
        # Number of switching events within the prediction horizon
        n = len(self.t_nom)

        # Preallocate the reference vector for the prediction horizon
        horizon_vector = np.zeros(2 * n)

        for ell in range(n):
            theta_pred = sys.base.w * ws * self.t_nom[ell]
            R_rot = np.array([[np.cos(theta_pred), -np.sin(theta_pred)],
                              [np.sin(theta_pred),
                               np.cos(theta_pred)]])
            horizon_vector[ell * 2:ell * 2 + 2] = R_rot.dot(iS_ref)

            # Add harmonic reference
            if 'harm_ref' in self.opp_data.lut_opp.data_vars:
                theta_harm = wrap_theta(theta_pred + v_ang - np.pi +
                                        np.pi / 2) + np.pi
                ref = self.opp_data.lut_opp['harm_ref'].sel(
                    modulation_index=self.opp_data.m,
                    theta_index=theta_harm,
                    method='nearest').values
                horizon_vector[ell * 2:ell * 2 +
                               2] += ref * sys.conv.v_dc / sys.par.Xsigma / ws

        return horizon_vector

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

        ws = self.input.ws

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
        m = 2 / sys.conv.v_dc * np.linalg.norm(v_conv)

        # Update the switching angles and positions based on the modulation index
        self.update_opp(m)

        t_new, U_new, u0 = read_switching_angles(self.opp_data.angles,
                                                 self.opp_data.positions,
                                                 vs_ang, self.Np * self.Ts, ws,
                                                 sys)

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

            y_ref_pred = self.make_opp_reference_vector(
                sys, ws, iS_ref, vs_ang)
            d_vector = np.zeros(2 * n)
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
        u_abc = 2 / sys.conv.v_dc * alpha_beta_2_abc(v_conv)

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
