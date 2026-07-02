"""
Open-loop OPP implementation for induction machine control.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common import Controller
from soft4pes.control.common.utils import get_modulating_signal
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta
from soft4pes.control.opp.utils import read_switching_angles, load_switching_angles


class IMOpenLoopOPP(Controller):
    """
    Open-loop optimized pulse pattern (OPP) implementation for induction machine control.

    Parameters
    ----------
    sys : object
        System model.
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

    def __init__(self, sys, d, opp_file, m_tol=1e-3):
        super().__init__()
        self.sys = sys
        self.m = None
        self.d = d
        self.angles = None
        self.positions = None
        self.lut_opp = None
        self.m_tol = m_tol
        self.opp_file = opp_file

    def set_sampling_interval(self, Ts):
        """
        Set the sampling interval and define parameters

        Parameters
        ----------
        Ts : float
            Sampling interval [s].

        """
        self.Ts = Ts

        # Load the OPP data
        self.lut_opp = load_switching_angles(self.opp_file, self.sys)

    def execute(self, sys, kTs):
        """
        Execute the open loop OPP controller

        Parameters
        ----------
        sys : object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        output : SimpleNamespace
            Output from the controller including the switching time instants and the corresponding 
            switch position.
        """

        # Calculate the transformation angle
        theta = np.arctan2(sys.psiR[1], sys.psiR[0])

        # Calculate load angle
        gamma = np.arcsin(sys.par.D / sys.par.Xm * self.input.T_ref /
                          self.input.psiS_mag_ref / self.input.psiR_mag_ref /
                          sys.par.kT)

        # Get stator current reference in dq frame
        iS_ref = self.input.iS_ref
        iS_ref_dq = alpha_beta_2_dq(iS_ref, theta)

        ws = self.input.ws

        # Calculate converter voltage vector
        v_conv = dq_2_alpha_beta(
            np.array([1, 0]), theta + gamma +
            np.pi / 2) + sys.par.Rs * dq_2_alpha_beta(iS_ref_dq, theta)

        # Compute angle and modulation index
        vs_ang = np.arctan2(v_conv[1], v_conv[0])
        m = 2 / sys.conv.v_dc * np.linalg.norm(v_conv) * ws

        # Read the switching angles and positions from the LUT
        # If the modulation index has changed significantly, update the angles and positions
        if self.m is None or not np.isclose(m, self.m, rtol=self.m_tol):
            self.m = m
            self.angles = self.lut_opp['switching_angles'].sel(
                modulation_index=m, method='nearest').values
            self.positions = self.lut_opp['switch_positions'].sel(
                modulation_index=m, method='nearest').values

        t_nom, U, u0 = read_switching_angles(self.angles, self.positions,
                                             vs_ang, self.Ts, ws, sys)

        u_abc = get_modulating_signal(dq_2_alpha_beta(v_conv, theta),
                                      sys.conv.v_dc)

        self.output = SimpleNamespace(t_switch=t_nom / self.Ts,
                                      switch_pos=np.transpose(U),
                                      u_abc=u_abc)

        return self.output
