"""Utility functions for MPC solvers."""

import numpy as np
from types import SimpleNamespace


def switching_constraint_violated(nl, u_abc, u_km1_abc):
    """
    Check if a candidate three-phase switch position violates a switching constraint. 
    A three-level converter is not allowed to directly switch from -1 and 1 (and vice versa) 
    on one phase. 

    Parameters
    ----------
    nl : int
        Number of converter voltage levels.
    u_abc : 1 x 3 ndarray of ints
        three-phase switch position.
    u_km1_abc : 1 x 3 ndarray of ints
        Previously applied three-phase switch position.

    Returns
    -------
    bool
        Constraint violated.
    """

    if nl == 2:
        return False
    elif nl == 3:
        return np.linalg.norm(uk_abc - u_km1_abc, np.inf) >= 2
    else:
        raise ValueError('Only two- and three-level converters are supported.')


def squared_weighted_second_norm(vector, Q):
    """
    Compute the squared weighted second norm of a vector. The elements of the norm are weighted by 
    the weighting matrix Q, i.e. sqrt(x.T * Q * x)^2 = x.T * Q * x.
    
    Parameters
    ----------
    vector : ndarray
        Vector.
    Q : ndarray
        Weighting matrix.

    Returns
    -------
    float
        Squared weighted second norm.
    """

    return np.dot(vector.T, Q).dot(vector)


def make_QP_matrices(sys, ctr):
    """
    Create the QP matrices.

    Parameters
    ----------
    sys : system object
        System model.
    ctr : controller object
        Controller object.

    Returns
    -------
    SimpleNamespace
        Namespace containing the QP matrices.
    """

    model = ctr.state_space
    A_QP = model.A
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

    Gamma = make_Gamma(Np, C, A_QP)
    Gamma_constraints = make_Gamma(Np, ctr.C_constr, A_QP)

    # If the system is a grid-connected converter, take into account the grid voltage that has
    # been modelled as a disturbance. Note that contrary to the reference paper, the constraints
    # are handled separately of the output variables.
    if hasattr(model, 'B1'):
        B1 = model.B1
        B2 = model.B2
        Upsilon = make_Upsilon(Np, C, A_QP, B1)
        Upsilon_constraints = make_Upsilon(Np, ctr.C_constr, A_QP, B1)
        Psi = make_Upsilon(Np, C, A_QP, B2)
    else:
        B = model.B
        Upsilon = make_Upsilon(Np, C, A_QP, B)
        Upsilon_constraints = make_Upsilon(Np, ctr.C_constr, A_QP, B)
        Psi = None

    # Form the quadric objective matrix H_tilde
    H = Upsilon.T.dot(Q_tilde).dot(Upsilon) + lambda_u * S.T.dot(S)
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

    V = np.array(
        [[1, 0, 0, -1, 0, 0],\
            [0, 1, 0, 0, -1, 0],\
            [0, 0, 1, 0, 0, -1]]).T

    Omega = np.kron(np.eye(Np), V)

    # Form the linear inequality constraint matrix A_QP
    A_QP = np.block([[Omega, np.zeros((6 * Np, R_size * Np))],
                     [np.dot(Pi, Upsilon_constraints), Z]])

    return SimpleNamespace(R_size=R_size,
                           Gamma=Gamma,
                           Gamma_constraints=Gamma_constraints,
                           Upsilon=Upsilon,
                           S=S,
                           E=E,
                           H_tilde=H_tilde,
                           Q_tilde=Q_tilde,
                           Delta=Delta,
                           Pi=Pi,
                           A_QP=A_QP,
                           Psi=Psi)


def make_Gamma(Np, C, A):
    """
    Make Gamma matrix for the QP.

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
        Gamma[Gamma_row_index] = np.dot(C, np.linalg.matrix_power(A, i + 1))
    return Gamma


def make_Upsilon(Np, C, A, B):
    """
    Make Upsilon matrix for the QP.

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
        Upsilon matrix.
    """
    Upsilon = np.zeros((Np * C.shape[0], Np * B.shape[1]))
    Upsilon_row = np.zeros((C.shape[0], Np * B.shape[1]))
    for i in range(Np):
        Upsilon_row = np.roll(Upsilon_row, B.shape[1], axis=1)
        Upsilon_row[:, :B.shape[1]] = C.dot(np.linalg.matrix_power(A,
                                                                   i)).dot(B)
        Upsilon_row_index = range(i * C.shape[0], (i + 1) * C.shape[0])
        Upsilon[Upsilon_row_index] = Upsilon_row
    return Upsilon
