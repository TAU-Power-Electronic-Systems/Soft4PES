"Stator current reference generator for the induction machine"

from types import SimpleNamespace

import numpy as np
from soft4pes.control.common import Controller


class IMStatorCurrRefGen(Controller):
    """
    Stator current reference generator for the induction machine. This class generates the stator
    current reference based on the stator flux magnitude and torque references.
    """

    def execute(self, sys, kTs):
        """
        Generate the stator current reference.

        Parameters
        ----------
        sys : object
            System model.

        Returns
        -------
        output : SimpleNamespace
            The output of the controller, containing the stator current reference.
        """

        T_ref = self.input.T_ref
        psiS_mag_ref = self.input.psiS_mag_ref

        psiR_steady_state = sys.calculate_steady_state_rotor_flux(
            psiS_mag_ref, T_ref)
        iS_ref_steady_state = sys.calc_steady_state_stator_current(
            psiR_steady_state, T_ref)

        # Rotate the reference to match the current rotor flux orientation
        theta_ref = np.arctan2(psiR_steady_state[1], psiR_steady_state[0])
        theta_real = np.arctan2(sys.psiR[1], sys.psiR[0])
        theta = theta_real - theta_ref
        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])
        iS_ref = np.dot(R, iS_ref_steady_state)

        self.output = SimpleNamespace(iS_ref=iS_ref)
        return self.output
