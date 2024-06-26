from types import SimpleNamespace
import numpy as np
from soft4pes.utils.conversions import alpha_beta_2_dq
from soft4pes.utils.conversions import dq_2_abc

class LinearGridCurrentControl:
    def __init__(self, sys, base, Ts, i_ref_seq_dq):
        self.L = sy.L  # Inductance
        self.R = sys.R  # Resistance
        self.Ts = Ts  # Sampling time
        self.alpha_c = (((2 * np.pi / 10) / Ts)/ base.w)  # Controller bandwidth
        self.k_p = self.alpha_c * L  # Proportional gain
        self.k_i = self.alpha_c * R  # Integral gain
        self.integral_error_d = 0.0
        self.integral_error_q = 0.0
        self.u_km1 = np.array([0, 0, 0])
        self.i_ref_seq_dq = i_ref_seq_dq
        self.state_space = SimpleNamespace()
      
    def __call__(self, sys, conv, t):
        # Get the discrete state-space model of the system
        self.state_space = sys.get_discrete_state_space(conv.v_dc, self.Ts)

        # Get the grid voltage
        vg = sys.get_grid_voltage(t)

        # Get the reference for current step
        i_ref_dq = self.i_ref_seq_dq(t)
        vg = sys.get_grid_voltage(t)
        theta = np.arctan2(vg[1], vg[0])
        i_ref = dq_2_alpha_beta(i_ref_dq, theta)

        u_c_dq = self.pi_controller(sys, conv, sys.x, vg, i_ref, u_seq, self.u_km1)
      
        u_k= dq_2_abc(u_c_dq, theta)  
        self.u_km1 = u_k
        return u_k
      
    def pi_controller (self, sys, conv, xk, vg, i_ref_k, u_seq, u_km1):
        # PI controller in dq frame
        error_d = i_ref_k[0] - xk[0]
        error_q = i_ref_k[1] - xk[1]
        
        self.integral_error_d += error_d * self.Ts
        self.integral_error_q += error_q * self.Ts

        u_c_d = self.k_p * error_d + self.k_i * self.integral_error_d
        u_c_q = self.k_p * error_q + self.k_i * self.integral_error_q

        # Compute the next state
        x_kp1 = np.dot(self.state_space.A, xk) + \
                np.dot(self.state_space.B1, u_k) + \
                np.dot(self.state_space.B2, vg)
      
        # Get current in alpha-beta frame
        i_alpha_beta = sys.get_current(x_kp1)
      
        # Convert current to dq frame
        i_dq = alpha_beta_2_dq(i_alpha_beta, theta)
      
        return np.array([u_c_d, u_c_q])
      

      
    def control(self, i_alpha_beta, i_ref_seq_dq, theta):
        # Main control function
        # Get current in alpha-beta frame
        i_alpha_beta = self.get_current(i_alpha_beta)
        
        # Convert current to dq frame
        i_dq = alpha_beta_2_dq(i_alpha_beta, theta)
        
        # Compute control voltage in dq frame using PI controller
        u_c_dq = self.pi_controller(i_dq, i_ref_seq_dq)
        
        # Convert control voltage to abc frame
        u_c_abc = self.dq_2_abc(u_c_dq, theta)
        
        return u_c_abc
