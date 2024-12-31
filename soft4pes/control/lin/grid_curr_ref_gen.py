"""
Grid current reference generator.
"""

import numpy as np
from soft4pes.control.common import Controller
from soft4pes.utils import alpha_beta_2_dq


class GridCurrRefGen(Controller):
    """
    Grid current reference generator. This class generates the grid current reference based on the 
    active and reactive power references using grid voltage.
    """

    def execute(self, sys, conv, kTs):
        """
        Generate the current reference.

        Parameters
        ----------
        sys : object
            System model.
        conv : object
            Converter model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        output : SimpleNamespace
            The output of the controller, containing the current reference in dq frame.
        """

        vg = sys.get_grid_voltage(kTs)
        theta = np.arctan2(vg[1], vg[0])
        vg_dq = alpha_beta_2_dq(vg, theta)
        ig_ref_d = self.input.P_ref / vg_dq[0]
        ig_ref_q = -self.input.Q_ref / vg_dq[0]
        self.output.ig_ref_dq = np.array([ig_ref_d, ig_ref_q])

        return self.output
