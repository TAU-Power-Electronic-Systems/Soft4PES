"""
Base class for controllers.
"""

from abc import ABC, abstractmethod
from types import SimpleNamespace
import numpy as np
from soft4pes.utils import alpha_beta_2_abc


class Controller(ABC):
    """
    Base class for controllers.

    Attributes
    ----------
    data : SimpleNamespace
        Data storage for the controller, containing input and output namespaces.
    input : SimpleNamespace
        Namespace for storing input data.
    output : SimpleNamespace
        Namespace for storing output data.
    Ts : float
        Sampling interval [s].
    common_mode_inj_enabled : bool
        Whether common-mode injection is used in the control system.
    """

    def __init__(self):
        self.data = SimpleNamespace(
            input=SimpleNamespace(),
            output=SimpleNamespace(),
        )
        self.input = SimpleNamespace()
        self.output = SimpleNamespace()
        self.Ts = 0
        self.common_mode_inj_enabled = False

    def set_sampling_interval(self, Ts):
        """
        Set the sampling interval. 
        
        This method can be extended to set and/or calculate additional parameters.

        Parameters
        ----------
        Ts : float
            Sampling interval [s].
        """
        self.Ts = Ts

    def make_modulating_signal(self, v_ref, v_dc):
        """
        Convert a voltage reference to a modulating signal.

        The modulating signal is limited to the range [-1, 1] when common-mode injection is not
        used, and to the range [-2/sqrt(3), 2/sqrt(3)] when common-mode injection is used.

        Parameters
        ----------
        v_ref : ndarray
            The reference voltage.
        v_dc : float
            The dc-link voltage.

        Returns
        -------
        ndarray
            The modulating signal in abc-frame.
        """

        limit = 1 if not self.common_mode_inj_enabled else 2 / np.sqrt(3)
        return np.clip(alpha_beta_2_abc(v_ref / (v_dc / 2)), -limit, limit)

    @abstractmethod
    def execute(self, sys, kTs):
        """
        Execute the controller.

        Parameters
        ----------
        sys : object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        output : SimpleNamespace
            The output of the controller after execution.
        """

    def save_data(self):
        """
        Save controller data.

        The method saves the current input and output data to the data storage.
        """
        for key, value in self.input.__dict__.items():
            if not hasattr(self.data.input, key):
                setattr(self.data.input, key, [])
            getattr(self.data.input, key).append(value)

        for key, value in self.output.__dict__.items():
            if not hasattr(self.data.output, key):
                setattr(self.data.output, key, [])
            getattr(self.data.output, key).append(value)
