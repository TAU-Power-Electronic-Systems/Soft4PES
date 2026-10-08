"""Runner for grid-forming control simulations."""

from types import SimpleNamespace

import numpy as np

from soft4pes.control import (
    common,
    lin,
    mpc,
    modulation,
)

from soft4pes.sim import Simulation
from soft4pes.utils import Sequence

try:
    from ..builders.grid_system_builder import GridSystemBuilder
except ImportError:  # pragma: no cover - direct script execution fallback
    from builders.grid_system_builder import GridSystemBuilder


class GridFormingRunner:
    """Runner for grid-forming control simulations."""

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

        V_ref = Sequence(
            np.array(self.references.V.times),
            np.array(self.references.V.values),
        )

        return SimpleNamespace(
            P_ref_seq=P_ref,
            V_ref_seq=V_ref,
        )

    # ==================================================
    # Run
    # ==================================================

    def run(self):

        config = self.config

        # Grid-forming example requires LCL
        if config.filter_type != "LCL Filter":

            raise ValueError("Grid-forming control currently "
                             "requires an LCL filter.")

        system = GridSystemBuilder.build(config)

        sys = system.sys

        references = self.create_references()

        # ==================================================
        # RFPSC
        # ==================================================

        rfpsc = lin.RFPSC(sys=sys)

        # ==================================================
        # Grid-forming MPC
        # ==================================================

        if config.controller_type == "Grid Forming - MPC":

            solver = mpc.solvers.iMPCQP()

            vc_controller = (mpc.algorithms.LCLGridVcCtr(
                solver=solver,
                lambda_u=config.lambda_u,
                Np=config.Np,
                I_conv_max=config.I_conv_max,
            ))

            control_loops = [
                rfpsc,
                vc_controller,
            ]

        # ==================================================
        # Grid-forming cascade
        # ==================================================

        elif config.controller_type == "Grid Forming - Cascade":

            current_controller = lin.LCLConvCurrCtr(sys=sys)

            voltage_controller = (lin.LCLVcCtr(
                sys=sys,
                I_conv_max=config.I_conv_max,
                curr_ctr=current_controller,
            ))

            control_loops = [
                rfpsc,
                voltage_controller,
                current_controller,
            ]

        else:

            raise ValueError("Invalid grid-forming controller.")

        # ==================================================
        # Control system
        # ==================================================

        Ts = 1.0 / config.fs_control

        ctr_sys = common.ControlSystem(
            control_loops=control_loops,
            ref_seq=references,
            Ts=Ts,
            pwm=modulation.CarrierPWM(),
            common_mode_inj=modulation.CommonModeInjection(mode="MinMax"),
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
            "V_ref_seq": references.V_ref_seq,
            "controller": "Grid Forming",
            "filter_type": config.filter_type,
        }
