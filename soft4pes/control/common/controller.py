"""
Base class for controllers.
"""

from abc import ABC, abstractmethod
from types import SimpleNamespace


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
    """

    def __init__(self):
        self.data = SimpleNamespace(
            input=SimpleNamespace(),
            output=SimpleNamespace(),
        )
        self.input = SimpleNamespace()
        self.output = SimpleNamespace()
        self.Ts = 0

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

    @abstractmethod
    def execute(self, sys, conv, kTs):
        """
        Execute the controller.

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
