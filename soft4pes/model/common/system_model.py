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
    x_size : int
        Length of the state vector.
    state_map : dict
        A dictionary mapping states to elements of the state vector.

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
    state_map : dict
        A dictionary mapping states to elements of the state vector.
    time_varying_model : bool
        Indicates if the system model is time-varying.
    cont_state_space : SimpleNamespace
        The continuous-time state-space model of the system.
    u_abc_k : 1 x 3 ndarray of floats
        Converter three-phase switch position or modulating signal at the current time step.
    Ts_k : float
        Sampling interval at the current time step.
    xkm1 : ndarray
        State vector at the previous time step.
    """

    def __init__(self, par, base, conv, x_size, state_map):
        """
        Initialize the system model.

        Parameters
        ----------
        par : system parameters
            System parameters in p.u.
        base : base value object
            Base values.
        conv : converter object
            Converter object.
        x_size : int
            Length of the state vector.
        state_map : dict
            A dictionary mapping states to elements of the state vector.        
        """
        self.base = base
        self.data = SimpleNamespace(x=[], t=[], u_abc=[])
        self.par = par
        self.conv = conv
        if not hasattr(self, 'x'):
            self.x = np.zeros(x_size)
        self.state_map = state_map
        self.time_varying_model = False
        self.cont_state_space = self.get_continuous_time_state_space()
        self.u_abc_k = np.zeros(3)
        self.x_km1 = np.zeros(x_size)
        self.Ts_k = 0

    def __getattr__(self, name):
        """
        Dynamically retrieve elements of the state vector based on the state map.

        Parameters
        ----------
        name : str
            The name of the state to retrieve.

        Returns
        -------
        ndarray
            The corresponding entries in the state vector.
        """
        if 'state_map' in self.__dict__ and name in self.state_map:
            return self.x[self.state_map[name]]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @abstractmethod
    def get_continuous_time_state_space(self):
        """
        Calculates the continuous-time state-space model of the system.

        Returns
        -------
        SimpleNamespace
            The continuous-time state-space model of the system.
        """

    def get_discrete_time_state_space(self, Ts, method):
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
        Ts_pu = Ts*self.base.w
        F_size = cont_state_space.F.shape[0]

        # Discretize the continuous-time state-space model using the specified method.
        # Continuous-time model: dx(t)/dt = F x(t) + G u(t) (+ P d(t))
        # Discrete-time model:   x[k+1] = A x[k] + B u[k] (+ D d[k])
        # Extract the matrices F, G, and optional P from the continuous-time state-space model,
        # discretize them and store them in a SimpleNamespace object. Rename the matrices
        # to A, B, and optional D, forming a discrete-time state-space model.
        if method == 'forward_euler':
            A = np.eye(F_size) + cont_state_space.F*Ts_pu
            B = cont_state_space.G*Ts_pu
            D = cont_state_space.P*Ts_pu if hasattr(
                cont_state_space, 'P') else None
        elif method == 'exact_discretization':
            A = expm(cont_state_space.F*Ts_pu)
            try:
                F_inv = np.linalg.inv(cont_state_space.F)
            except np.linalg.LinAlgError as exc:
                raise ValueError("Matrix F is not invertible.") from exc
            common_term = np.dot(
                -F_inv, (np.eye(cont_state_space.F.shape[0]) - A))
            B = common_term.dot(cont_state_space.G)
            D = common_term.dot(cont_state_space.P) if hasattr(
                cont_state_space, 'P') else None
        else:
            raise ValueError(
                'Invalid discretization method. Available methods: forward_euler, '
                'exact_discretization')

        if D is None:
            return SimpleNamespace(A=A, B=B)
        return SimpleNamespace(A=A, B=B, D=D)

    @abstractmethod
    def set_initial_state(self, **kwargs):
        """
        Calculate and set the initial state of the system.
        """

    @abstractmethod
    def get_next_state(self, matrices, u_abc, kTs, Ts):
        """
        Calculate the next state of the system.

        Parameters
        ----------
        u_abc : 1 x 3 ndarray of floats
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
        u_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        kTs : float
            Current discrete time instant [s].
        """

    def update_state(self, matrices, u_abc, kTs, Ts):
        """
        Update the system state and save data.

        Parameters
        ----------
        matrices : SimpleNamespace
            A SimpleNamespace object containing the state-space model matrices.
        u_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        kTs : float
            Current discrete time instant [s].
        Ts : float
            Sampling interval at the current time step.
        """
        self.u_abc_k = u_abc
        self.Ts_k = Ts
        meas = self.get_measurements(kTs)
        self.save_data(kTs, u_abc, meas)
        self.x_km1 = self.x
        self.x = self.get_next_state(matrices, u_abc, kTs, Ts)

    def save_data(self, kTs, u_abc, meas):
        """
        Save simulation data.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].
        u_abc : 1 x 3 ndarray of floats 
            Converter three-phase switch position or modulating signal.
        meas : SimpleNamespace, optional
            Measurement data.
        """

        self.data.x.append(self.x)
        self.data.t.append(kTs)
        self.data.u_abc.append(u_abc)
        if meas is not None:
            for key, value in meas.__dict__.items():
                if not hasattr(self.data, key):
                    setattr(self.data, key, [])
                getattr(self.data, key).append(value)
