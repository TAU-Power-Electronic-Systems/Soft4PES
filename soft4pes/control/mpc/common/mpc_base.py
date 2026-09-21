"""This module defines the MPCBase class, which serves as a base class for model predictive 
controllers (MPC). It stores common parameters and provides utility functions for creating reference
and disturbance vectors over the prediction horizon.
"""

import numpy as np

from soft4pes.control.common.utils import wrap_theta
from soft4pes.control.mpc.solvers.utils import compute_next_state


def has_soft_constraints(C_soft_constr, soft_constr_weights,
                         soft_constraints_max):
    """
    Check if soft constraints are enabled by verifying that all soft constraint parameters are 
    provided.

    Parameters
    ----------
    C_soft_constr : ndarray or None
        Output matrix for the constrained variables (used for soft constraints).
    soft_constr_weights : ndarray or None
        Weighting matrix in the objective function for the soft constraints.
    soft_constraints_max : ndarray or None
        Maximum values for constrained variables.

    Returns
    -------
    bool
        True if soft constraints are enabled, False otherwise.

    Raises
    ------
    ValueError
        If only a subset of soft constraint parameters is provided.
    """

    soft_constraint_params = [
        C_soft_constr, soft_constr_weights, soft_constraints_max
    ]
    num_none = sum(p is None for p in soft_constraint_params)
    if 0 < num_none < len(soft_constraint_params):
        raise ValueError(
            "All soft-constraint parameters (C_soft_constr, soft_constr_weights "
            "and soft_constraints_max) must be provided or all must be None to disable soft "
            "constraints.")
    return num_none == 0


class MPCBase:
    """
    Base class for MPC controllers.

    Parameters
    ----------
    C : ndarray
        Output matrix. Defines the tracked variables.
    Q : ndarray
        Weighting matrix in the objective function for the tracked variables.
    Np : int
        Prediction horizon steps.
    lambda_u : float
        Weighting factor for the control effort.
    solver : solver object
        Solver for MPC.
    disc_method : str
        Discretization method for the state-space model.
    C_soft_constr : ndarray, optional
        Output matrix for the constrained variables (used for soft constraints).
    soft_constr_weights : ndarray, optional
        Weighting matrix in the objective function for the soft constraints.
    soft_constraints_max : ndarray, optional
        Maximum values for constrained variables.

    Attributes
    ----------
    C : ndarray
        Output matrix. Defines the tracked variables.
    Q : ndarray
        Weighting matrix in the objective function for the tracked variables.
    M : ndarray
        Gradient matrix for gradient-based MPC
    Np : int
        Prediction horizon steps.
    lambda_u : float
        Weighting factor for the control effort.
    solver : solver object
        Solver for MPC.
    disc_method : str
        Discretization method for the state-space model.
    state_space : SimpleNamespace
        The state-space model of the system.
    u_km1_abc : 1 x 3 ndarray of floats
        Previous (step k-1) three-phase switch position or modulating signal.
    C_soft_constr : ndarray
        Output matrix for the constrained variables (used for soft constraints).
    soft_constr_weights : ndarray
        Weighting matrix in the objective function for the soft constraints.
    soft_constraints_max : ndarray
        Maximum values for constrained variables.
    has_soft_constraints : bool
        Flag indicating whether soft constraints are enabled.
    t_nom : 1 x N ndarray of floats
        Nominal switching time instants within the prediction horizon.
    U_nom : 3 x N ndarray of floats
        Three-phase switch positions corresponding to the nominal switching time instants.
    U_used : int
        Number of switching events that have already been used in the previous control step.
    """

    def __init__(self,
                 C,
                 Q,
                 Np,
                 lambda_u,
                 solver,
                 C_soft_constr=None,
                 soft_constr_weights=None,
                 soft_constraints_max=None,
                 disc_method='exact_discretization'):
        self.C = C
        self.Q = Q
        self.M = None
        self.Np = Np
        self.lambda_u = lambda_u
        self.solver = solver
        self.disc_method = disc_method
        self.state_space = None
        self.u_km1_abc = np.array([0, 0, 0])

        self.C_soft_constr = C_soft_constr
        self.soft_constr_weights = soft_constr_weights
        self.soft_constraints_max = soft_constraints_max
        self.has_soft_constraints = has_soft_constraints(
            C_soft_constr, soft_constr_weights, soft_constraints_max)

        self.t_nom = np.array([])
        self.U_nom = np.array([]).reshape(3, 0)
        self.U_used = 0

    def get_ctr_state_space(self, sys, Ts):
        """
        Get the discrete-time state-space model. If the system has a time-varying model, the state-
        space model is updated at each time step.

        Parameters
        ----------
        sys : system object
            System model.
        Ts : float
            Sampling interval [s].
        """

        if sys.time_varying_model:
            sys.cont_state_space = sys.get_continuous_time_state_space()
            self.state_space = sys.get_discrete_time_state_space(
                Ts, self.disc_method)
        elif self.state_space is None:
            self.state_space = sys.get_discrete_time_state_space(
                Ts, self.disc_method)

    def make_horizon_vector(self, w, Ts, vector_in, start_step=1):
        """
        Predict the future values of a vector over the prediction horizon by rotating the input 
        vector. The rotation is applied to each variable in alpha-beta frame in the input vector, 
        and the result is a vector extended over the prediction horizon.

        The start step determines the prediction time steps. For start_step=1, predictions are for
        k+1 to k+Np, which is typically used for reference trajectories. For start_step=0, 
        predictions are for k to k+Np-1, which is typically used for disturbances.

        Example: vector_in = [vc_ref^T(k), ig_ref^T(k)]^T, Np = 3, start_step = 1, then the output 
        will be [vc_ref^T(k+1), ig_ref^T(k+1), vc_ref^T(k+2), ig_ref^T(k+2), vc_ref^T(k+3),
        ig_ref^T(k+3)]^T.

        Parameters
        ----------
        w : float
            Angular frequency [rad/s].
        Ts : float
            Sampling interval [s].
        vector_in : n x 1 ndarray
            Input vector with variables in alpha-beta frame at current time step.
        start_step : int, optional
            Starting rotation step (default=1 for references k+1...k+Np, 
            use 0 for disturbances k...k+Np-1).

        Returns
        -------
        horizon_vector : Np*n x 1 ndarray
            Vector extended over the prediction horizon with rotations applied.
        """

        # Create a rotation matrix
        theta = w * Ts
        R_rot = np.array([[np.cos(theta), -np.sin(theta)],
                          [np.sin(theta), np.cos(theta)]])

        # Check how many variables are in the input vector
        variables = vector_in.shape[0] // 2

        # Preallocate vector (Np * n_variables * 2, 1)
        horizon_vector = np.zeros(self.Np * variables * 2)

        # Rotate each variable for each step and pack into the horizon vector
        for ell in range(self.Np):
            R_rot_ell = np.linalg.matrix_power(R_rot, ell + start_step)
            for var_idx in range(variables):
                variable = vector_in[var_idx * 2:var_idx * 2 + 2]
                variable_rotated = R_rot_ell.dot(variable)
                start_idx = ell * variables * 2 + var_idx * 2
                horizon_vector[start_idx:start_idx + 2] = variable_rotated

        return horizon_vector

    def make_opp_reference_vector(self, sys, w, i_ref, harm_ref, v_ang):
        """
        Create the reference vector for based on the nominal OPP switching time instants 
        over the prediction horizon. 

        Parameters
        ----------
        sys : system object
            System model.
        w : float
            Angular frequency [p.u.].
        i_ref : 2 x 1 ndarray
            Current reference in alpha-beta frame.
        harm_ref : xarray.Dataset
            Harmonic current reference.
        v_ang : float
            Converter voltage angle [rad].

        Returns
        -------
        horizon_vector : ny*n x 1 ndarray
            Reference vector for the prediction horizon
        """
        # Number of switching events within the prediction horizon
        n = len(self.t_nom)

        # Preallocate the reference vector for the prediction horizon
        horizon_vector = np.zeros(2 * n)

        for ell in range(n):
            theta_pred = sys.base.w * w * self.t_nom[ell]
            R_rot = np.array([[np.cos(theta_pred), -np.sin(theta_pred)],
                              [np.sin(theta_pred),
                               np.cos(theta_pred)]])
            horizon_vector[ell * 2:ell * 2 + 2] = R_rot.dot(i_ref)

            # Add harmonic reference
            if harm_ref is not None:
                theta_harm = wrap_theta(theta_pred + v_ang - np.pi +
                                        np.pi / 2) + np.pi
                ref = harm_ref.sel(theta_index=theta_harm,
                                   method='nearest').values

                if hasattr('sys', 'ws'):
                    gain = sys.par.Xsigma
                else:
                    gain = sys.par.X_fc + sys.par.Xg

                horizon_vector[ell * 2:ell * 2 +
                               2] += ref * sys.conv.v_dc / 2 / gain

        return horizon_vector

    def get_gradient_matrix(self, ctr, sys, x_ell, d_vector=None):
        """
        Compute the gradient matrix for gradient-based MPC.

        Parameters
        ----------
        ctr : controller object
            Controller object.
        sys : system object
            System object.
        x_ell : 1 x n ndarray of floats
            Current state vector.
        d_vector : 1 x m ndarray of floats, optional
            Disturbance vector for the prediction horizon.

        Returns
        -------
        M : ndarray of floats
            Gradient matrix.
        """

        # Number of outputs
        ny = ctr.C.shape[0]

        # Number of switching events within the prediction horizon
        nt = len(ctr.t_nom)

        # Append the current switch position
        t = np.concatenate(([0], ctr.t_nom))
        u = np.vstack((ctr.u_km1_abc, np.transpose(ctr.U_nom)))

        # Preallocate the gradient matrix
        M = np.zeros((ny * nt, nt + 1))

        # Compute the gradient matrix
        for i in range(nt):
            dt = t[i + 1] - t[i]
            state_space = sys.get_discrete_time_state_space(
                dt, ctr.disc_method)

            # Compute the next state
            x_ell_next = compute_next_state(state_space, x_ell, u[i, :],
                                            d_vector, i)

            # Calculate the gradient
            m_ell = ctr.C @ (x_ell_next - x_ell) / dt

            # Add to the gradient matrix
            m_vec = np.tile(m_ell, (nt - i, 1))
            M[ny * i:ny * nt, i + 1] = m_vec.flatten()
            M[ny * i:ny * nt, i] = M[ny * i:ny * nt, i] - m_vec.flatten()

            x_ell = x_ell_next

        # Discard the first column
        M = M[:, 1:]

        return M

    def read_modified_time_instants(self, t_opp, U_opp):
        """
        Read the information about the modificatoins to the switching time 
        instants in the previous control step and update the nominal 
        switching time instants and switch positions

        Parameters
        ----------
        t_opp : ndarray
            Switching time instants of the nominal OPP within the prediction horizon.
        U_opp : ndarray
            Switch positions of the nominal OPP within the prediction horizon.

        """
        # Remove switching events that have already been
        # used in the previous control step
        t_new = t_opp[self.U_used:]
        U_new = U_opp[:, self.U_used:]
        self.U_used = 0

        # Append saved switching events from the previous control step
        self.t_nom = np.concatenate((self.t_nom, t_new))
        self.U_nom = np.hstack((self.U_nom, U_new))

    def write_modified_time_instants(self, Ts, t_opt):
        """
        Save the information about the modifications to the switching time instants 
        in the current control step for the next control step.
        
        
        Parameters
        ----------
        Ts : float
            Sampling interval [s].
        t_opt : ndarray
            Switching time instants of the optimal solution within the prediction horizon.

        """
        # Save/remove switching instants and switch positions for the next control step
        t_opt_Ts = np.sum(t_opt < Ts)
        t_nom_Ts = np.sum(self.t_nom < Ts)
        t_diff = t_nom_Ts - t_opt_Ts

        U_tmp = self.U_nom

        if t_diff > 0:
            # Save switching events that have not been used in the current control step
            self.t_nom = np.linspace(1e-6, t_diff * 1e-6, t_diff)
            self.U_nom = U_tmp[:, t_opt_Ts:t_nom_Ts]
        elif t_diff < 0:
            # Remove switching events that have been used in the current control step
            self.U_used = -t_diff
            self.t_nom = np.array([])
            self.U_nom = np.array([]).reshape(3, 0)
        else:
            self.t_nom = np.array([])
            self.U_nom = np.array([]).reshape(3, 0)

        # Update the current switch position for the next control step
        if t_opt_Ts > 0:
            self.u_km1_abc = U_tmp[:, t_opt_Ts - 1]

    def make_reference_vector(self, w, Ts, ref):
        """
        Create the reference vector for the prediction horizon (k+1 to k+Np).

        Parameters
        ----------
        w : float
            Angular frequency [rad/s].
        Ts : float
            Sampling interval [s].
        ref : n x 1 ndarray
            Reference values for the controlled outputs at the current time step.

        Returns
        -------
        ref_vector : Np*n x 1 ndarray
            Reference vector for the prediction horizon.
        """

        return self.make_horizon_vector(w, Ts, ref, start_step=1)

    def make_disturbance_vector(self, w, Ts, d):
        """
        Create the disturbance vector for the prediction horizon (k to k+Np-1).

        Parameters
        ----------
        w : float
            Angular frequency [rad/s].
        Ts : float
            Sampling interval [s].
        d : n x 1 ndarray
            Disturbance values at the current time step.

        Returns
        -------
        dist_vector : Np*n x 1 ndarray
            Disturbance vector for the prediction horizon.
        """

        return self.make_horizon_vector(w, Ts, d, start_step=0)
