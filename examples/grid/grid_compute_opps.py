"""
Example of offline optimal pulse pattern (OPP) computation.

This example computes OPPs for the selected grid-connected system and stores the
resulting switching-angle and switch-position lookup tables in a NetCDF file.
"""

from examples.grid.pars.grid_config import get_custom_system
from soft4pes.control.modulation import OPPComputation


if __name__ == "__main__":

    # Create the system from predefined grid, filter, and converter components.
    config = get_custom_system(
        grid_name="Strong_LV_Grid",
        filter_name="LCL_Filter_fr_1300",
        converter_name="3L_LV_Converter",
    )

    sys = config.sys

    # Define the OPP problem.
    opp = OPPComputation(
        sys=sys,
        d=5,
        symmetry="QaHWS",
        n_m=256,
        n_ini_points=10,
        max_harmonics=500,
    )

    # Compute the OPPs using parallel evaluation of the multistart initial points.
    opp.compute(use_parallel=True)

    # Save the lookup table.
    opp.save_results()