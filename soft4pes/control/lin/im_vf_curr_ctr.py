"""
Open-loop V/f control for an induction machine (IM)
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common import Controller
from soft4pes.utils import dq_2_alpha_beta
from soft4pes.control.common.utils import get_modulating_signal


class VfCurrCtr(Controller):
    """
    Open-loop V/f control for an induction machine (IM). The controller calculates the required 
    stator voltage based on the torque reference and stator flux magnitude reference in an open-loop
    manner. The stator voltage is aligned considering the rotor flux angle to facilitate fixed rotor
    speed.

    Parameters
    ----------
    sys : object
        System model.
        
    Attributes
    ----------
    sys : object
        System model.
    v0 : float
        Approximated stator voltage magnitude at zero frequency.

    """

    def __init__(self, sys):
        super().__init__()
        self.sys = sys
        self.v0 = self.sys.par.Rs * np.linalg.norm(self.sys.iS)

    def execute(self, sys, kTs):
        """
        Execute the open loop V/f controller

        Parameters
        ----------
        sys : object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        output : SimpleNamespace
            Output from the controller including the modulation signal and the stator electrical 
            frequency.
        """

        # Derive the slip frequncy reference from the torque reference and stator flux magnitude
        # reference
        w_sl = (self.input.T_ref / self.input.psiS_mag_ref**2 / sys.par.kT *
                sys.par.Rr * sys.par.Xs**2 / sys.par.Xm**2)

        # Stator electrical frequency
        ws = sys.wr + w_sl

        # Calculate required stator voltage
        if ws < 1:
            v_conv_mag = ws * (1 - self.v0) + self.v0
        else:
            v_conv_mag = 1

        # Calculate rotor flux magnitude reference
        psiR_steady_state = sys.calculate_steady_state_rotor_flux(
            self.input.psiS_mag_ref, self.input.T_ref)

        # Rotor  flux magnitude reference
        psiR_mag_ref = np.linalg.norm(psiR_steady_state)

        # Calculate load angle
        gamma = np.arcsin(sys.par.D / sys.par.Xm * self.input.T_ref /
                          self.input.psiS_mag_ref / psiR_mag_ref / sys.par.kT)

        # Calculate the rotor flux angle
        theta = np.arctan2(sys.psiR[1], sys.psiR[0])

        # Align the converter voltage vector
        v_conv = dq_2_alpha_beta(np.array([v_conv_mag, 0]),
                                 theta + gamma + np.pi / 2)

        u_abc = get_modulating_signal(v_conv, sys.conv.v_dc)

        self.output = SimpleNamespace(u_abc=u_abc, ws=ws)

        return self.output
