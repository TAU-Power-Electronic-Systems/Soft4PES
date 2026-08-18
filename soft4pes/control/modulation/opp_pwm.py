"""
Optimized pulse pattern (OPP) modulator. The modulator generates a list of the switching angles and 
positions based on the modulation index and the converter voltage angle. The switching angles and 
positions are read from a lookup table (LUT) that is loaded from a specified OPP file.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.modulation.utils import get_opp_switching_instants, load_switching_angles_from_file
from soft4pes.utils.conversions import abc_2_alpha_beta


class OPPPWM(Controller):
    """
    Optimized pulse pattern (OPP) modulator.

    Parameters
    ----------
    sys : object
        System model.
    opp_file : str
        Path to the OPP file.
    m_tol : float (optional)
        Tolerance for modulation index change to update the OPP data.

    Attributes
    ----------
    sys : object
        System model.
    m_tol : float
        Tolerance for modulation index change to update the OPP data.
    lut_opp : xarray.Dataset
        Lookup table (LUT) containing the switching angles and positions for different modulation
        indices.
    opp_data : SimpleNamespace
        A SimpleNamespace object that contains the current modulation index and the corresponding 
        switching angles and positions.
    """

    def __init__(self, sys, switching_frequency, m_tol=1e-3):
        super().__init__()
        self.sys = sys

        self.m_tol = m_tol
        self.lut_opp = load_switching_angles_from_file(self.sys, switching_frequency)

        # Namespace to store the OPPs for the current modulation index
        self.opp_data = SimpleNamespace(m=None, angles=None, positions=None)

    def update_opp(self, m):
        """
        Update the switching angles and positions based on the modulation index.

        Parameters
        ----------
        m : float
            Modulation index.
        """

        # Read the switching angles and positions from the LUT.
        # If the modulation index change exceeds the tolerance, update the angles and positions.
        if self.opp_data.m is None or not np.isclose(
                m, self.opp_data.m, rtol=self.m_tol):
            self.opp_data.m = m
            self.opp_data.angles = self.lut_opp['switching_angles'].sel(
                modulation_index=m, method='nearest').values
            self.opp_data.positions = self.lut_opp['switch_positions'].sel(
                modulation_index=m, method='nearest').values

    def execute(self, sys, kTs):
        """
        Execute the OPP modulator to determine the switching angles and positions.

        Parameters
        ----------
        sys : system object
            The system model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        t_switch : 1 x MAX_COLS ndarray
            Switching time instants. The time instants are normalized to the sampling interval Ts.
        switch_array : 3 x MAX_COLS ndarray
            Switch positions.
        """

        # Maximum number of switching events in the output
        MAX_COLS = 5

        u_ref_abc = self.input.u_abc

        # Calculate the converter voltage angle
        u = abc_2_alpha_beta(u_ref_abc)
        u_ang = np.arctan2(u[1], u[0])

        # Update OPP to match the current modulation index
        self.update_opp(np.linalg.norm(u))

        # Retrieve the switch position
        t_switch, switch_pos = get_opp_switching_instants(
            self.opp_data.angles, self.opp_data.positions, u_ang, self.Ts,
            self.input.ws, sys)

        # Pad output to a fixed size
        n = len(t_switch)
        t_pad = np.inf * np.ones(MAX_COLS)
        U_pad = np.zeros([3, MAX_COLS])

        t_pad[:n] = t_switch[:n]
        U_pad[:, :n] = switch_pos[:, :n]

        self.output = SimpleNamespace(
            t_switch=t_pad / self.Ts,
            switch_pos=np.transpose(U_pad),
            u_abc=u_ref_abc,
        )

        return self.output
