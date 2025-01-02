"""
System base class
"""
from abc import ABC, abstractmethod
from types import SimpleNamespace


class SystemModel(ABC):
    """
    System base class. The class implements some functionalities that are common for all system 
    models.

    Attributes
    ----------
    base : base value object
        Base values.
    data : SimpleNamespace
        Namespace for storing simulation data.
    par : system parameters
        System parameters in p.u..
    x : ndarray
        Current state of the system.
    """

    def __init__(self, par, base):
        self.base = base
        self.data = SimpleNamespace(x=[], t=[], uk_abc=[])
        self.par = par
        self.x = 0

    @abstractmethod
    def get_discrete_state_space(self, v_dc, Ts):
        """
        Calculates the discrete-time state-space model of the system.

        Parameters
        ----------
        v_dc : float
            The converter dc-link voltage [p.u.].
        Ts : float
            Sampling interval [s].

        Returns
        -------
        SimpleNamespace
            The discrete-time state-space model of the system.
        """

    @abstractmethod
    def set_initial_state(self, **kwargs):
        """
        Calculate and set the initial state of the system.
        """

    @abstractmethod
    def get_next_state(self, matrices, uk_abc, kTs):
        """
        Calculate the next state of the system.

        Parameters
        ----------
        uk_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        matrices : SimpleNamespace
            A SimpleNamespace object containing the state-space model matrices.

        Returns
        -------
        ndarray
            The next state of the system.
        """

    @abstractmethod
    def get_measurements(self, kTs):
        """
        Get additional measurements of the system.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].
        """

    def update(self, matrices, uk_abc, kTs):
        """
        Update the system state and save data.

        Parameters
        ----------
        matrices : SimpleNamespace
            A SimpleNamespace object containing the state-space model matrices.
        uk_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        kTs : float
            Current discrete time instant [s].
        meas : SimpleNamespace, optional
            Measurement data.
        """

        meas = self.get_measurements(kTs)
        self.save_data(kTs, uk_abc, meas)
        self.x = self.get_next_state(matrices, uk_abc, kTs)

    def save_data(self, kTs, uk_abc, meas):
        """
        Save simulation data.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].
        uk_abc : 1 x 3 ndarray of floats 
            Converter three-phase switch position or modulating signal.
        meas : SimpleNamespace, optional
            Measurement data.
        """

        self.data.x.append(self.x)
        self.data.t.append(kTs)
        self.data.uk_abc.append(uk_abc)
        if meas is not None:
            for key, value in meas.__dict__.items():
                if not hasattr(self.data, key):
                    setattr(self.data, key, [])
                getattr(self.data, key).append(value)
