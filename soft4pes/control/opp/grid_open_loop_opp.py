"""
Open-loop OPP implementation for grid following control.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common import Controller
from soft4pes.utils import alpha_beta_2_dq
from soft4pes.control.opp.utils import load_switching_angles, read_switching_angles


class GridOpenLoopOPP(Controller):
    """
    Open-loop optimized pulse pattern (OPP) implementation for grid following control.

    Parameters
    ----------
    sys : object
        System model.
    d : int
        Number of switching angles.
    
    Attributes
    ----------
    sys : object
        System model.
    wg : float
        Grid angular frequency [rad/s].
    m : float
        Curretn modulation index.
    angles : 1 x d ndarray
        Switching angles.
    positions : 1 x d ndarray
        Switching positions corresponding to the switching angles.
    lut : xarray Dataset
        Lookup table containing the switching angles and positions 
        for different modulation indices.
    d : int
        Number of switching angles.
    """

    def __init__(self, sys, d):
        super().__init__()
        self.sys = sys
        self.wg = 1
        self.d = d
        self.m = None
        self.angles = None
        self.positions = None
        self.lut = None

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
        self.lut = load_switching_angles(self.d, self.sys)

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
            switch position or modulating signal.
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
        v_conv_dq = (sys.par.R_fc + sys.par.Rg) * i_conv_ref_dq + self.wg * (
            sys.par.X_fc + sys.par.Xg) * np.array(
                [-i_conv_ref_dq[1], i_conv_ref_dq[0]]) + vg_dq

        # Modulation index
        m = 2 / sys.conv.v_dc * np.linalg.norm(v_conv_dq)

        # Read the switching angles and positions from the LUT
        # If the modulation index has changed significantly, update the angles and positions
        if self.m is None or not np.isclose(m, self.m, rtol=1e-3):
            self.m = m
            self.angles = self.lut['switching_angles'].sel(
                modulation_index=m, method='nearest').values
            self.positions = self.lut['switch_positions'].sel(
                modulation_index=m, method='nearest').values

        # Converter voltage angle
        v_conv_ang = theta + np.arctan2(v_conv_dq[1], v_conv_dq[0])

        # Retrieve the switching angles and the corresponding
        # switching times and three-phase switch positions
        t_nom, U, u0 = read_switching_angles(self.angles, self.positions,
                                             v_conv_ang, self.Ts, self.wg, sys)

        self.output = SimpleNamespace(t_switch=t_nom / self.Ts,
                                      switch_pos=np.transpose(U),
                                      u_abc=np.array([0, 0, 0]))

        return self.output
