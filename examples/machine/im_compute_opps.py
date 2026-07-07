"""
Example of offline optimal pulse pattern (OPP) computation.

This example computes OPPs for the selected converter-machine system and stores
the resulting switching-angle and switch-position lookup tables in a NetCDF file.
"""

from examples.machine.pars.machine_config import get_custom_system
from soft4pes import model
from soft4pes.control.modulation import OPPComputation


if __name__ == "__main__":

    # Create the system from predefined machine and converter components.
    config = get_custom_system(
        machine_name="MV_Induction_Machine",
        converter_name="3L_MV_Converter",
    )

    sys = model.machine.InductionMachine(
        par=config.machine_params,
        conv=config.conv,
        base=config.base,
        psiS_mag_ref=1,
        T_ref_init=1,
    )

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