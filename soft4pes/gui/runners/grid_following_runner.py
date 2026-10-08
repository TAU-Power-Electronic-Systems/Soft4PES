"""Grid-following runner for the Soft4PES GUI."""

from types import SimpleNamespace

import numpy as np

from soft4pes.control import (
    common,
    lin,
    modulation,
)

from soft4pes.sim import Simulation
from soft4pes.utils import Sequence

try:
    from ..builders.grid_system_builder import GridSystemBuilder
except ImportError:  # pragma: no cover - direct script execution fallback
    from builders.grid_system_builder import GridSystemBuilder


class GridFollowingRunner:
    """Runner for grid-following control simulations."""

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

        system = GridSystemBuilder.build(config)

        sys = system.sys

        references = self.create_references()

        # ==================================================
        # PLL
        # ==================================================

        pll = (lin.PLL(sys=sys) if config.filter_type == "LCL Filter" else
               lin.PLL(sys=sys, zeta=1, wn=2 * np.pi * 5))

        # ==================================================
        # Current reference
        # ==================================================

        current_reference = lin.GridCurrRefGen()

        # ==================================================
        # Current controller
        # ==================================================

        if config.filter_type == "L Filter":

            current_controller = lin.LConvCurrCtr(sys=sys)

        elif config.filter_type == "LCL Filter":

            current_controller = lin.LCLGridCurrCtrWACFB(sys=sys)

        else:

            raise ValueError("Unsupported filter.")

        # ==================================================
        # Controller system
        # ==================================================

        Ts = 1.0 / config.fs_control

        control_loops = [
            pll,
            current_reference,
            current_controller,
        ]

        ctr_sys = common.ControlSystem(
            control_loops=control_loops,
            ref_seq=references,
            Ts=Ts,
            pwm=modulation.CarrierPWM(),
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

        # ==================================================
        # Results
        # ==================================================

        return {
            "sim_data": sim_data,
            "sys": sys,
            "base": system.base,
            "P_ref_seq": references.P_ref_seq,
            "Q_ref_seq": references.Q_ref_seq,
            "controller": "Grid Following",
            "filter_type": config.filter_type,
        }
