"""
Grid current controller for a converter with LCL filter based on weighted average control
 (WAC) feedback.

[Ref.]. L. S. Perić, E. Levi and S. N. Vukosavić, "Compound Feedback for Current-Controlled
 Grid-Side Inverters With LCL Filters," in IEEE Transactions on Power Electronics, vol. 40,
   no. 2, pp. 3005-3019, Feb. 2025, doi: 10.1109/TPEL.2024.3487109.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import get_modulating_signal, DiscreteTransferFunction


class LCLGridCurrCtrWACFB(Controller):
    """
    Grid current controller for a converter with LCL filter based on weighted average based (WAC) 
    feedback.

    Parameters
    ----------
    sys : object
        System model containing electrical parameters and base values.

    
    Attributes
    ----------
    sys : object
        System model containing electrical parameters and base values.
    gamma : float
        Tuning parameter for the high-pass filter (HPF) in the damping compensation path.
    xi : float
        Damping ratio for the damping compensation path.
    alpha_d : float
        Tuning parameter for the integrator gain in the main control path.
    ctr : SimpleNamespace
        Controller parameters and filters.
    """

    def __init__(self, sys, gamma=None, xi=None, alpha_d=0.3):
        super().__init__()
        self.sys = sys
        self.gamma = gamma
        self.xi = xi
        self.alpha_d = alpha_d
        self.ctr_imp = None

    def set_sampling_interval(self, Ts):
        """
        Set the sampling interval and compute controller parameters.

        Parameters
        ----------
        Ts : float
            Sampling interval in seconds.
        """
        self.Ts = float(Ts)
        Ts_pu = self.Ts * self.sys.base.w
        wr = np.sqrt((self.sys.par.X_fc + self.sys.par.X_fg) /
                     (self.sys.par.X_fc * self.sys.par.X_fg * self.sys.par.Xc))

        fr_over_fs = wr * Ts_pu / (2.0 * np.pi)
        # Set default values for gamma and xi based on the ratio of
        # the resonant frequency to the sampling frequency.
        if fr_over_fs > 1 / 12:
            if self.gamma is None:
                self.gamma = 5
            if self.xi is None:
                self.xi = 0.2
        else:
            if self.gamma is None:
                self.gamma = 1.25
            if self.xi is None:
                self.xi = 0.5

        # Eq.(35), W_C2(z) = 4*X_fg*Xc/Ts^2 * ((z-1)^2 / (z+1)^2) ->
        # W_C2(z) = (g - 2*g z^-1 + g z^-2) / (1 + 2 z^-1 + z^-2)
        g = 4.0 * self.sys.par.X_fg * self.sys.par.Xc / (Ts_pu * Ts_pu)
        W_C2 = DiscreteTransferFunction(numerator_coeffs=[g, -2.0 * g, g],
                                        denominator_coeffs=[1.0, 2.0, 1.0])

        # Eq.(19)
        L = 0.5 * (self.sys.par.X_fc + self.sys.par.X_fg)
        K = 2.0 * L * wr
        # Eq.(16), proportional and integral gains for damping compensator W_C(z)
        k1 = (2.0 * self.xi * K) / (wr * self.sys.par.X_fg * self.sys.par.Xc)
        sigma = K / (self.sys.par.X_fc + self.sys.par.X_fg)
        k2 = k1 / sigma
        # Eq.(33),W_C(z) = k1*Ts*z/(z-1) + k2  ->
        # W_C(z) = ((k1*Ts+k2) - k2 z^-1)/(1 - z^-1)
        W_C = DiscreteTransferFunction(numerator_coeffs=[k1 * Ts_pu + k2, -k2],
                                       denominator_coeffs=[1.0, -1.0])

        # tuning parameter for high-pass filter W_HP(z)
        tau = self.gamma / wr
        a = np.exp(-Ts_pu / tau)
        # Eq.(34), W_HP(z) = ((z-1)/(z-a))^2 ->
        # W_HP(z) = (1 - 2 z^-1 + z^-2) / (1 - 2 a z^-1 + a^2 z^-2)
        W_HP = DiscreteTransferFunction(
            numerator_coeffs=[1.0, -2.0, 1.0],
            denominator_coeffs=[1.0, -2.0 * a, a * a])

        # delay of the feedback acquisition in damping compensation path.
        # Eq.(25), W_D(z) = (1+2z+z^2)/(4z^2) ->
        # W_D(z) = (0.25 + 0.5 z^-1 + 0.25 z^-2)
        W_D_ui = DiscreteTransferFunction(numerator_coeffs=[0.25, 0.5, 0.25])

        # Eq. (36), W_Q(z) = Im(z) / (Ts^2 * (X_fc+X_fg) * (z+1)^2)
        # Im(z) = 4*X_fc*X_fg*Xc*(z-1)^2 + Ts^2*(X_fc+X_fg)*(z+1)^2
        # W_Q(z) = (b+c) - 2*(b-c) z^-1 + (b+c) z^-2 / (c + 2 c z^-1 + c z^-2)
        b = 4.0 * self.sys.par.X_fc * self.sys.par.X_fg * self.sys.par.Xc
        c = (Ts_pu * Ts_pu) * (self.sys.par.X_fc + self.sys.par.X_fg)
        W_Q = DiscreteTransferFunction(
            numerator_coeffs=[b + c, -2 * b + 2 * c, b + c],
            denominator_coeffs=[c, 2 * c, c])

        # delay of feedback acquisition in the WAC feedback path.
        # Eq.(25), W_D(z) = (1+2z+z^2)/(4z^2) ->
        # W_D(z) = (0.25 + 0.5 z^-1 + 0.25 z^-2)
        W_D_if = DiscreteTransferFunction(numerator_coeffs=[0.25, 0.5, 0.25])

        # dimensionless differential gain of the series lead compensator WDIF(z).
        # It sets the amount of lead action added to the main current controller.
        # Increasing d improves the phase characteristic, increases damping,
        # and usually reduces overshoot while increasing closed-loop bandwidth.
        # The papers treat d as a relative tuning parameter, independent of the
        # plant parameters. With improved scheduling, a practical value is d = 0.444.
        # In general, d is beneficial up to about 0.6; for larger values,
        # robustness (vector margin) starts to decrease.
        d = 0.444
        # WDIF(z): series differential lead compensator proposed in [17] and [27] of the [Ref.].
        # WDIF(z) = 1 + d*(1 - z^-1) = (1 + d) - d*z^-1
        W_DIF = DiscreteTransferFunction(numerator_coeffs=[1.0 + d, -d])

        # Main controller based on Eq. (5.11) of [27] in the [Ref.].
        X_eq = ((self.sys.par.X_fc * self.sys.par.X_fg) /
                (self.sys.par.X_fc + self.sys.par.X_fg))
        R_eq = self.sys.par.R_fc + self.sys.par.R_fg
        beta = R_eq * Ts_pu / X_eq
        e = self.alpha_d * X_eq / Ts_pu
        W_REG = DiscreteTransferFunction(
            numerator_coeffs=[e, -e * np.exp(-beta)],
            denominator_coeffs=[1.0, -1.0])

        self.ctr_imp = SimpleNamespace(Ts_pu=Ts_pu,
                                       wr=wr,
                                       W_C2=W_C2,
                                       W_C=W_C,
                                       W_HP=W_HP,
                                       W_D_ui=W_D_ui,
                                       W_Q=W_Q,
                                       W_D_if=W_D_if,
                                       W_DIF=W_DIF,
                                       W_REG=W_REG)

    def execute(self, sys, kTs):

        vg_ab = sys.get_grid_voltage(kTs)
        theta = np.arctan2(vg_ab[1], vg_ab[0])

        # Get the grid current reference
        ig_ref_dq = self.input.ig_ref_dq
        ig_dq = alpha_beta_2_dq(sys.ig, theta)

        # WAC feedback: iF_dq = W_D_if * W_Q * ig_dq
        iF_dq = self.ctr_imp.W_D_if.apply(self.ctr_imp.W_Q.apply(ig_dq))

        # damping path: u_comp = W_D_ui * W_HP * W_C * W_C2 * ig_dq
        iC_dq = self.ctr_imp.W_C2.apply(ig_dq)
        uCP1_dq = self.ctr_imp.W_C.apply(iC_dq)
        uCP_dq = self.ctr_imp.W_HP.apply(uCP1_dq)
        u_comp_dq = self.ctr_imp.W_D_ui.apply(uCP_dq)

        # main control path: u_reg_dq = W_REG * W_DIF * e_dq
        e_dq = ig_ref_dq - iF_dq
        u_reg_dq = self.ctr_imp.W_REG.apply(self.ctr_imp.W_DIF.apply(e_dq))

        # final control signal: u_dq = u_reg_dq - u_comp_dq
        ui_dq = u_reg_dq - u_comp_dq

        u_abc = get_modulating_signal(dq_2_alpha_beta(ui_dq, theta),
                                      sys.conv.v_dc)
        self.output = SimpleNamespace(u_abc=u_abc)
        return self.output
