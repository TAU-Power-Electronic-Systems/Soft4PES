"""
Induction machine model. The machine operates at a constant (rated) electrical angular rotor speed.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import dq_2_alpha_beta
from soft4pes.model.common.system_model import SystemModel


class InductionMachine(SystemModel):
    """
    Induction machine model operating at a constant (rated) electrical angular rotor speed.
    The state of the system is the stator current and rotor flux in the alpha-beta frame, i.e., 
    [iS_alpha, iS_beta, psiR_alpha, psiR_beta]^T. The system input is the converter three-phase 
    switch position or modulating signal. The initial state of the system is based on the stator 
    flux magnitude reference and torque reference.

    Parameters
    ----------
    par : InductionMachineParameters
        Induction machine parameters in p.u.
    conv : converter object
        Converter object.
    base : base value object
        Base values.
    psiS_mag_ref_init : float
        Initial stator flux magnitude reference [p.u.].
    T_ref_init : float
        Initial torque reference [p.u.].

    Attributes
    ----------
    data : SimpleNamespace
        Namespace for storing simulation data.
    par : InductionMachineParameters
        Induction machine parameters in p.u.
    conv : converter object
        Converter object.
    base : base value object
        Base values.
    x : 1 x 4 ndarray of floats
        Current state of the machine [p.u.].
    psiS_mag_ref : float
        Stator flux magnitude reference [p.u.].
    cont_state_space : SimpleNamespace
        The continuous-time state-space model of the system.
    state_map : dict
        A dictionary mapping states to elements of the state vector.
    """

    def __init__(self, par, conv, base, psiS_mag_ref_init, T_ref_init):
        self.par = par
        self.set_initial_state(psiS_mag_ref_init=psiS_mag_ref_init,
                               T_ref_init=T_ref_init)
        x_size = 4
        state_map = {
            'iS': slice(0, 2),  # Stator current (x[0:2])
            'psiR': slice(2, 4),  # Rotor flux (x[2:4])
        }
        super().__init__(par=par,
                         conv=conv,
                         base=base,
                         x_size=x_size,
                         state_map=state_map)
        self.time_varying_model = True

    def set_initial_state(self, **kwargs):
        """
        Calculates the initial state of the machine based on the initial stator flux magnitude 
        reference and torque reference.

        Parameters
        ----------
        psiS_mag_ref : float
            Initial stator flux magnitude reference [p.u.].
        T_ref_init : float
            Initial torque reference [p.u.].
        """

        psiS_mag_ref = kwargs.get('psiS_mag_ref_init')
        T_ref_init = kwargs.get('T_ref_init')

        psiR = self.calculate_steady_state_rotor_flux(psiS_mag_ref)
        iS = self.calc_steady_state_stator_current(psiR, T_ref_init)

        self.x = np.concatenate((iS, psiR))

    def calculate_steady_state_rotor_flux(self, psiS_mag_ref):
        D = self.par.D
        kT = self.par.kT
        Xm = self.par.Xm
        Xs = self.par.Xs
        Rr = self.par.Rr

        # Assume stator flux orientation, i.e., psiS is aligned with the d-axis
        psiS_d = psiS_mag_ref

        # Rotor flux in dq-frame
        psiR_q = -D / (Xm * kT) * psiS_d
        A = Rr * Xm / D
        B = Rr * Xs / D
        a = -B
        b = A * psiS_d
        c = -B * psiR_q**2

        psiR_d = (-b - np.sqrt(b**2 - 4 * a * c)) / (2 * a)

        # Convert the rotor flux from dq-frame to alpha-beta frame using the stator flux angle
        # (0 rad)
        psiR = dq_2_alpha_beta(np.array([psiR_d, psiR_q]), 0)

        return psiR

    def calc_steady_state_stator_current(self, psiR, T_ref):
        """
        Calculate the steady-state stator current.

        Parameters
        ----------
        psiR : 1 x 2 ndarray of floats
            Rotor flux [p.u.].
        T_ref : float
            Torque reference [p.u.].

        Returns
        -------
        1 x 2 ndarray
            Steady-state stator current [p.u.].
        """

        # Assume rotor flux orientation, i.e., psiR is aligned with the d-axis
        psiR_d = np.linalg.norm(psiR)
        Xm = self.par.Xm
        Xr = self.par.Xr

        iS_d = psiR_d / Xm
        iS_q = T_ref * Xr / (Xm * psiR_d) / self.par.kT

        iS = dq_2_alpha_beta(np.array([iS_d, iS_q]),
                             np.arctan2(psiR[1], psiR[0]))

        return iS

    def get_continuous_time_state_space(self):
        """
        Calculate the continuous-time state-space model of the system. The state-space model is 
        timing-varying, as the rotor speed is a function of the machine state.

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing matrices F and G of the continuous-time state-space 
            model.
        """

        wr = self.wr
        Rs = self.par.Rs
        Rr = self.par.Rr
        Xr = self.par.Xr
        Xm = self.par.Xm
        D = self.par.D
        tauS = Xr * D / (Rs * Xr**2 + Rr * Xm**2)
        tauR = Xr / Rr

        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

        F = np.array([[-1 / tauS, 0, Xm / (tauR * D), wr * Xm / D],
                      [0, -1 / tauS, -wr * Xm / D, Xm / (tauR * D)],
                      [Xm / tauR, 0, -1 / tauR, -wr],
                      [0, Xm / tauR, wr, -1 / tauR]])

        G = Xr / D * np.dot(np.block([[np.eye(2), np.zeros(
            (2, 2))]]).T, K) * self.conv.v_dc / 2

        return SimpleNamespace(F=F, G=G)

    @property
    def Te(self):
        return self.par.kT * (self.par.Xm / self.par.Xr) * np.cross(
            self.psiR, self.iS)

    @property
    def wr(self):
        return self.par.ws - (self.par.Rr * self.Te /
                              np.linalg.norm(self.psiR)**2)

    def get_next_state(self, matrices, u_abc, kTs, Ts):
        """
        Calculate the next state of the system. 

        Parameters
        ----------
        u_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        matrices : SimpleNamespace
            SimpleNamespace object containing the state-space model matrices.
        kTs : float
            Current discrete time instant [s] (not used).
        Ts : float
            Sampling interval [s] (not used).


        Returns
        -------
        1 x 4 ndarray of floats
            Next state of the system.
        """

        x_kp1 = np.dot(matrices.A, self.x) + np.dot(matrices.B, u_abc)
        return x_kp1

    def get_measurements(self, kTs):
        """
        Update the measurement data of the system.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing the machine torque and (electrical) angular rotor 
            speed.
        """

        return SimpleNamespace(Te=self.Te, wr=self.wr)
