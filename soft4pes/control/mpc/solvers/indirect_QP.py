"""
This module contains the class IndirectQP, which is used to solve the indirect model predictive 
control (MPC) problem using a quadratic program (QP) solver. 

The formulation of the control problem and the QP matrices are based on:
M. Rossi, P. Karamanakos, and F. Castelli-Dezza, “An indirect model predictive control method for
grid-connected three-level neutral point clamped converters with LCL filters,” IEEE Trans. Ind.
Applicat., vol. 58, no. 3, pp. 3750-3768, May/Jun. 2022. The same states do not have to be both
controlled (output variables) and constrained.

The QP is solved using the `qpsolvers` package and the `DAQP` solver (MIT license).
"""

import numpy as np
from qpsolvers import solve_qp
from soft4pes.control.mpc.solvers.base_solver import BaseMpcSolver
from soft4pes.control.mpc.solvers.utils import make_QP_matrices


class IndirectQP(BaseMpcSolver):
    """
    QP solver for indirect MPC.
    
    This solver reformulates the MPC problem as a quadratic program with linear constraints, solving
    it at each time step to find the optimal control action. 

    Attributes
    ----------
    QP_matrices : SimpleNamespace
        Namespace containing the precomputed matrices used in the QP problem.
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
        u_abc : 1 x 3 ndarray of floats
            Optimal three-phase modulating signal for the current time step.
        """

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
        U_tilde = solve_qp(m.H_tilde, f, m.A_QP, b_QP, solver='daqp')

        # Return the first three elements of the optimal solution, which correspond to the control
        # action at the current time step
        return U_tilde[0:3]
