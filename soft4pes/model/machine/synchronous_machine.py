"""
Permanent magnet synchronous machine (PMSM) model. The machine operates at a constant electrical 
angular rotor speed.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.model.common.system_model import SystemModel
from soft4pes.utils.conversions import alpha_beta_2_dq, dq_2_alpha_beta


class MTPALookupTable:
    """
    Maximum Torque Per Ampere (MTPA) lookup table for synchronous machines.
    
    This class generates and manages the MTPA trajectory, providing optimal
    current references for given torque demands.
    """

    def __init__(self, par, iS_mag_points=101, theta_points=2001):
        """
        Initialize MTPA lookup table.
        
        Parameters
        ----------
        par : SynchronousMachineParameters
            Machine parameters.
        iS_mag_points : int, optional
            Number of stator current magnitude points for trajectory generation. Default is 101.
        theta_points : int, optional
            Number of angle points for trajectory generation. Default is 2001.
        """

        self.par = par
        self.iS_mag_points = iS_mag_points
        self.theta_points = theta_points
        self.mtpa_lut = {}  # Dictionary: {torque: iS_dq}
        self.generate_mtpa_trajectory()

    def generate_mtpa_trajectory(self):
        """
        Generate the maximum torque per ampere (MTPA) trajectory.
        
        Creates a lookup table mapping torque values to optimal stator current references.
        """

        iS_mag_range = np.linspace(0, 1, self.iS_mag_points)
        theta_range = np.linspace(0, np.pi / 2, self.theta_points)

        for iS_mag in iS_mag_range:
            id_trajectory = -iS_mag * np.cos(theta_range)
            iq_trajectory = iS_mag * np.sin(theta_range)

            # Calculate torque map for this current magnitude
            Te_map = np.dot(
                iq_trajectory.reshape(-1, 1) / self.par.pf,
                (self.par.Xsd - self.par.Xsq) * id_trajectory.reshape(1, -1) +
                self.par.PsiPM)

            # Extract diagonal (optimal torque for each angle)
            Te_line = [Te_map[kk, kk] for kk in range(theta_range.size)]

            # Find maximum torque and corresponding currents
            max_index = np.argmax(Te_line)
            optimal_torque = Te_line[max_index]
            optimal_iS_dq = np.array(
                [id_trajectory[max_index], iq_trajectory[max_index]])

            # Store in lookup table
            self.mtpa_lut[optimal_torque] = optimal_iS_dq

    def get_optimal_current(self, Te_ref):
        """
        Get optimal stator current reference for given torque reference.
        
        Parameters
        ----------
        Te_ref : float
            Torque reference [p.u.].
     
        Returns
        -------
        ndarray
            Optimal stator current reference [p.u.].
        """

        # Find closest torque value in lookup table
        closest_torque = min(self.mtpa_lut.keys(),
                             key=lambda torque: abs(torque - Te_ref))

        return np.array(self.mtpa_lut[closest_torque])


class SynchronousMachine(SystemModel):
    """
    Permanent magnet synchronous machine (PMSM) model. The model operates at a constant electrical 
    angular rotor speed. The system is modelled in a dq-frame, where the d-axis is aligned with the 
    rotor angle.

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
    i_mag_points : int, optional
        Number of current magnitude points for MTPA trajectory generation. The default is 101.
    theta_points : int, optional
        Number of angle points for MTPA trajectory generation. The default is 2001.

    Attributes
    ----------
    data : SimpleNamespace
        Namespace for storing simulation data.
    par : SynchronousMachineParameters
        Synchronous machine parameters in p.u.
    conv : converter object
        Converter object.
    base : base value object
        Base values.
    x : 1 x 2 ndarray of floats
        Current state of the machine [p.u.].
    cont_state_space : SimpleNamespace
        The continuous-time state-space model of the system.
    state_map : dict
        A dictionary mapping states to elements of the state vector.
    time_varying_model : bool
        Indicates if the system model is time-varying.
    mtpa : MTPALookupTable
        Maximum torque per ampere (MTPA) lookup table.
    theta_el : float
        Electrical angle of the machine [rad].
    """

    def __init__(self,
                 par,
                 conv,
                 base,
                 T_ref_init,
                 i_mag_points=101,
                 theta_points=2001):
        self.par = par
        self.theta_el = 0

        self.mtpa = MTPALookupTable(par, i_mag_points, theta_points)
        self.set_initial_state(T_ref_init=T_ref_init)

        x_size = 2
        state_map = {
            'iS': slice(0, 2),  # Stator current (x[0:2])
        }
        super().__init__(par=par,
                         conv=conv,
                         base=base,
                         x_size=x_size,
                         state_map=state_map)
        self.time_varying_model = True

    def set_initial_state(self, **kwargs):
        """
        Calculates the initial state of the machine based on the torque reference.

        Parameters
        ----------
        T_ref_init : float
            The initial torque reference [p.u.].
        """

        T_ref_init = kwargs.get('T_ref_init')

        # Get the initial stator current from MTPA
        iS_dq = self.mtpa.get_optimal_current(T_ref_init)
        self.x = dq_2_alpha_beta(iS_dq, self.theta_el)

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
            A SimpleNamespace object containing matrices F, G1, and G2 of the continuous-time 
            state-space model.
        """

        ws = self.par.ws
        Rs = self.par.Rs
        Xsd = self.par.Xsd
        Xsq = self.par.Xsq
        PsiPM = self.par.PsiPM

        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

        R = np.array([[np.cos(self.theta_el),
                       np.sin(self.theta_el)],
                      [-np.sin(self.theta_el),
                       np.cos(self.theta_el)]])

        F = np.array([[-Rs / Xsd, ws * Xsq / Xsd],
                      [-ws * Xsd / Xsq, -Rs / Xsq]])

        G1 = np.dot(np.dot(np.array([[1 / Xsd, 0], [0, 1 / Xsq]]), R),
                    K) * self.conv.v_dc / 2

        G2 = np.array([0, -ws * PsiPM / Xsq])

        return SimpleNamespace(F=F, G1=G1, G2=G2)

    @property
    def Te(self):
        iS_dq = alpha_beta_2_dq(self.x, self.theta_el)
        return self.par.kT * ((self.par.Xsd - self.par.Xsq) * iS_dq[0] +
                              self.par.PsiPM) * iS_dq[1]

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

        x_dq = alpha_beta_2_dq(self.x, self.theta_el)
        x_kp1_dq = np.dot(matrices.A, x_dq) + np.dot(matrices.B1,
                                                     u_abc) + matrices.B2
        return dq_2_alpha_beta(x_kp1_dq, self.theta_el)

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
            A SimpleNamespace object containing the machine torque and rotor electrical angle.
        """

        return SimpleNamespace(Te=self.Te, theta_el=self.theta_el)

    def update_internal_variables(self, kTs):
        """
        Update the electrical rotor angle of the machine.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].
        """

        self.theta_el = kTs * self.par.ws * self.base.w
