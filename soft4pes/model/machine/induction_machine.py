"""
Induction machine model. The machine operates at a constant electrical angular rotor speed.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import dq_2_alpha_beta
from soft4pes.model.common.system_model import SystemModel


class InductionMachine(SystemModel):
    """
    Induction machine model operating at a constant electrical angular rotor speed.
    The state of the system is the stator current and rotor flux in the alpha-beta frame, i.e., 
    [iS_alpha, iS_beta, psiR_alpha, psiR_beta]^T. The machine is modelled with rotor flux alignment.
    The system input is the converter three-phase switch position or modulating signal. The initial 
    state of the model is based on the stator flux magnitude reference and torque reference.

    Parameters
    ----------
    par : InductionMachineParameters
        Induction machine parameters in p.u.
    conv : converter object
        Converter object.
    base : base value object
        Base values.
    psiS_mag_ref : float
        Stator flux magnitude reference [p.u.].
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
    psiR_mag_ref : float
        Rotor flux magnitude reference [p.u.].
    wr : float
        Electrical angular rotor speed [p.u.].
    cont_state_space : SimpleNamespace
        The continuous-time state-space model of the system.
    """

    def __init__(self, par, conv, base, psiS_mag_ref, T_ref_init):
        self.par = par
        self.set_initial_state(psiS_mag_ref=psiS_mag_ref,
                               T_ref_init=T_ref_init)
        super().__init__(par=par, conv=conv, base=base)
        self.psiR_mag_ref = np.linalg.norm(self.x[2:4])

    def set_initial_state(self, **kwargs):
        """
        Calculates the initial state of the machine based on the torque reference and 
        stator flux magnitude reference.

        Parameters
        ----------
        psiS_mag_ref : float
            The stator flux magnitude reference [p.u.].
        T_ref_init : float
            The initial torque reference [p.u.].
        """

        psiS_mag_ref = kwargs.get('psiS_mag_ref')
        T_ref_init = kwargs.get('T_ref_init')

        # Based on torque reference and stator flux magnitude reference, the rotor
        # flux and rotor speed are calculated
        psiR_dq, self.wr = self.get_steady_state_psir(psiS_mag_ref, T_ref_init)

        # Get the initial angle and align the rotor flux vector with d-axis
        theta = np.arctan2(psiR_dq[1], psiR_dq[0])
        psiR_dq = np.array([np.linalg.norm(psiR_dq), 0])

        # Calculate the stator current
        iS_dq = self.calc_stator_current(psiR_dq, T_ref_init)

        iS = dq_2_alpha_beta(iS_dq, theta)
        psiR = dq_2_alpha_beta(psiR_dq, theta)

        self.x = np.concatenate((iS, psiR))

    def get_steady_state_psir(self, psiS_mag_ref, T_ref):
        """
        Calculates the steady-state rotor flux and rotor speed.

        Parameters
        ----------
        psiS_mag_ref : float
            The stator flux magnitude reference [p.u.].
        T_ref : float
            The torque reference [p.u.].

        Returns
        -------
        psiR_dq : 1 x 2 ndarray
            The steady-state rotor flux in the dq frame [p.u.].
        wr : float
            The steady-state (electrical angular) rotor speed [p.u.].
        """

        D = self.par.D
        kT = self.par.kT
        Xm = self.par.Xm
        Xs = self.par.Xs
        Rr = self.par.Rr

        # The stator flux is aligned with the d-axis, q-component is zero
        psiS_d = psiS_mag_ref

        # Rotor flux in d/q
        psiR_q = -T_ref * D / (kT * Xm * psiS_d)
        Delta = Xm**2 * psiS_d**2 - 4 * Xs**2 * psiR_q**2
        psiR_d = (Xm * psiS_d + np.sqrt(Delta)) / (2 * Xs)
        psiR_dq = np.array([psiR_d, psiR_q])

        # Slip angular frequency
        w_sl = -Rr * Xs * psiR_q / (D * psiR_d)

        # Rotor electrical angular frequency
        wr = self.par.ws - w_sl

        return psiR_dq, wr

    def calc_stator_current(self, psiR_dq, T_ref):
        """
        Calculate the steady-state stator current.

        Parameters
        ----------
        psiR_dq : 1 x 2 ndarray
            The rotor flux in the dq frame [p.u.].
        T_ref : float
            The torque reference [p.u.].

        Returns
        -------
        1 x 2 ndarray
            The stator current in the dq frame [p.u.].
        """

        psiR_mag = np.linalg.norm(psiR_dq)

        iS_d = psiR_mag / self.par.Xm
        iS_q = T_ref / psiR_mag * self.par.Xr / self.par.Xm / self.par.kT
        return np.array([iS_d, iS_q])

    def get_continuous_state_space(self):
        """
        Calculate the continuous-time state-space model of the system.

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
        iS = self.x[0:2]
        psiR = self.x[2:4]
        return self.par.kT * (self.par.Xm / self.par.Xr) * np.cross(psiR, iS)

    def get_next_state(self, matrices, u_abc, kTs):
        """
        Calculate the next state of the system.

        Parameters
        ----------
        u_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        matrices : SimpleNamespace
            A SimpleNamespace object containing the state-space model matrices.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        1 x 4 ndarray of floats
            The next state of the system.
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
            A SimpleNamespace object containing the machine torque.
        """
        return SimpleNamespace(Te=self.Te)
