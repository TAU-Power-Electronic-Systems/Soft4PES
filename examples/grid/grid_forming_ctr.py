"""
Example of grid-forming control of converter with LC filter using reference-feedforward power
synchronization control (RFPSC) and cascade controller or model predictive control (MPC). The RFPSC 
synchronizes with the grid and generates the capacitor voltage reference, which is subsequently 
tracked by the cascade controller or MPC.
"""

from types import SimpleNamespace
import numpy as np

from pars.grid_config import get_default_system
from soft4pes import model
from soft4pes.control import common, lin, mpc, modulation
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Get the system parameters from the ready made components. All the available components and systems
# are defined in the examples/grid/pars/grid_parameter_sets.json file, and given in the
# documentation. Here, a 2-level converter connected to a weak, low voltage grid via an LCL filter
# is used.
config = get_default_system(name='Weak_LV_Grid_LCL_Filter_2L_conv')
sys = model.grid.RLGridLCLFilter(par_grid=config.grid_params,
                                 par_lcl_filter=config.lcl_params,
                                 conv=config.conv,
                                 base=config.base)

# Define the active power and capacitor voltage magnitude reference sequences
# The first array contains the time instants (in seconds) and the second array the corresponding
# reference values (in per unit). The reference is interpolated linearly between the time instants.
P_ref_seq = Sequence(
    times=np.array([0, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.4]),
    values=np.array([0, 0, 0.5, 0.5, 1, 1, 0, 0]),
)
V_ref_seq = Sequence(
    times=np.array([0, 0.4]),
    values=np.array([1, 1]),
)
ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, V_ref_seq=V_ref_seq)

# Start building the grid-forming control system. First, define the reference-feedforward power
# synchronization control (RFPSC), which will be the outermost control loop.
rfpsc = lin.RFPSC(sys=sys)

# Define indirect MPC, used as an inner loop tracking the capacitor voltage reference provided by
# RFPSC. When PWM is used, lambda_u, which penalizes the control effort, should be set to relatively
# low value to prevent MPC from reacting to the switching ripple.
solver = mpc.solvers.IndirectMpcQP()
vc_mpc = mpc.controllers.LCLVcMpcCtr(solver=solver,
                                     lambda_u=1e-2,
                                     Np=4,
                                     I_conv_max=1.3)

# Select the control loops
control_loops = [rfpsc, vc_mpc]  # Use MPC with RFPSC

# Uncomment the following line to use the cascade controller instead of MPC
# ic_ctr = lin.LCLConvCurrCtr(sys=config.sys)
# vc_ctr = lin.LCLVcCtr(sys=config.sys, I_conv_max=1.3, curr_ctr=ic_ctr)
# control_loops = [rfpsc, vc_ctr, ic_ctr]

# Define the control system. Set pwm to None to disable PWM.
ctr_sys = common.ControlSystem(control_loops=control_loops,
                               ref_seq=ref_seq,
                               Ts=100e-6,
                               pwm=modulation.CarrierPWM())

# Simulate the system. In order to get accurate results with PWM, the simulation time step should
# be at least two magnitudes lower than the control time step.
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=1e-6)
sim_data = sim.simulate(t_stop=0.4)

# Save the simulation data to a .mat file
sim.save_data()

# Plot the simulation results, excluding the initial transient
plotter = Plotter(data=sim_data, sys=sys, t_start=0.05)
plotter.plot_states(states_to_plot=['vc', 'i_conv', 'ig'],
                    frames=['abc', 'abc', 'abc'],
                    plot_u_abc_ref=True)
plotter.plot_control_signals_grid(plot_P=True,
                                  plot_Q=True,
                                  plot_V=True,
                                  P_ref=P_ref_seq,
                                  V_ref=V_ref_seq)
plotter.show_all()
