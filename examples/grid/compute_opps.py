"""
Example of offline optimal pulse pattern (OPP) computation.

This script computes optimal pulse patterns (OPPs) for the selected system configuration
and stores the resulting switching-angle lookup table in a MATLAB .mat file.
"""

import multiprocessing as mp

from soft4pes.control.modulation import OPP
from examples.grid.pars.grid_config import get_default_system

if __name__ == "__main__":

    # Required for multiprocessing on Windows.
    mp.freeze_support()

    # --------------------------------------------------------------
    # System configuration
    # --------------------------------------------------------------

    config = get_default_system(
        name="Strong_LV_Grid_LCL_Filter_2L_conv_2"
   )

    sys = config.sys

    # --------------------------------------------------------------
    # OPP solver configuration
    # --------------------------------------------------------------

    opp = OPP(
        sys=sys,
        d=5,
        level=1,
        sys_ind=1,
        hws=0,
        n_m=256,
        n_ini_points=500,
        max_harmonics=500,
        include_zero_modulation=False,
    )

    # --------------------------------------------------------------
    # Compute OPPs
    # --------------------------------------------------------------

    opp.compute(use_parallel=True)

    # --------------------------------------------------------------
    # Save results
    # --------------------------------------------------------------

    opp.save_results()