"""
Solvers for model predictive control (MPC) algorithms.

"""

from soft4pes.control.mpc.solvers.indirect_mpc_qp import iMPCQP
from soft4pes.control.mpc.solvers.branch_and_bound import BranchAndBound
from soft4pes.control.mpc.solvers.enumeration import Enumeration
from soft4pes.control.mpc.solvers.gp3c import GP3C

from soft4pes.control.mpc.solvers.utils import (
    switching_constraint_violated,
    squared_weighted_second_norm,
    make_QP_matrices,
    make_Gamma,
    make_Upsilon,
)

__all__ = [
    'iMPCQP',
    'BranchAndBound',
    'Enumeration',
    'GP3C',
    'switching_constraint_violated',
    'squared_weighted_second_norm',
    'make_QP_matrices',
    'make_Gamma',
    'make_Upsilon',
]
