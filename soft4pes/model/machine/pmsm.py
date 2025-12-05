"""
Permanent magnet synchronous machine (PMSM) model. The machine operates at a constant electrical 
angular rotor speed. 
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.model.common.system_model import SystemModel
from soft4pes.utils.conversions import alpha_beta_2_dq, dq_2_alpha_beta


class PMSM(SystemModel):
    """
    Permanent magnet synchronous machine (PMSM) model. The model operates at a constant electrical
    angular rotor speed. The system is modelled in a alpha-beta frame. The state of the system is 
    the stator current and rotor flux, i.e. [iS_alpha, iS_beta, psiR_alpha, psiR_beta]^T. The 
    system input is the converter three-phase switch position or modulating signal. The initial 
    state of the model is based on the torque reference and the electrical angle, set to -pi/2 rad
    at t = 0 s.

    Note that although the rotor flux appears as a state of the system, it is generated using the 
    electrical angle and the permanent magnet flux linkage at the state update. This approach avoids 
    numerical integration errors that would accumulate when using Forward Euler discretization for 
    the rotor flux dynamics, since the rotor flux magnitude is constant and only rotates with the 
    electrical angle. The full state-space model is still used in the MPC state predictions.

    Parameters
    ----------
    par : PMSMParameters
        Permanent magnet synchronous machine parameters in p.u.
    conv : converter object
        Converter object.
    base : base value object
        Base values.
    T_ref_init : float
        Initial torque reference [p.u.].
    mtpa_lut : MTPALookupTable
        MTPA lookup table for optimal current calculation.

    Attributes
    ----------
    data : SimpleNamespace
        Namespace for storing simulation data.
    par : PMSMParameters
        Permanent magnet synchronous machine parameters in p.u.
    conv : converter object
        Converter object.
    base : base value object
        Base values.
    x : 1 x 4 ndarray of floats
        Current state of the machine [p.u.].
    cont_state_space : SimpleNamespace
        The continuous-time state-space model of the system.
    state_map : dict
        A dictionary mapping state names to elements of the state vector.
    time_varying_model : bool
        Indicates if the system model is time-varying.
    theta_el : float
        Electrical angle of the machine [rad].
    """

    def __init__(self, par, conv, base, T_ref_init, mtpa_lut):
        x_size = 4
        state_map = {
            'iS': slice(0, 2),  # Stator current (x[0:2])
            'psiR': slice(2, 4),  # Rotor flux linkage (x[2:4])
        }
        self.theta_el = -np.pi / 2

        super().__init__(par=par,
                         conv=conv,
                         base=base,
                         x_size=x_size,
                         state_map=state_map)
        self.time_varying_model = True

        self.set_initial_state(T_ref_init=T_ref_init, mtpa_lut=mtpa_lut)

    def set_initial_state(self, **kwargs):
        """
        Calculate the initial state of the machine based on the torque reference.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments containing:
            - T_ref_init : float
                The initial torque reference [p.u.].
            - mtpa_lut : MTPALookupTable
                MTPA lookup table for optimal current calculation.
        """

        T_ref_init = kwargs.get('T_ref_init')
        mtpa_lut = kwargs.get('mtpa_lut')

        # Get the initial stator current from MTPA
        iS_dq = mtpa_lut.get_optimal_current(T_ref_init)
        iS = dq_2_alpha_beta(iS_dq, self.theta_el)
        psiR = self.psiR
        self.x = np.concatenate((iS, psiR))

    def get_stator_current_ref_dq(self, T_ref):
        """
        Get the optimal steady-state stator current using MTPA.

        Parameters
        ----------
        T_ref : float
            The torque reference [p.u.].

        Returns
        -------
        ndarray
            The optimal stator current in the dq frame [p.u.].
        """
        return self.mtpa.get_optimal_current(T_ref)

    def get_continuous_state_space(self):
        """
        Calculate the continuous-time state-space model of the system.

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing matrices F and G of the continuous-time state-space 
            model.
        """

        ws = self.par.ws
        Rs = self.par.Rs
        Xsd = self.par.Xsd
        Xsq = self.par.Xsq

        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

        Xs = (Xsd + Xsq) / 2
        delta_X = Xsd - Xsq
        X_theta = np.array([[Xs + delta_X * np.cos(2 * self.theta_el) / 2, \
                             delta_X * np.sin(2 * self.theta_el) / 2],
                            [delta_X * np.sin(2 * self.theta_el) / 2, \
                             Xs - delta_X * np.cos(2 * self.theta_el) / 2]])
        J = np.array([[0, -1], [1, 0]])

        R = np.array([[-np.sin(2 * self.theta_el),
                       np.cos(2 * self.theta_el)],
                      [np.cos(2 * self.theta_el),
                       np.sin(2 * self.theta_el)]])

        X_theta_inv = np.linalg.inv(X_theta)

        F11 = -X_theta_inv.dot(Rs * np.eye(2) + ws * delta_X * R)
        F12 = -ws * X_theta_inv.dot(J)
        F21 = np.zeros((2, 2))
        F22 = ws * J
        F = np.block([[F11, F12], [F21, F22]])

        G = self.conv.v_dc / 2 * np.vstack(
            [np.eye(2), np.zeros((2, 2))]).dot(X_theta_inv).dot(K)

        return SimpleNamespace(F=F, G=G)

    @property
    def Te(self):
        iS_dq = alpha_beta_2_dq(self.iS, self.theta_el)
        return ((self.par.Xsd - self.par.Xsq) * iS_dq[0] +
                self.par.PsiPM) * iS_dq[1]

    @property
    def psiR(self):
        return np.array([np.cos(self.theta_el),
                         np.sin(self.theta_el)]) * self.par.PsiPM

    def get_next_state(self, matrices, u_abc, kTs, Ts):
        """
        Calculate the next state of the system.

        Parameters
        ----------
        matrices : SimpleNamespace
            A SimpleNamespace object containing the state-space model matrices A and B.
        u_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal [p.u.].
        kTs : float
            Current discrete time instant [s].
        Ts : float
            Sampling interval [s].

        Returns
        -------
        1 x 4 ndarray of floats
            The next state of the system.
        """

        # Get the next state
        x = np.concatenate((self.iS, self.psiR))
        x_kp1 = np.dot(matrices.A, x) + np.dot(matrices.B, u_abc)

        # Update electrical angle
        self.theta_el += self.par.ws * Ts * self.base.w

        return x_kp1

    def get_measurements(self, kTs):
        """
        Get the measurement data of the system.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing the machine electromagnetic torque Te [p.u.].
        """

        return SimpleNamespace(Te=self.Te)
