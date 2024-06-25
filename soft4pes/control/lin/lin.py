import numpy as np

class LinearGridCurrentControl:
    def __init__(self, L, R, Ts):
        self.L = L  # Inductance
        self.R = R  # Resistance
        self.Ts = Ts  # Sampling time
        self.alpha_c = (2 * np.pi / 10) / Ts  # Controller bandwidth
        self.k_p = self.alpha_c * L  # Proportional gain
        self.k_i = self.alpha_c * R  # Integral gain
        self.integral_error_d = 0.0
        self.integral_error_q = 0.0

    def alpha_beta_2_dq(self, i_alpha_beta, theta):
        # Convert alpha-beta to dq frame
        transformation_matrix = np.array([
            [np.cos(theta), np.sin(theta)],
            [-np.sin(theta), np.cos(theta)]
        ])
        i_dq = np.dot(transformation_matrix, i_alpha_beta)
        return i_dq

    def pi_controller(self, i_dq, i_ref_seq_dq):
        # PI controller in dq frame
        error_d = i_ref_seq_dq[0] - i_dq[0]
        error_q = i_ref_seq_dq[1] - i_dq[1]
        
        self.integral_error_d += error_d * self.Ts
        self.integral_error_q += error_q * self.Ts

        u_c_d = self.k_p * error_d + self.k_i * self.integral_error_d
        u_c_q = self.k_p * error_q + self.k_i * self.integral_error_q

        return np.array([u_c_d, u_c_q])

    def control(self, i_alpha_beta, i_ref_seq_dq, theta):
        # Main control function
        # Get current in alpha-beta frame
        i_alpha_beta = self.get_current(i_alpha_beta)
        
        # Convert current to dq frame
        i_dq = self.alpha_beta_2_dq(i_alpha_beta, theta)
        
        # Compute control voltage in dq frame using PI controller
        u_c_dq = self.pi_controller(i_dq, i_ref_seq_dq)
        
        # Convert control voltage to abc frame
        u_c_abc = self.dq_2_abc(u_c_dq, theta)
        
        return u_c_abc
