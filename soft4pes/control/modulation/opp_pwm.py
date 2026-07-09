"""
Optimized pulse pattern (OPP) modulator 
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.modulation.utils import read_switching_angles, load_switching_angles
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
    opp_data : SimpleNamespace
        Contains the OPP data including the modulation index tolerance, 
        current modulation index, switching angles, switching positions, 
        and the loaded OPP data.
    """

    def __init__(self, sys, opp_file, m_tol=1e-3):
        super().__init__()
        self.sys = sys

        # Additional attributes for the OPP
        self.opp_data = SimpleNamespace(file=opp_file,
                                        m_tol=m_tol,
                                        m=None,
                                        angles=None,
                                        positions=None,
                                        lut_opp=None)

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

        # Update OPP
        self.update_opp(np.linalg.norm(u))

        # retrieve the switch position
        t_switch, switch_pos, u0 = read_switching_angles(
            self.opp_data.angles, self.opp_data.positions, u_ang, self.Ts,
            self.input.w, sys)

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
