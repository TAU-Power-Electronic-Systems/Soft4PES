"""
This module contains the class MPCQP, which is used to solve the model predictive 
control (MPC) problem using a quadratic program (QP) solver. 

The formulation of the control problem and the QP matrices are based on:

M. Rossi, P. Karamanakos, and F. Castelli-Dezza, “An indirect model predictive control method for
grid-connected three-level neutral point clamped converters with LCL filters,” IEEE Trans. Ind.
Applicat., vol. 58, no. 3, pp. 3750-3768, May/Jun. 2022. The same states do not have to be both
controlled (output variables) and constrained.

M. A. W. Begh, P. Karamanakos and T. Geyer, "Gradient-Based Predictive Pulse Pattern 
Control of Medium-Voltage Drives—Part I: Control, Concept, and Analysis," 
in IEEE Transactions on Power Electronics, vol. 37, no. 12, pp. 14222-14236, Dec. 2022

The QP is solved using the `qpsolvers` package and the `DAQP` solver (MIT license).
"""

import numpy as np
from qpsolvers import solve_qp
from soft4pes.control.mpc.common.solver_base import MPCSolverBase
from soft4pes.control.mpc.solvers.utils import make_QP_matrices


class MPCQP(MPCSolverBase):
    """
    QP solver for MPC.
    
    This solver reformulates the MPC problem as a quadratic program with linear constraints, solving
    it at each time step to find the optimal control action. 

    Attributes
    ----------
    QP_matrices : SimpleNamespace
        Namespace containing the precomputed matrices used in the QP problem if such are available.
    """

    def __init__(self):
        super().__init__()
        self.QP_matrices = None

    def __call__(self, sys, ctr, y_ref_pred, d_pred=None):
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
        d_pred : ndarray of floats, optional
            Disturbance trajectory over the prediction horizon [p.u.].

        Returns
        -------
        opt_sol : 1 x n ndarray of floats
            Optimal solution for the control action at the current time step.
        """

        if ctr.M is not None:
            nt = len(ctr.t_nom)
            ny = ctr.C.shape[0]

            Tp = ctr.Np * ctr.Ts

            # Formulate the objective function for the QP
            Qblk = np.kron(np.eye(nt), ctr.Q)
            H = (ctr.M.T @ Qblk @ ctr.M + np.eye(nt) * ctr.lambda_u) * Tp * Tp

            x_rep = np.tile(sys.x[0:ny], (nt, 1)).flatten()
            r = y_ref_pred - x_rep
            f = (-r @ Qblk @ ctr.M - ctr.lambda_u * ctr.t_nom) * Tp

            # Formulate the constraints for the QP
            shifted_eye = np.roll(np.eye(nt), shift=1, axis=1)
            A = np.eye(nt) - np.triu(shifted_eye)

            b = np.zeros((nt, 1))
            b[-1] = 1

            lb = np.zeros((nt, 1))
            ub = np.ones((nt, 1))

            # Solve the QP
            t_opt = solve_qp(H, f, A, b, lb=lb, ub=ub, solver='daqp')

            opt_sol = t_opt * Tp

            return opt_sol

        # If the QP matrices have not been computed yet or if the system has a time-varying model,
        # compute the QP matrices
        if not self.initialized or sys.time_varying_model:
            self.QP_matrices = make_QP_matrices(ctr)
            self.initialized = True

        m = self.QP_matrices
        x = sys.x
        u_km1 = ctr.u_km1_abc

        # Formulate the time varying matrix Theta
        Theta = -m.Upsilon.T.dot(m.Q_tilde).dot(y_ref_pred - m.Gamma.dot(
            x)) - ctr.lambda_u * m.S.T.dot(m.E).dot(u_km1)

        # Check if disturbance term is present and add it to Theta if it is
        if d_pred is not None:
            Theta = Theta + m.Upsilon.T.dot(m.Q_tilde).dot(m.Psi).dot(d_pred)

        # Form the time varying linear objective vector f
        # Include slack variables only if soft constraints are used
        if ctr.has_soft_constraints:
            f = np.hstack([Theta, np.zeros(m.R_size * ctr.Np)])
        else:
            f = Theta

        # Form the time varying linear inequality constraint vector b
        b_QP = np.ones(6 * ctr.Np)
        if ctr.has_soft_constraints:
            if d_pred is not None:
                b_QP = np.hstack([
                    b_QP, m.Delta - m.Pi.dot(
                        m.Gamma_constraints.dot(x) +
                        m.Psi_constraints.dot(d_pred))
                ])
            else:
                b_QP = np.hstack(
                    [b_QP, m.Delta - m.Pi.dot(m.Gamma_constraints.dot(x))])

        # Solve the QP
        opt_sol = solve_qp(m.H_tilde, f, m.A_QP, b_QP, solver='daqp')

        # Return the first three elements of the optimal solution, which correspond to the control
        # action at the current time step
        return opt_sol[0:3]
