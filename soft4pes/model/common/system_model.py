"""
System base class
"""
from abc import ABC, abstractmethod
from types import SimpleNamespace
import numpy as np
from scipy.linalg import expm


class SystemModel(ABC):
    """
    System base class. The class implements some functionalities that are common for all system 
    models.

    Parameters
    ----------
    par : system parameters
        System parameters in p.u.
    base : base value object
        Base values.
    conv : converter object
        Converter object.

    Attributes
    ----------
    base : base value object
        Base values.
    data : SimpleNamespace
        Namespace for storing simulation data.
    par : system parameters
        System parameters in p.u.
    conv : converter object
        Converter object.
    x : ndarray
        Current state of the system.
    cont_state_space : SimpleNamespace
        The continuous-time state-space model of the system.
    """

    def __init__(self, par, base, conv):
        self.base = base
        self.data = SimpleNamespace(x=[], t=[], uk_abc=[])
        self.par = par
        self.conv = conv
        if not hasattr(self, 'x'):
            self.x = 0
        self.cont_state_space = self.get_continuous_state_space()

    @abstractmethod
    def get_continuous_state_space(self):
        """
        Calculates the continuous-time state-space model of the system.

        Returns
        -------
        SimpleNamespace
            The continuous-time state-space model of the system.
        """

    def get_discrete_state_space(self, Ts, method):
        """
        Get the discrete-time state-space model using the specified discretization method. Linear 
        system is assumed. 

        Parameters
        ----------
        Ts : float
            Sampling interval [s].
        method : str, optional
            Discretization method. Available options are 'forward_euler' or 'exact_discretization'.

        Returns
        -------
        SimpleNamespace
            Discrete-time state-space model.
        """

        cont_state_space = self.cont_state_space
        Ts_pu = Ts * self.base.w
        F_size = cont_state_space.F.shape[0]

        # Discretize the state-space model using the specified method
        # The continuous state-space model is dx/dt = Fx + Gu or dx/dt = Fx + G1u + G2d
        # Extract the matrices F, G, G1, G2 from the continuous state-space model, discretize
        # them and store them in a SimpleNamespace object. Rename the matrices to A, B, B1, and B2,
        # forming a discrete state-space model x[k+1] = Ax[k] + Bu[k] or
        # x[k+1] = Ax[k] + B1u[k] + B2d[k]
        if method == 'forward_euler':
            A = np.eye(F_size) + cont_state_space.F * Ts_pu
            B = {
                'B' + key[1:]: value * Ts_pu
                for key, value in cont_state_space.__dict__.items()
                if key.startswith('G')
            }
        elif method == 'exact_discretization':
            A = expm(cont_state_space.F * Ts_pu)
            try:
                F_inv = np.linalg.inv(cont_state_space.F)
            except np.linalg.LinAlgError as exc:
                raise ValueError("Matrix F is not invertible.") from exc
            B = {
                'B' + key[1:]:
                np.dot(-F_inv,
                       (np.eye(cont_state_space.F.shape[0]) - A)).dot(value)
                for key, value in cont_state_space.__dict__.items()
                if key.startswith('G')
            }
        else:
            raise ValueError(
                'Invalid discretization method. Available methods: forward_euler, '
                'exact_discretization')

        return SimpleNamespace(A=A, **B)

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
