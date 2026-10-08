"""Simulation configuration for Soft4PES GUI."""

from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Container for the simulation configuration of Soft4PES GUI."""

    # ==================================================
    # Grid
    # ==================================================

    Vg: float
    Ig: float
    fg: float

    Rg: float
    Lg: float

    # ==================================================
    # Filter
    # ==================================================

    filter_type: str

    Lfc: float
    Rfc: float

    Cf: float = 0.0
    Rc: float = 0.0

    Lfg: float = 0.0
    Rfg: float = 0.0

    # ==================================================
    # Converter
    # ==================================================

    Vdc: float = 750.0
    converter_levels: int = 2

    # ==================================================
    # Controller
    # ==================================================

    controller_type: str = "Grid Following - Linear"

    fs_control: float = 10000.0

    # MPC
    Np: int = 2
    lambda_u: float = 5e-3
    I_conv_max: float = 1.3

    # ==================================================
    # Simulation
    # ==================================================

    Ts_sim: float = 1e-6
    t_stop: float = 0.3
