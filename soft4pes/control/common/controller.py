from abc import ABC, abstractmethod
from types import SimpleNamespace


class ControllerBase(ABC):
    """
    Base class for controllers.
    """

    def __init__(self):
        self.data = SimpleNamespace()

    @abstractmethod
    def input(self, ref):
        """
        Get the reference signal for the controller.
        """

    @abstractmethod
    def execute(self, sys, conv, kTs):
        """
        Execute the controller.
        """

    @abstractmethod
    def output(self):
        """
        Get the output signal of the controller.
        """

    @abstractmethod
    def save_data(self, kTs):
        """
        Save controller data.
        """
