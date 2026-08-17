"""
Gradient-based predictive pulse pattern control (GP3C) solver for 
systems utilizing optimized pulse patterns.

The QP is solved using the `qpsolvers` package and the `DAQP` solver (MIT license).
"""

import numpy as np
from qpsolvers import solve_qp
from soft4pes.control.mpc.common.solver_base import MPCSolverBase
from soft4pes.control.mpc.solvers.utils import compute_next_state


class GP3C(MPCSolverBase):
    """
    GP3C solver for OPP-based control.

    This solver optimizes the switching time instants of the nominal OPP within 
    the prediction horizon by describing the evolution of the system with gradients, 
    and formulating the control problem as a quadratic program (QP).

    The algorithm is based on:
    M. A. W. Begh, P. Karamanakos and T. Geyer, "Gradient-Based Predictive Pulse Pattern 
    Control of Medium-Voltage Drives—Part I: Control, Concept, and Analysis," 
    in IEEE Transactions on Power Electronics, vol. 37, no. 12, pp. 14222-14236, Dec. 2022

    """

    def get_gradient_matrix(self, ctr, sys, x_ell, d_vector=None):
        """
        Compute the gradient matrix

        Parameters
        ----------
        ctr : controller object
            Controller object.

        sys : system object
            System object.

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
        u = np.vstack((ctr.u_km1_abc, np.transpose(ctr.U)))

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

    def __call__(self, sys, ctr, y_ref_pred, d_vector=None):
        """
        Solve the MPC optimization problem by formulating and solving a quadratic program.

        Parameters
        ----------
        sys : system object
            System model.
        ctr : controller object
            Controller object.
        y_ref_pred : ndarray of floats
            Reference trajectory over the prediction horizon [p.u.].
        d_vector : ndarray of floats (optional)
            Disturbance vector over the prediction horizon [p.u.].
        Returns
        -------
        t_opt : ndarray of floats
            Optimal switching time instants over the prediction horizon
        """

        nt = len(ctr.t_nom)
        ny = ctr.C.shape[0]

        Tp = ctr.Np * ctr.Ts

        # Compute the gradient matrix
        M = self.get_gradient_matrix(ctr, sys, sys.x, d_vector)

        # Formulate the objective function for the QP
        Qblk = np.kron(np.eye(nt), ctr.Q)
        H = (M.T @ Qblk @ M + np.eye(nt) * ctr.lambda_u) * Tp * Tp

        x_rep = np.tile(sys.x[0:ny], (nt, 1)).flatten()
        r = y_ref_pred - x_rep
        f = (-r @ Qblk @ M - ctr.lambda_u * ctr.t_nom) * Tp

        # Formulate the constraints for the QP
        shifted_eye = np.roll(np.eye(nt), shift=1, axis=1)
        A = np.eye(nt) - np.triu(shifted_eye)

        b = np.zeros((nt, 1))
        b[-1] = 1

        lb = np.zeros((nt, 1))
        ub = np.ones((nt, 1))

        # Solve the QP
        t_opt = solve_qp(H, f, A, b, lb=lb, ub=ub, solver='daqp')

        if t_opt is None:
            raise ValueError(
                "QP solver failed to find a solution. Please check the problem formulation and constraints."
            )
        else:
            t_opt = t_opt * Tp

        return t_opt
