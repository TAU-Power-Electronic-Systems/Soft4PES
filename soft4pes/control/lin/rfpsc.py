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
from soft4pes.model.grid import RLGridLCLFilter
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta
from soft4pes.control.common.utils import wrap_theta, get_modulating_signal, FirstOrderFilter


class RFPSC(Controller):
    """
    Reference-feedforward power synchronization control (RFPSC).

    Parameters
    ----------
    sys : system object
        System model.
    Ra : float, optional
        Virtual damping resistance [p.u.].
    Kp : float, optional
        Proportional gain of the active power droop control [p.u.]. If not provided, it is 
        calculated based on the nominal frequency, nominal grid peak voltage and the virtual
        damping resistance.
    w_bw : float, optional
        Current filter bandwidth [p.u.].

    Attributes
    ----------
    Ra : float
        Virtual damping resistance [p.u.].
    theta_c : float
        The angle of the synchronous reference frame set by the droop control. The initial angle
        is set to -pi/2 to align the q-axis with the grid voltage. 
    ig_filter : FirstOrderFilter
        First-order filter for the current.
    Kp : float
        Proportional gain of the active power droop control [p.u.].
    """

    def __init__(self, sys, Ra=0.2, Kp=None, w_bw=0.1):
        super().__init__()
        self.Ra = Ra
        self.theta_c = -np.pi / 2
        self.ig_filter = FirstOrderFilter(w_bw=w_bw, size=2)

        if Kp is not None:
            self.Kp = Kp
        else:
            # If Kp is not provided, calculate it based on the nominal frequency, nominal grid peak
            # voltage and the virtual damping resistance according to the reference
            Vg = np.sqrt(2 / 3) * sys.par.Vg
            self.Kp = sys.par.wg * self.Ra / Vg

    def execute(self, sys, kTs):
        """
        Execute the RFPSC control algorithm.

        Parameters
        ----------
        sys : system object
            The system model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing the modulating signal for the converter (uk_abc) and
            a capacitor voltage reference in case LC(L) filter is used (vc_ref).
        """

        V_ref = self.input.V_ref
        P_ref = self.input.P_ref

        vg = sys.get_grid_voltage(kTs)
        if isinstance(sys, RLGridLCLFilter):
            ig = sys.x[2:4]
        else:
            ig = sys.x

        ig_dq = alpha_beta_2_dq(ig, self.theta_c)
        P = np.dot(vg, ig)

        # Droop control
        wc = sys.par.wg + self.Kp * (P_ref - P)

        # Calculate the reference current in dq-frame
        ig_ref_d = P_ref / V_ref
        ig_ref_q = self.ig_filter.output[1]
        ig_ref_dq = np.array([ig_ref_d, ig_ref_q])

        # Calculate the reference voltage
        v_ref_dq = V_ref * np.array([1, 0]) + self.Ra * (ig_ref_dq - ig_dq)
        v_ref = dq_2_alpha_beta(v_ref_dq, self.theta_c)

        # Calculate the dq-frame reference with a frame that is aligned with the grid voltage
        theta = np.arctan2(vg[1], vg[0])
        v_ref_dq = alpha_beta_2_dq(v_ref, theta)

        self.output = SimpleNamespace(
            uk_abc=get_modulating_signal(v_ref, sys.conv.v_dc),
            vc_ref_dq=v_ref_dq,
        )

        self.ig_filter.update(ig_dq, self.Ts, sys.base)
        self.theta_c += wc * self.Ts * sys.base.w
        self.theta_c = wrap_theta(self.theta_c)

        return self.output
