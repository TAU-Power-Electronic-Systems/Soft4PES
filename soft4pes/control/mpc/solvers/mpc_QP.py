"""
This module contains the class MpcQP, which is used to solve the MPC problem using a quadratic 
program (QP) solver. 

The formulation of the control problem and the QP matrices are based on "M. Rossi, P. Karamanakos, 
and F. Castelli-Dezza, “An indirect model predictive control method for grid-connected three-level 
neutral point clamped converters with LCL filters,” IEEE Trans. Ind. Applicat., vol. 58, no. 3, pp. 
3750-3768, May/Jun. 2022". Note, that contrary to the reference, the grid voltage is modelled as a 
disturbance. Moreover, the same states do not have to be both tracked and limited.

The QP is solved using the qpsolvers package and the solver 'DAQP', licensed under the MIT 
license.
"""

import numpy as np
from types import SimpleNamespace
from qpsolvers import solve_qp


class MpcQP:
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
            self.QP_matrices = self.make_QP_matrices(sys, conv, ctr)

        m = self.QP_matrices

        # Reshape the vectors to be row vectors
        x = sys.x.reshape(-1, 1)
        y_ref = y_ref[1:].flatten().reshape(-1, 1)
        u_km1 = ctr.u_km1_abc.reshape(-1, 1)

        # Calculate time varying matrices Theta_tilde and b for the QP
        Theta = -m.Ypsilon.T.dot(m.Q_tilde).dot(
            y_ref - m.Gamma.dot(x)) - ctr.lambda_u * m.S.T.dot(m.E).dot(u_km1)

        # If the system is a grid, predict the grid voltage
        if m.Psi is not None:
            Ts_pu = ctr.Ts * sys.base.w
            delta_theta = sys.par.wg * Ts_pu
            R_vg = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                            [np.sin(delta_theta), np.cos(delta_theta)]])

            Vg = np.zeros((ctr.Np * 2, 1))
            Vg[0:2] = ctr.vg.reshape(-1, 1)
            for k in range(2, ctr.Np * 2, 2):
                Vg[k:k + 2] = np.dot(R_vg, Vg[k - 2:k])

            Theta = Theta + m.Ypsilon.T.dot(m.Psi).dot(Vg)

        Theta_tilde = np.vstack([Theta, np.zeros((m.R_size * ctr.Np, 1))])

        b = np.vstack([
            np.ones((6 * ctr.Np, 1)),
            m.Delta - m.Pi.dot(m.Gamma_constraints).dot(x)
        ])

        # Solve the QP and return the solution to the controller
        U_tilde = solve_qp(m.H_tilde, Theta_tilde, m.A, b, solver='daqp')

        return U_tilde[0:3]

    def make_QP_matrices(self, sys, conv, ctr):
        """
        Create the QP matrices.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        ctr : controller object
            Controller object.

        Returns
        -------
        SimpleNamespace
            Namespace containing the QP matrices.
        """

        model = sys.get_discrete_state_space(conv.v_dc, ctr.Ts)
        A = model.A
        C = ctr.C

        Np = ctr.Np
        lambda_u = ctr.lambda_u
        R_size = np.size(ctr.R, 1)

        Q_tilde = np.kron(np.eye(Np), ctr.Q)
        R_tilde = np.kron(np.eye(Np), ctr.R)

        S = np.eye(3 * Np) - np.block([[np.zeros(
            (3, 3 * Np))], [np.eye(3 * (Np - 1)),
                            np.zeros((3 * (Np - 1), 3))]])
        E = np.block([[np.eye(3)], [np.zeros(((Np - 1) * 3, 3))]])

        Gamma = self.make_Gamma(Np, C, A)
        Gamma_constraints = self.make_Gamma(Np, ctr.C_lim, A)

        # If the system is a grid, take into account the grid voltage that has been modelled as a
        # disturbance
        if hasattr(model, 'B1'):
            B1 = model.B1
            B2 = model.B2
            Ypsilon = self.make_Ypsilon(Np, C, A, B1)
            Ypsilon_constraints = self.make_Ypsilon(Np, ctr.C_lim, A, B1)
            Psi = self.make_Ypsilon(Np, C, A, B2)
        else:
            B = model.B
            Ypsilon = self.make_Ypsilon(Np, C, A, B)
            Ypsilon_constraints = self.make_Ypsilon(Np, ctr.C_lim, A, B)
            Psi = None

        H = Ypsilon.T.dot(Q_tilde).dot(Ypsilon) + lambda_u * S.T.dot(S)
        H_tilde = np.block([[H, np.zeros((3 * Np, R_size * Np))],
                            [np.zeros((R_size * Np, 3 * Np)), R_tilde]])

        K_inv = np.array([[1, 0], [-1 / 2, np.sqrt(3) / 2],
                          [-1 / 2, -np.sqrt(3) / 2]])
        K_inv_tilde = np.kron(np.eye(R_size), K_inv)

        W = np.array([[1, -1, 0, 0, 0, 0, 0],\
                      [0, 0, 1, -1, 0, 0, 0],
                      [0, 0, 0, 0, 1, -1, 0]]).T
        W_tilde = np.kron(np.eye(R_size), W)

        N = np.kron(np.eye(R_size), np.block([[np.ones((6, 1))], [0]]))

        Nc = np.dot(N, ctr.c)

        M = np.kron(np.eye(R_size), np.ones((7, 1)))

        Z = np.kron(np.eye(Np), -M)

        Pi = np.kron(np.eye(Np), np.dot(W_tilde, K_inv_tilde))

        Delta = np.kron(np.ones((Np, 1)), Nc)

        V = (np.sqrt(3) / 2) * np.array(
            [[1, 0, 0, -1, 0, 0],\
             [0, 1, 0, 0, -1, 0],\
             [0, 0, 1, 0, 0, -1]]).T

        Omega = np.kron(np.eye(Np), V)

        A = np.block([[Omega, np.zeros((6 * Np, R_size * Np))],
                      [np.dot(Pi, Ypsilon_constraints), Z]])

        return SimpleNamespace(R_size=R_size,
                               Gamma=Gamma,
                               Gamma_constraints=Gamma_constraints,
                               Ypsilon=Ypsilon,
                               S=S,
                               E=E,
                               H_tilde=H_tilde,
                               Q_tilde=Q_tilde,
                               Delta=Delta,
                               Pi=Pi,
                               A=A,
                               Psi=Psi)

    def make_Gamma(self, Np, C, A):
        """
        Make Gamma matrix for the sphere-decoder algorithm.

        Parameters
        ----------
        Np : int
            Prediction horizon.
        C : ndarray
            Output matrix of the system.
        A : ndarray
            State matrix of the system.

        Returns
        -------
        ndarray
            Gamma matrix.
        """
        Gamma = np.zeros((Np * C.shape[0], A.shape[1]))
        for i in range(0, Np):
            Gamma_row_index = range(i * C.shape[0], (i + 1) * C.shape[0])
            Gamma[Gamma_row_index] = np.dot(C,
                                            np.linalg.matrix_power(A, i + 1))
        return Gamma

    def make_Ypsilon(self, Np, C, A, B):
        """
        Make Ypsilon matrix for the sphere-decoder algorithm.

        Parameters
        ----------
        Np : int
            Prediction horizon.
        C : ndarray
            Output matrix of the system.
        A : ndarray
            State matrix of the system.
        B : ndarray
            Input matrix of the system.

        Returns
        -------
        ndarray
            Ypsilon matrix.
        """
        Ypsilon = np.zeros((Np * C.shape[0], Np * B.shape[1]))
        Ypsilon_row = np.zeros((C.shape[0], Np * B.shape[1]))
        for i in range(Np):
            Ypsilon_row = np.roll(Ypsilon_row, B.shape[1], axis=1)
            Ypsilon_row[:, :B.shape[1]] = C.dot(np.linalg.matrix_power(
                A, i)).dot(B)
            Ypsilon_row_index = range(i * C.shape[0], (i + 1) * C.shape[0])
            Ypsilon[Ypsilon_row_index] = Ypsilon_row
        return Ypsilon
