"""
This module contains the class MpcQP, which is used to solve the MPC problem using a quadratic 
program (QP) solver. 

The formulation of the control problem and the QP matrices are based on "M. Rossi, P. Karamanakos, 
and F. Castelli-Dezza, “An indirect model predictive control method for grid-connected three-level 
neutral point clamped converters with LCL filters,” IEEE Trans. Ind. Applicat., vol. 58, no. 3, pp. 
3750-3768, May/Jun. 2022". Note, that contrary to the reference, the grid voltage is modelled as a 
disturbance. Moreover, the same states do not have to be both controlled (i.e., be output variables)
and constrained.

The QP is solved using the qpsolvers package and the solver 'DAQP', licensed under the MIT 
license.
"""

import numpy as np
from qpsolvers import solve_qp
from soft4pes.control.mpc.solvers.utils import make_QP_matrices


class IndirectMpcQP:
    """
    Problem formulation and QP solver for indirect MPC. 

    Attributes
    ----------
    QP_matrices : SimpleNamespace
        Namespace containing the matrices used in the QP problem.
    """

    def __init__(self):
        self.QP_matrices = None

    def __call__(self, sys, conv, ctr, y_ref):
        """
        Formulate and solve the MPC QP.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        ctr : controller object
            Controller object.
        y_ref : ndarray of floats
            Reference vector [p.u.].

        Returns
        -------
        uk_abc : 1 x 3 ndarray of floats
            The three-phase modulating signal.
        """

        if self.QP_matrices is None:
            self.QP_matrices = make_QP_matrices(sys, conv, ctr)

        m = self.QP_matrices

        # Reshape the vectors to be row vectors
        x = sys.x.reshape(-1, 1)
        y_ref = y_ref[1:].flatten().reshape(-1, 1)
        u_km1 = ctr.u_km1_abc.reshape(-1, 1)

        # Formulate the time varying matrice Theta
        Theta = -m.Upsilon.T.dot(m.Q_tilde).dot(
            y_ref - m.Gamma.dot(x)) - ctr.lambda_u * m.S.T.dot(m.E).dot(u_km1)

        # If the system is a grid-connected converter, predict the grid voltage. This formulation of
        # Theta differs from the reference, as the grid voltage is modelled here as a disturbance.
        if m.Psi is not None:
            Ts_pu = ctr.Ts * sys.base.w
            delta_theta = sys.par.wg * Ts_pu
            R_vg = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                            [np.sin(delta_theta), np.cos(delta_theta)]])

            Vg = np.zeros((ctr.Np * 2, 1))
            Vg[0:2] = ctr.vg.reshape(-1, 1)
            for k in range(2, ctr.Np * 2, 2):
                Vg[k:k + 2] = np.dot(R_vg, Vg[k - 2:k])

            Theta = Theta + m.Upsilon.T.dot(m.Psi).dot(Vg)

        # Form the time varying linear objective vector d
        d = np.vstack([Theta, np.zeros((m.R_size * ctr.Np, 1))])

        # Form the time varying linear inequality constraint vector
        b_QP = np.vstack([
            np.ones((6 * ctr.Np, 1)),
            m.Delta - m.Pi.dot(m.Gamma_constraints).dot(x)
        ])

        # Solve the QP and return the solution to the controller
        U_tilde = solve_qp(m.H_tilde, d, m.A_QP, b_QP, solver='daqp')

        return U_tilde[0:3]
