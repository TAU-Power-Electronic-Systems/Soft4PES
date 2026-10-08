"""Direct MPC runner."""

from types import SimpleNamespace

import numpy as np

from soft4pes.control import (
    common,
    lin,
    mpc,
)

from soft4pes.sim import Simulation
from soft4pes.utils import Sequence

try:
    from ..builders.grid_system_builder import GridSystemBuilder
except ImportError:  # pragma: no cover - direct script execution fallback
    from builders.grid_system_builder import GridSystemBuilder


class DirectMPCRunner:
    """Runner for direct MPC simulations."""

    def __init__(
        self,
        config,
        references,
    ):

        self.config = config
        self.references = references

    # ==================================================
    # References
    # ==================================================

    def create_references(self):

        P_ref = Sequence(
            np.array(self.references.P.times),
            np.array(self.references.P.values),
        )

        Q_ref = Sequence(
            np.array(self.references.Q.times),
            np.array(self.references.Q.values),
        )

        return SimpleNamespace(
            P_ref_seq=P_ref,
            Q_ref_seq=Q_ref,
        )

    # ==================================================
    # Run
    # ==================================================

    def run(self):

        config = self.config

        # Direct MPC example uses L filter
        if config.filter_type != "L Filter":

            raise ValueError("Direct grid-current MPC currently "
                             "supports the L filter.")

        system = GridSystemBuilder.build(config)

        sys = system.sys

        references = self.create_references()

        # ==================================================
        # Reference generator
        # ==================================================

        reference_controller = lin.GridCurrRefGen()

        # ==================================================
        # Branch-and-Bound solver
        # ==================================================

        solver = mpc.solvers.BranchAndBound()

        # ==================================================
        # Direct MPC
        # ==================================================

        controller = (mpc.algorithms.RLGridCurrCtr(
            solver=solver,
            lambda_u=config.lambda_u,
            Np=config.Np,
        ))

        # ==================================================
        # Control system
        # ==================================================

        Ts = 1.0 / config.fs_control

        ctr_sys = common.ControlSystem(
            control_loops=[
                reference_controller,
                controller,
            ],
            ref_seq=references,
            Ts=Ts,
        )

        # ==================================================
        # Simulation
        # ==================================================

        sim = Simulation(
            sys=sys,
            ctr=ctr_sys,
            Ts_sim=config.Ts_sim,
        )

        sim_data = sim.simulate(t_stop=config.t_stop)

        return {
            "sim_data": sim_data,
            "sys": sys,
            "base": system.base,
            "P_ref_seq": references.P_ref_seq,
            "Q_ref_seq": references.Q_ref_seq,
            "controller": "Direct MPC",
            "filter_type": config.filter_type,
        }
