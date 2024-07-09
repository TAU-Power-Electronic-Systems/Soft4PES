""" Model-predictive stator current control for an induction machine."""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils.conversions import dq_2_alpha_beta


class IMMpcCurrCtr:
    """
    Model-predictive current control for an induction machine. The controller aims to track
    the stator currents in the alpha-beta frame. The current reference is calculated based on the
    torque reference.

    Attributes
    ----------
    solver : solver object
        Solver for model-predictive control.
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon.
    Ts : float
        Sampling time [s].
    T_ref_seq : Sequence
        Torque reference sequence [p.u.].
    u_km1 : 1 x 3 ndarray of ints
        Previous 3-phase switch position.
    state_space : SimpleNamespace 
        The state-space model of the system.
    C : 2 x 4 ndarray of ints
        Output matrix.
    sim_data : dict
        Controller data.
    """

    def __init__(self, solver, lambda_u, Np, Ts, T_ref):
        """
        Initialize an IMMpcCurrCtr instance.

        Parameters
        ----------
        solver : solver object
            Solver for an MPC algorithm.
        lambda_u : float
            Weighting factor for the control effort.
        Np : int
            Prediction horizon.
        Ts : float
            Sampling interval [s].
        T_ref_seq : Sequence
            Torque reference sequence [p.u.].
        """
        self.lambda_u = lambda_u
        self.Np = Np
        self.Ts = Ts
        self.u_km1 = np.array([0, 0, 0])
        self.T_ref_seq = T_ref
        self.state_space = SimpleNamespace()
        self.solver = solver

        # Output matrix
        self.C = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])

        self.sim_data = {
            'u': [],
            'iS_ref': [],
            't': [],
            'T_ref': [],
        }

    def __call__(self, sys, conv, t):
        """
        Perform MPC.

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
            3-phase switch position or modulating signals.
        """

        self.state_space = sys.get_discrete_state_space(conv.v_dc, self.Ts)

        # Get the stator current reference for the current step
        psiR_mag_ref = np.linalg.norm(np.array([sys.x0[2], sys.x0[3]]))
        T_ref = self.T_ref_seq(t)
        T_ref = T_ref[0]
        is_dq_ref = sys.calc_stator_current(psiR_mag_ref, T_ref)

        # Get the grid-voltage angle and calculate the reference in alpha-beta frame
        theta = np.arctan2(sys.x[3], sys.x[2])
        i_ref = dq_2_alpha_beta(is_dq_ref, theta)

        # Predict the current reference over the prediction horizon
        # Make a rotation matrix
        Ts_pu = self.Ts * sys.base.w
        delta_theta = sys.wr * Ts_pu
        R_ref = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                          [np.sin(delta_theta), np.cos(delta_theta)]])

        # Predict the reference by rotating the current reference
        y_ref = np.zeros((self.Np, 2))
        i_ref_temp = i_ref
        for k in range(self.Np):
            y_ref[k, :] = np.dot(R_ref, i_ref_temp)
            i_ref_temp = y_ref[k, :]

        # Solve the control problem
        uk = self.solver(sys, conv, self, y_ref)
        self.u_km1 = uk

        self.save_data(i_ref, uk, T_ref, t)

        return uk

    def get_next_state(self, sys, xk, uk, k):
        """
        Calculate the next state of the system.

        Parameters
        ----------
        sys : system object
            The system model, not used in this method.
        xk : 1 x 2 ndarray of floats
            The current state of the system.
        uk : 1 x 3 ndarray of ints
            Converter 3-phase switch position.
        k : int
            The solver prediction step. Not used in this method.

        Returns
        -------
        1 x 2 ndarray of floats
            The next state of the system.
        """

        return np.dot(self.state_space.A, xk) + np.dot(self.state_space.B, uk)

    def save_data(self, iS_ref, u_k, T_ref, t):
        """
        Save controller data.

        Parameters
        ----------
        iS_ref : 1 x 2 ndarray of floats
            Current reference in alpha-beta frame.
        u_k : 1 x 3 ndarray of ints
            Converter 3-phase switch position.
        t : float
            Current time [s].
        """
        self.sim_data['iS_ref'].append(iS_ref)
        self.sim_data['u'].append(u_k)
        self.sim_data['T_ref'].append(T_ref)
        self.sim_data['t'].append(t)
