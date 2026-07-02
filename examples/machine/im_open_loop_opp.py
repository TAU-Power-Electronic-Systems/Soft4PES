"""
Example of open-loop control for IM with OPPs
"""

from types import SimpleNamespace
import numpy as np

from pars.machine_config import get_custom_system
from soft4pes import model
from soft4pes.control import common, opp, lin
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define torque reference sequence and stator flux magnitude reference sequence using sequence
# objects. The first array contains the time instants (in seconds) and the second array the
# corresponding reference values (in per unit). The reference is interpolated linearly between the
# time instants.
T_ref_seq = Sequence(
    np.array([0, 0.2]),
    np.array([1, 1]),
)

psiS_mag_ref_seq = Sequence(
    np.array([0, 0.2]),
    np.array([1, 1]),
)

ref_seq = SimpleNamespace(T_ref_seq=T_ref_seq,
                          psiS_mag_ref_seq=psiS_mag_ref_seq)

# Get the system parameters from the ready made components. All the available components and systems
# are defined in the examples/machine/pars/machine_parameter_sets.json file, and given in the
# documentation. Here, a 3-level converter connected to medium voltage induction machine is used.
config = get_custom_system(machine_name='MV_Induction_Machine',
                           converter_name='3L_MV_Converter')

# Create the system model consisting of the induction machine and converter. The initial stator flux
# magnitude reference and torque reference are passed to the IM model to set the initial
# state. Moreover, a sequence object is passed to the IM model to define the time-varying rotor
# speed.
sys = model.machine.InductionMachine(
    par=config.machine_params,
    conv=config.conv,
    base=config.base,
    psiS_mag_ref_init=psiS_mag_ref_seq(0),
    T_ref_init=T_ref_seq(0),
)

# Define the control loops
im_ws_est = lin.IMwsEstimator(sys=sys)
iS_ref_gen = lin.IMStatorCurrRefGen()
ctr = opp.IMOpenLoopOPP(sys=sys, d=6, opp_file='3L_d6_opp_inductive.nc')

# Instantiate the controller
ctr_sys = common.ControlSystem(control_loops=[im_ws_est, iS_ref_gen, ctr],
                               ref_seq=ref_seq,
                               Ts=50e-6)

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
                    frames=['abc', 'abc'],
                    plot_u_abc=True)
plotter.plot_control_signals_machine(plot_T=True, T_ref=T_ref_seq)
plotter.plot_spectra(states_to_plot=['iS'],
                     f_fund_SI=config.base.w / (2 * np.pi),
                     f_max_SI_plot=2500,
                     start_time=0.1,
                     n_cycles=1,
                     style='bar')
plotter.show_all()
