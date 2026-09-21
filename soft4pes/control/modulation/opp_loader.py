"""
Outer control loop which loads and updates the optimized pulse pattern (OPP) data.

"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import FirstOrderFilter
from soft4pes.control.modulation.utils import load_switching_angles_from_file, update_opp


class OPPLoader(Controller):
    """
    The outer loop loads the OPP data from a file and selects the appropriate OPP 
    based on the modulation index. 
    The OPP is updated if the modulation index changes significantly.

    Parameters
    ----------
    sys : system object
        The system model.
    switching_frequency : float
        The desired switching frequency of the converter [Hz].
    m_tol : float (optional)
        Tolerance for the modulation index change to trigger an update of the OPP.

    Attributes
    ----------
    m : float
        Current modulation index.
    m_tol : float
        Tolerance for the modulation index change to trigger an update of the OPP.
    lut_opp : xarray.Dataset
        Dataset containing the OPP data for different modulation indices.
    opp_data : SimpleNamespace
        Namespace to store the OPPs for the current modulation index.

    """

    def __init__(self, sys, switching_frequency, m_tol=1e-2):
        super().__init__()
        self.sys = sys

        self.m = None
        self.m_tol = m_tol
        self.lut_opp = load_switching_angles_from_file(self.sys,
                                                       switching_frequency)
        self.ws_filter = None

        # Namespace to store the OPPs for the current modulation index
        self.opp_data = SimpleNamespace(m=None,
                                        angles=None,
                                        positions=None,
                                        harm_ref=None)

    def execute(self, sys, kTs):
        """
        Parameters
        ----------
        sys : system object
            The system model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        output : SimpleNamespace
            Namespace containing the OPP data for the current modulation index.
        """

        self.output = self.input

        if hasattr(sys, "ws"):
            # Initialize the first-order filter for the electrical angular frequency
            if self.ws_filter is None:
                self.ws_filter = FirstOrderFilter(0.1, 1, 1)

            # Filter the theoretical electrical angular frequency
            self.ws_filter.update(sys.ws, self.Ts, sys.base)

            ws = self.ws_filter.output
            self.output.ws = ws

            # Compute the modulation index
            m = 2 / sys.conv.v_dc * self.input.psiS_mag_ref * ws
        else:

            # Derive the converter voltage magnitude from the active and reactive power references
            v_conv_mag = np.sqrt((1 + (self.input.Q_ref *
                                       (sys.par.Xg + sys.par.X_fc)))**2 +
                                 (self.input.P_ref *
                                  (sys.par.Xg + sys.par.X_fc))**2)

            m = 2 / sys.conv.v_dc * v_conv_mag

        # If the modulation index change exceeds the tolerance, update the angles and positions.
        if self.m is None or not np.isclose(m, self.m, rtol=self.m_tol):
            self.m = m
            [angles, positions, harm_ref] = update_opp(self.lut_opp, self.m)

            self.opp_data.angles = angles
            self.opp_data.positions = positions
            self.opp_data.harm_ref = harm_ref

        self.output.angles = self.opp_data.angles
        self.output.positions = self.opp_data.positions
        self.output.harm_ref = self.opp_data.harm_ref

        return self.output
