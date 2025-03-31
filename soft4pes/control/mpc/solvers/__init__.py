"""
Solvers for model predictive control (MPC) algorithms.

"""

from soft4pes.control.mpc.solvers.mpc_QP import IndirectMpcQP
from soft4pes.control.mpc.solvers.mpc_bnb import MpcBnB
from soft4pes.control.mpc.solvers.mpc_enum import MpcEnum
from soft4pes.control.mpc.solvers.utils import (
    switching_constraint_violated,
    squared_weighted_second_norm,
    make_QP_matrices,
    make_Gamma,
    make_Upsilon,
)

__all__ = [
    'IndirectMpcQP',
    'MpcBnB',
    'MpcEnum',
    'switching_constraint_violated',
    'squared_weighted_second_norm',
    'make_QP_matrices',
    'make_Gamma',
    'make_Upsilon',
]
