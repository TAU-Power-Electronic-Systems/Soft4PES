"""
Grid current reference generator.
"""
from types import SimpleNamespace
import numpy as np
from soft4pes.control.common import Controller
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta


class GridCurrRefGen(Controller):
    """
    Grid current reference generator. This class generates the grid current reference based on the 
    active and reactive power references using grid voltage. The equations are in per unit. Grid 
    voltage orientation is assumed, i.e. vg_d is aligned with d-axis of the dq-reference frame. 
    Moreover, the positive grid current flows from the converter to the grid.
    """

    def execute(self, sys, kTs):
        """
        Generate the current reference.

        Parameters
        ----------
        sys : object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        output : SimpleNamespace
            The output of the controller, containing the grid current reference and the grid or PLL
            angle (theta).
        """

        vg = sys.get_grid_voltage(kTs)

        theta_vg = np.arctan2(vg[1], vg[0])

        vg_dq = alpha_beta_2_dq(vg, theta_vg)
        den = vg_dq[0]**2 + vg_dq[1]**2

        P_ref = self.input.P_ref
        Q_ref = self.input.Q_ref

        ig_ref_d = (P_ref * vg_dq[0] + Q_ref * vg_dq[1]) / den
        ig_ref_q = -(Q_ref * vg_dq[0] - P_ref * vg_dq[1]) / den

        ig_ref_dq = np.array([ig_ref_d, ig_ref_q])

        ig_ref = dq_2_alpha_beta(ig_ref_dq, theta_vg)

        if getattr(self.input, "theta", None) is None:
            theta_out = theta_vg
        else:
            theta_out = self.input.theta

        self.output = SimpleNamespace(ig_ref=ig_ref, theta=theta_out)

        return self.output
