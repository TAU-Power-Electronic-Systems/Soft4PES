"""
Synchronous machine model. The machine operates at a constant electrical angular rotor speed.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import dq_2_alpha_beta
from soft4pes.utils import alpha_beta_2_dq
from soft4pes.model.common.system_model import SystemModel

class SynchronousMachine(SystemModel):
    """

    Parameters
    ----------
    par : SynchronousMachineParameters
        Synchronous machine parameters in p.u.
    conv : converter object
        Converter object.
    base : base value object
        Base values.
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
    cont_state_space : SimpleNamespace
        The continuous-time state-space model of the system.
    state_map : dict
        A dictionary mapping states to elements of the state vector.
    """

    def __init__(self, par, conv, base, T_ref_init):
        self.par = par
        self.generate_references(par)
        self.set_initial_state(T_ref_init=T_ref_init)

        x_size = 2
        state_map = {
            'iS_dq': slice(0, 2),  # Stator current (x[0:2])
        }
        super().__init__(par=par,
                         conv=conv,
                         base=base,
                         x_size=x_size,
                         state_map=state_map)
        self.time_varying_model = True

    def generate_references(self,par):
        
        # MTPA
        i_mag_range  = np.linspace(0,1,101)
        theta_range  = np.linspace(0,np.pi/2,2001)

        Te = []
        isd = []
        isq = []
        for i_mag in i_mag_range:
            id_vec = -i_mag * np.cos(theta_range)
            iq_vec =  i_mag * np.sin(theta_range)
            Te_map = np.dot(iq_vec.reshape(-1, 1)/par.pf,(par.Xsd - par.Xsq)*id_vec.reshape(1, -1) + par.PsiPM);

            Te_line = []
            for kk in range(theta_range.size):
                Te_line.append(Te_map[kk][kk])

            max_value = max(Te_line)
            max_index = Te_line.index(max_value)
            Te.append(Te_line[max_index])
            isd.append(id_vec[max_index])
            isq.append(iq_vec[max_index])

            self.Te_ref = Te
            self.is_dq_ref = np.array([isd,isq]).T

    def set_initial_state(self, **kwargs):
        """
        Calculates the initial state of the machine based on the torque reference and 
        stator flux magnitude reference.

        Parameters
        ----------
        T_ref_init : float
            The initial torque reference [p.u.].
        """

        T_ref_init = kwargs.get('T_ref_init')

        # Calculate references from the MTPA for th inital torque
        iS_dq = self.calc_stator_current(T_ref_init)

        self.x = iS_dq

    def calc_stator_current(self, T_ref):
        """
        Calculate the steady-state stator current.

        Parameters
        ----------
        T_ref : float
            The torque reference [p.u.].

        Returns
        -------
        1 x 2 ndarray
            The stator current in the dq frame [p.u.].
        """

        closest_value = min(self.Te_ref, key=lambda x: abs(x - T_ref)) 
        return self.is_dq_ref[self.Te_ref.index(closest_value)]

    def get_continuous_state_space(self,theta=0):
        """
        Calculate the continuous-time state-space model of the system.

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing matrices F, G1, and G2 of the continuous-time state-space 
            model.
        """
        ws = self.par.ws
        Rs = self.par.Rs
        Xsd = self.par.Xsd
        Xsq = self.par.Xsq
        PsiPM = self.par.PsiPM

        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])
        
        R = np.array([[ np.cos(theta), np.sin(theta)],
                      [-np.sin(theta), np.cos(theta)]])
        
        F = np.array([[-Rs / Xsd,  ws * Xsq / Xsd],
                      [-ws * Xsd / Xsq, -Rs / Xsq]])

        G1 = np.dot(np.dot(np.array([[1 / Xsd, 0],
                                     [0, 1 / Xsq]]), R),K) * self.conv.v_dc / 2
        
        G2 = np.array([0,-ws * PsiPM / Xsq])
        
        return SimpleNamespace(F=F, G1=G1, G2=G2)

    @property
    def Te(self):
        iS_dq = self.x
        return self.par.kT * ((self.par.Xsd - self.par.Xsq) * iS_dq[0] + self.par.PsiPM) * iS_dq[1]

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
        1 x 2 ndarray of floats
            The next state of the system.
        """

        x_kp1 = np.dot(matrices.A, self.x) + np.dot(matrices.B1, u_abc) + matrices.B2
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
