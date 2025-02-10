"""
Reference-feedforward power synchronization control (RFPSC). 

Reference: 
L. Harnefors, F. M. M. Rahman, M. Hinkkanen, and M. Routimo, “Reference-feedforward 
power-synchronization control,” IEEE Trans. Power Electron., vol. 35, no. 9, pp. 8878-8881, Sep. 
2020.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta
from soft4pes.control.common.utils import wrap_theta, get_modulating_signal, FirstOrderFilter


class RFPSC(Controller):
    """
    Reference-feedforward power synchronization control (RFPSC).

    Parameters
    ----------
    Ra : float, optional
        Virtual damping resistance [p.u.].
    wb : float, optional
        Current filter bandwidth [p.u.].

    Attributes
    ----------
    Ra : float
        Virtual damping resistance [p.u.].
    theta_c : float
        Initial angle of the synchronous reference frame.
    ig_filter : FirstOrderFilter
        First-order filter for the current.
    """

    def __init__(self, Ra=0.2, wb=0.1):
        super().__init__()
        self.Ra = Ra
        self.theta_c = -np.pi / 2
        self.ig_filter = FirstOrderFilter(wb=wb, size=2)

    def execute(self, sys, conv, kTs):
        """
        Execute the RFPSC control algorithm.

        Parameters
        ----------
        sys : system object
            The system model.
        conv : converter object
            The converter model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing the modulating signal (uk_abc).
        """

        V_ref = self.input.V_ref
        P_ref = self.input.P_ref

        vg = sys.get_grid_voltage(kTs)
        ig = sys.x
        ig_dq = alpha_beta_2_dq(ig, self.theta_c)
        P = np.dot(vg, ig)

        # Droop control
        wc = 1 + 0.2 * (P_ref - P)

        # Calculate the reference current in dq-frame
        ig_ref_d = P_ref / V_ref
        ig_ref_q = self.ig_filter.output[1]
        ig_ref_dq = np.array([ig_ref_d, ig_ref_q])

        # Calculate the reference voltage
        v_ref_dq = V_ref * np.array([1, 0]) + self.Ra * (ig_ref_dq - ig_dq)
        v_ref = dq_2_alpha_beta(v_ref_dq, self.theta_c)

        self.output = SimpleNamespace(
            uk_abc=get_modulating_signal(v_ref, conv.v_dc))

        self.ig_filter.update(ig_dq, self.Ts, sys.base)
        self.theta_c += wc * self.Ts * sys.base.w
        self.theta_c = wrap_theta(self.theta_c)

        return self.output
