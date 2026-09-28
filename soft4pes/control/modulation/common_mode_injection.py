"""
Common-mode injection for modulating signal.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.common.controller import Controller


class CommonModeInjection(Controller):
    """
    Common-mode injection for modulating signal. The selected common-mode injection method
    computes a common-mode voltage component that is added to the three-phase modulating signal.
    Common-mode injection is applicable for carrier-based PWM schemes and for modulating-signal
    feedforward.

    Available common-mode injection methods:
    - MinMax: Adds a common-mode component u_cm = -0.5 * (max(u_ref_abc) + min(u_ref_abc)) to the 
      modulating signal. For a two level converter, this method is equivalent to space-vector 
      modulation (SVM). The maximum amplitude of the three-phase modulating signal before the
    common-mode injection is u_abc_ref_max = 2/sqrt(3) = 1.1547.

    Parameters
    ----------
    mode : str, optional
        Common-mode injection method. Default is 'MinMax', which is the only available method.

    Attributes
    ----------
    mode : str
        Common-mode injection method.
    u_abc_ref_max : float
        Maximum value of the three-phase modulating signal before common-mode injection.
    """

    def __init__(self, mode='MinMax'):
        super().__init__()
        self.mode = mode

        if self.mode == 'MinMax':
            self.u_abc_ref_max = 2 / np.sqrt(3)
        else:
            self.u_abc_ref_max = 1

    def execute(self, sys, kTs):
        """
        Apply common-mode injection.

        Parameters
        ----------
        sys : system object
            The system model (not used).
        kTs : float
            Current discrete time instant [s] (not used).

        Returns
        -------
        u_ref_abc_cm : 3 x 1 ndarray
            Three-phase modulating signal with common-mode injection.
        """

        u_ref_abc = self.input.u_abc

        if self.mode == 'MinMax':
            u_max = np.max(u_ref_abc)
            u_min = np.min(u_ref_abc)
            u_cm = -0.5 * (u_max + u_min)
        else:
            raise ValueError(
                f'Common mode injection mode {self.mode} not recognized. Available '
                'modes: MinMax.')

        self.output = SimpleNamespace(u_abc=u_ref_abc + u_cm)

        return self.output
