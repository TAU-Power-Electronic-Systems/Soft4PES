"""Sphere decoder based solver for model-predictive control"""

from types import SimpleNamespace
import numpy as np


class MpcSpheDec:
    """
    Sphere decoder based solver for model-predictive control

    Attributes
    ----------
    Q : ndarray of floats
        Weights for reference tracking.
    U_km1 : 3*Np x 1 ndarray of ints
        Previous 3-phase switch position sequence.
    matrices : SimpleNamespace
        Matrices for the sphere-decoder algorithm.
    initialized : bool
        Initialization flag for the matrices.
    """

    def __init__(self, Q):
        """
        Initialize a MpcSpheDec instance.

        Parameters
        ----------
        Q : ndarray of floats
            Weights for reference tracking.
        """
        self.Q = Q
        self.U_km1 = None
        self.matrices = None
        self.initialized = False

    def __call__(self, sys, conv, ctr, y_ref):
        """
        Solve MPC problem by using sphere decoder.

        Parameters
        ----------
        sys : object
            System object.
        conv : object
            Converter object.
        ctr : object
            Controller object.
        y_ref : _ x 2 ndarray of floats
            Reference vector [p.u.].

        Returns
        -------
        uk : 1 x 3 ndarray of ints
            The 3-phase switch position with the lowest cost.
        """

        if not self.initialized:
            self.matrices = self.make_problem_matrices(sys, conv, ctr)
            self.U_km1 = np.zeros(3 * ctr.Np)
            self.initialized = True

        Y_ref = y_ref.flatten()
        Gamma = self.matrices.Gamma
        Ypsilon = self.matrices.Ypsilon
        Q_tilde = self.matrices.Q_tilde
        S = self.matrices.S
        E = self.matrices.E
        lambda_u = ctr.lambda_u
        Hinv = self.matrices.Hinv
        V = self.matrices.V

        Theta = -Ypsilon.T.dot(Q_tilde).dot(Y_ref - Gamma.dot(
            sys.x)) - lambda_u * S.T.dot(E.dot(self.U_km1[:3]))

        # If grid voltage is modelled as a disturbance
        if hasattr(self.matrices, 'Psi'):

            # Create the grid voltage vector
            Ts_pu = ctr.Ts * sys.base.w
            delta_theta = sys.wg * Ts_pu
            R_vg = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                            [np.sin(delta_theta), np.cos(delta_theta)]])

            Vg = np.zeros((ctr.Np * 2))
            Vg[0:2] = ctr.vg
            for k in range(2, ctr.Np * 2, 2):
                Vg[k:k + 2] = np.dot(R_vg, Vg[k - 2:k])

            Theta = Theta + Ypsilon.T.dot(self.matrices.Psi).dot(Vg)

        # Unconstrained solution and its projection to V space
        U_unc = -Hinv.dot(Theta)
        U_bar_unc = V.dot(U_unc)

        # Initial solution and its projection to V space. The initial solution
        # is based on the previous 3-phase switch position sequence.
        U_ini = np.concatenate((self.U_km1[3:], self.U_km1[-3:]))
        U_bar_ini = V.dot(U_ini)

        # Euclidian distance between the unconstrained and initial solution
        # Add small value to avoid numerical issues
        rho = np.linalg.norm(U_bar_unc - U_bar_ini)**2 * (1 + 1e-9)

        # Perform sphere decoding
        U_opt = np.zeros(3 * ctr.Np)
        dist = 0
        i = 0
        _, U, _ = self.sphe_dec(conv, ctr, U_ini, U_opt, dist, i, rho,
                                U_bar_unc, self.U_km1)
        self.U_km1 = U
        uk = U[0:3]

        return uk

    def sphe_dec(self, conv, ctr, U, U_opt, dist, i, rho, U_bar_unc, u_km1):
        """
        Perform sphere decoding as a recursive algorithm.

        Parameters
        ----------
        conv : object
            Converter object.
        ctr : object
            Control object.
        U : 1 x 3*Np ndarray of ints
            3-phase switch position sequence being optimized.
        U_opt : 1 x 3*Np ndarray of ints
            3-phase switch position sequence with the lowest cost.
        dist : float
            Current distance to unconstrained optimal solution.
        i : int
            Index.
        rho : float
            Minimum distance to unconstrained optimal solution.
        U_bar_unc : 1 x 3*Np ndarray of floats
            Unconstrained optimal solution.
        u_km1 : 1 x 3 ndarray
            Previosuly applied 3-phase switch position.

        Returns
        -------
        U : 1 x 3*Np ndarray of ints
            3-phase switch position sequence being optimized.
        U_opt : 1 x 3*Np ndarray of ints
            3-phase switch position sequence with the lowest cost.
        rho : float
            Minimum distance to unconstrained optimal solution.
        """

        if i < 3:
            u_old = u_km1[i]
        else:
            u_old = U[i - 3]

        for u in self.get_allowed_switch_positions(conv, u_old):
            U[i] = u
            d = (U_bar_unc[i] -
                 self.matrices.V[i, :i + 1].dot(U[:i + 1]))**2 + dist

            if d <= rho:
                if i < 3 * ctr.Np - 1:
                    U, U_opt, rho = self.sphe_dec(conv, ctr, U, U_opt, d,
                                                  i + 1, rho, U_bar_unc, u_km1)
                else:
                    U_opt = np.copy(U)
                    rho = d

        return U, U_opt, rho

    def make_problem_matrices(self, sys, conv, ctr):
        """
        Make matrices for the sphere-decoder algorithm.

        Parameters
        ----------
        sys : object
            System object.
        conv : object
            Converter object.
        ctr : object
            Control object.

        Returns
        -------
        SimpleNamespace
            Matrices for the sphere-decoder algorithm.
        """

        model = sys.get_discrete_state_space(conv.v_dc, ctr.Ts)
        Np = ctr.Np
        lambda_u = ctr.lambda_u

        Q_tilde = np.kron(np.eye(Np), self.Q)
        S = np.kron(np.eye(Np), np.eye(3)) - np.block(
            [[np.zeros((3, 3 * Np))],
             [np.kron(np.eye(Np - 1), np.eye(3)),
              np.zeros(((Np - 1) * 3, 3))]])

        E = np.block([[np.eye(3)], [np.zeros(((Np - 1) * 3, 3))]])

        A = model.A
        C = ctr.C

        Gamma = self.make_Gamma(Np, C, A)

        matrices = SimpleNamespace(
            Gamma=Gamma,
            Q_tilde=Q_tilde,
            S=S,
            E=E,
        )

        # Chek if the system is a induction machine or a grid with
        # grid voltage modelled as a disturbance
        if hasattr(model, 'B'):  # Machine
            B = model.B
            Ypsilon = self.make_Ypsilon(Np, C, A, B)

        elif hasattr(model, 'B1'):  # Grid
            B1 = model.B1
            B2 = model.B2
            Ypsilon = self.make_Ypsilon(Np, C, A, B1)
            Psi = self.make_Ypsilon(Np, C, A, B2)
            matrices.Psi = Psi

        H = Ypsilon.T.dot(Q_tilde).dot(Ypsilon) + lambda_u * S.T.dot(S)
        Hinv = np.linalg.inv(H)
        V = np.linalg.inv(np.linalg.cholesky(Hinv))
        matrices.Ypsilon = Ypsilon
        matrices.H = H
        matrices.Hinv = Hinv
        matrices.V = V

        return matrices

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

    def get_allowed_switch_positions(self, conv, u_km1):
        """
        Get allowed 1-phase switch positions based on the previously applied position. 
        A three-level converter is not allowed to change directly between positions -1 and 1. 

        Parameters
        ----------
        u_km1 : int
            Previously applied 1-phase switch position.

        Returns
        -------
        1 x n ndarray of ints (n is the number of allowed switch positions)
            Allowed 1-phase switch positions.
        """

        if conv.nl == 2:
            res = np.array([-1, 1])

        elif conv.nl == 3:
            if u_km1 == -1:
                res = np.array([-1, 0])
            elif u_km1 == 0:
                res = np.array([-1, 0, 1])
            elif u_km1 == 1:
                res = np.array([0, 1])

        return res
