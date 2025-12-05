"""
Example of direct model predictive control (MPC) for a permanent magnet synchronous machine (PMSM) 
drive system. The controller aims to track the stator current reference calculated based on the 
reference values of the maximum torque per ampere (MTPA) trajectory and torque. The machine operates
at a constant (nominal) speed.
"""

from types import SimpleNamespace
import numpy as np

from pars.machine_config import get_default_system
from soft4pes import model
from soft4pes.control import mpc, common
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define base values
base = model.machine.BaseMachine(Vm_R_SI=274,
                                 Im_R_SI=71,
                                 fm_R_SI=50,
                                 npp=4,
                                 pf=1)

# Define torque reference sequence
# The first array contains the time instants (in seconds) and the second array the corresponding
# reference values (in per unit). The reference is interpolated linearly between the time instants.
T_ref_seq = Sequence(
    times=np.array([0, 0.05, 0.05, 0.1, 0.1, 0.15]),
    values=np.array([0, 0, 0.5, 0.5, 1, 1]),
)
ref_seq = SimpleNamespace(T_ref_seq=T_ref_seq)

# Define converter parameters
conv = model.conv.Converter(v_dc_SI=750, nl=2, base=base)

# Define PMSM parameters
sm_params = model.machine.PMSMParameters(fs_SI=50,
                                         pf_SI=1,
                                         Rs_SI=0.3,
                                         Lsd_SI=4e-3,
                                         Lsq_SI=5.5e-3,
                                         LambdaPM_SI=0.7,
                                         base=base)

# Uncomment the following lines to use the ready made configuration. All the available components
# and systems are defined in the examples/machine/pars/machine_parameter_sets.json file, and given
# in the online documentation.
# config = get_default_system("LV_PMSM_2L_Converter")
# sm_params = config.machine_params
# conv = config.conv
# base = config.base

# Create a MTPA lookup table for current reference calculation
MPTA_lut = common.MTPALookupTable(par=sm_params)

# Define system models. The torque reference and the MTPA lookup table are passed to the PMSM model
# to set the initial state.
sys = model.machine.PMSM(par=sm_params,
                         conv=conv,
                         base=base,
                         T_ref_init=T_ref_seq(0),
                         mtpa_lut=MPTA_lut)

# Use Branch-and-Bound solver
solver = mpc.solvers.MpcBnB(conv=conv)

# Define current controller
ctr = mpc.controllers.PMSMMpcCurrCtr(solver=solver,
                                     lambda_u=1e-4,
                                     Np=2,
                                     disc_method='forward_euler')

# Define control system, which includes the MTPA lookup table as an outer control loop and the MPC
# current controller as an inner control loop
ctr_sys = common.ControlSystem(control_loops=[MPTA_lut, ctr],
                               ref_seq=ref_seq,
                               Ts=25e-6)

# Simulate the system
sim = Simulation(sys=sys,
                 ctr=ctr_sys,
                 Ts_sim=25e-6,
                 disc_method='forward_euler')
sim_data = sim.simulate(t_stop=0.15)

# Save the simulation data to a .mat file
sim.save_data()

# Plot the results
plotter = Plotter(data=sim_data, sys=sys)
plotter.plot_states(states_to_plot=['iS'], frames=['dq'], plot_u_abc=True)
plotter.plot_control_signals_machine(plot_T=True, T_ref=T_ref_seq)
plotter.show_all()
