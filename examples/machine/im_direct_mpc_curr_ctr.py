"""
Example of direct model predictive control (MPC) for an induction machine drive system. The 
controller aims to track the stator current reference calculated based on the reference values of 
the stator flux magnitude and torque. The machine operates at a constant (nominal) speed.
"""

from types import SimpleNamespace
import numpy as np

from pars.machine_config import get_custom_system
from soft4pes import model
from soft4pes.control import mpc, common
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define torque reference sequence using a sequence object
# The first array contains the time instants (in seconds) and the second array the corresponding
# reference values (in per unit). The reference is interpolated linearly between the time instants.
T_ref_seq = Sequence(
    np.array([0, 0.05, 0.05, 0.15, 0.15, 0.2]),
    np.array([0, 0, 1, 1, 0.5, 0.5]),
)
ref_seq = SimpleNamespace(T_ref_seq=T_ref_seq)

# Get the system parameters from the ready made components. All the available components and systems
# are defined in the examples/machine/pars/machine_parameter_sets.json file, and given in the
# documentation. Here, a 2-level converter connected to low voltage induction machine is used.
config = get_custom_system(machine_name='LV_Induction_Machine',
                           converter_name='2L_LV_Converter')

# Create the system model consisting of the induction machine and converter. The stator flux
# magnitude reference and initial torque reference are passed to the IM model to set the initial
# state.
sys = model.machine.InductionMachine(
    par=config.machine_params,
    conv=config.conv,
    base=config.base,
    psiS_mag_ref=1,
    T_ref_init=T_ref_seq(0),
)

# Use Branch-and-Bound solver
solver = mpc.solvers.MpcBnB(conv=config.conv)

# Uncomment to use enumeration based solver
# solver = mpc.solvers.MpcEnum(conv=config.conv)

# Define the indirect MPC current controller, which tracks the stator current references, derived
# from the stator flux magnitude and torque references.
ctr = mpc.controllers.IMMpcCurrCtr(solver=solver,
                                   lambda_u=10e-3,
                                   Np=2,
                                   disc_method='exact_discretization')
ctr_sys = common.ControlSystem(control_loops=[ctr], ref_seq=ref_seq, Ts=50e-6)

# Simulate the system
sim = Simulation(sys=sys,
                 ctr=ctr_sys,
                 Ts_sim=5e-6,
                 disc_method='exact_discretization')
sim_data = sim.simulate(t_stop=0.2)

# Save the simulation data to a .mat file
sim.save_data()

# Plot the results
plotter = Plotter(data=sim_data, sys=sys)
plotter.plot_states(states_to_plot=['iS', 'psiR'],
                    frames=['dq', 'abc'],
                    plot_u_abc=True)
plotter.plot_control_signals_machine(plot_T=True, T_ref=T_ref_seq)
plotter.show_all()
