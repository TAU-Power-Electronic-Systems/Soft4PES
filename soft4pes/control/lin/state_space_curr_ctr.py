""" State-space current controller with anti-windup scheme 
    for grid-connected converter with RL load """

from types import SimpleNamespace
import numpy as np
from soft4pes.utils.conversions import alpha_beta_2_dq, dq_2_abc, dq_2_alpha_beta


class RLGridStateSpaceCurrCtr:
    """
    State-space current controller with anti-windup scheme 
    for grid-connected converter with RL load.
    
    Attributes
    ----------
    Rf : float
        Resistance [p.u.].
    Xf : float
        Reactance [p.u.].
    Ts : float
        Sampling interval [s].           
    Ts_pu : float
        Sampling interval [p.u.].
    ctr_pars : SimpleNamespace
         A SimpleNamespace object containing controller parameters delta, K_i, k_ii and K_ti 
    uc_ii_dq : 1 x 2 ndarray of floats
        Converter voltage reference after current controller integrator in dq frame [p.u.].
    uc_km1_dq : 1 x 2 ndarray of floats
        Previous converter voltage reference in dq frame [p.u.].                                    
    i_ref_seq_dq : Sequence
        Current reference sequence instance in dq-frame [p.u.].   
    sim_data : dict
        Controller data.
    """

    def __init__(self, sys, base, Ts, i_ref_seq_dq):
        """
        Initialize a RLGridStateSpaceCurrCtr.

        Parameters
        ----------
        sys : system object
           System model.
        base : base-value object
           Base values.
        Ts : float
           Sampling interval [s].
        i_ref_seq_dq : Sequence
           Current reference sequence instance in dq-frame [p.u.].
        """

        self.Xf = sys.Xg  # Assume the inductances are equal
        self.Rf = sys.Rg  # Assume the resitances are equal
        self.Ts = Ts
        self.Ts_pu = self.Ts * base.w
        self.ctr_pars = self.get_state_space_ctr_pars()
        self.u_ii_dq = np.zeros(2)
        self.uc_km1_dq = np.zeros(2)
        self.i_ref_seq_dq = i_ref_seq_dq

        self.sim_data = {
            'ig_ref': [],
            'u': [],
            't': [],
        }

    def __call__(self, sys, conv, t):
        """
        Perform control.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        t : float
            Current time [s].

        Returns
        -------
        1 x 3 ndarray of floats
            Modulating signal.
        """

        vg = sys.get_grid_voltage(t)

        # Get the reference for current step
        ic_ref_dq = self.i_ref_seq_dq(t)

        # Calculate the transformation angle
        theta = np.arctan2(vg[1], vg[0])

        # Get dq frame current (converter current equals grid current due to lack of a filter)
        ic_dq = alpha_beta_2_dq(sys.x, theta)

        # Maximum converter output voltage
        u_max = conv.v_dc / 2

        # Assume filter capacitor voltage equals grid voltage (No filter considered)
        uf_dq = vg

        # Compute the converter voltage reference using the state space controller with anti-windup
        uc_dq = self.state_space_controller(ic_dq, ic_ref_dq, uf_dq, u_max)

        # Transform the converter voltage reference back to abc frame
        uc_abc = dq_2_abc(uc_dq, theta)

        u_k = uc_abc / (conv.v_dc / 2)

        # Save controller data
        ig_ref = dq_2_alpha_beta(ic_ref_dq, theta)
        self.save_data(ig_ref, u_k, t)

        return u_k

    def get_state_space_ctr_pars(self):
        """
        Calculate state-space controller parameters.
        
        Returns
        -------
        SimpleNamespace
            Controller parameters.
        """
        Ts_pu = self.Ts_pu
        Rf = self.Rf
        Xf = self.Xf

        # Closed-loop controller bandwidth (10x crossover frequency)
        alpha_c = 2 * np.pi / 10 / Ts_pu

        # Consider delta equals to one due to not considering delay
        delta = 1

        # Coefficients
        phi = np.exp((-Rf / Xf) * Ts_pu) * delta
        landa = (delta - phi) / Rf

        # The closed-loop pole locations
        p_1 = 0
        p_2 = np.exp(-alpha_c * Ts_pu)
        p_3 = p_2

        # Coefficients
        k_2 = -p_1 - p_2 - p_3 + phi + 1
        k_1 = (p_1 * p_2 + p_1 * p_3 + p_2 * p_3 + k_2 * phi + k_2 -
               phi) / landa

        # State feedback gain
        K_i = np.array([k_1, 0, k_2 * 0])

        # Integral gain
        k_ii = (-p_1 * p_2 * p_3 + k_1 * landa - k_2 * phi) / landa

        # Feedforward gain
        k_ti = k_ii / (1 - p_3)

        return SimpleNamespace(delta=delta, K_i=K_i, k_ii=k_ii, k_ti=k_ti)

    def state_space_controller(self, ic_dq, ic_ref_dq, uf_dq, u_max):
        """
        State-space controller in dq frame.
        
        Parameters
        ----------
        ic_dq : 1 x 2 ndarray of floats
            Grid Current in dq frame [p.u.].
        ic_ref_dq : 1 x 2 ndarray of floats
            Reference current in dq frame [p.u.].
        uf_dq : 1 x 2 ndarray of floats
            Grid voltage in dq frame [p.u.] (In case: Without considering the filter). 
        u_max : float
            Maximum converter output voltage [p.u.].        

        Returns
        -------
        1 x 2 ndarray of floats
            Converter voltage reference in dq frame [p.u.].
        """

        X_LC = np.array([ic_dq, uf_dq, self.uc_km1_dq])

        # State space controller with anti-windup in dq frame
        uc_ref_dq_unlim = (self.ctr_pars.k_ti * ic_ref_dq) - np.dot(
            self.ctr_pars.K_i, X_LC) + self.u_ii_dq

        # Limiting the converter voltage reference
        uc_ref_dq = self.voltage_reference_limiter(u_max, uc_ref_dq_unlim)

        self.u_ii_dq += self.ctr_pars.k_ii * ((
            (uc_ref_dq - uc_ref_dq_unlim) / self.ctr_pars.k_ti) +
                                              (ic_ref_dq - ic_dq))

        self.uc_km1_dq = self.ctr_pars.delta * uc_ref_dq

        return uc_ref_dq

    def voltage_reference_limiter(self, u_max, uc_ref_dq_unlim):
        """
        limit the converter voltage reference.

        Parameters
        ----------
        u_max : float
            Maximum converter output voltage [p.u.].
        uc_ref_dq_unlim : 1 x 2 ndarray of floats
            Unlimited converter voltage reference [p.u.].

        Returns
        -------
        1 x 2 ndarray of floats
            Limited converter voltage reference [p.u.].
        """

        uc_mag = np.linalg.norm(uc_ref_dq_unlim)

        if uc_mag <= u_max:
            uc_ref_dq = uc_ref_dq_unlim
        else:
            uc_ref_dq = (uc_ref_dq_unlim / uc_mag) * u_max

        return uc_ref_dq

    def save_data(self, ig_ref, u_k, t):
        """
        Save controller data.

        Parameters
        ----------
        ig_ref : 1 x 2 ndarray of floats
            Current reference in alpha-beta frame.
        u_k : 1 x 3 ndarray of ints
            Converter 3-phase switch position.
        t : float
            Current time [s].
        """
        self.sim_data['ig_ref'].append(ig_ref)
        self.sim_data['u'].append(u_k)
        self.sim_data['t'].append(t)
