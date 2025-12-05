"""
Example of direct model predictive control (MPC) for a grid-connected power converter. MPC is 
designed as a current controller, thus the main objective is to track the reference of the grid 
current. The current references are generated based on the power references. 
"""

from types import SimpleNamespace
import numpy as np

from pars.grid_config import get_custom_system
from soft4pes import model
from soft4pes.control import mpc, common, lin
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Get the system parameters from the ready made components. All the available components and systems
# are defined in the examples/grid/pars/grid_parameter_sets.json file, and given in the
# documentation. Here, a 3-level converter connected to a strong, low voltage grid without a filter
# is used.
config = get_custom_system(grid_name='Strong_LV_Grid',
                           filter_name='No_Filter',
                           converter_name='3L_LV_Converter')

# Create the system model consisting of the grid and converter
sys = model.grid.RLGrid(par=config.grid_params,
                        conv=config.conv,
                        base=config.base)

# Define power reference sequences
# The first array contains the time instants (in seconds) and the second array the corresponding
# reference values (in per unit). The reference is interpolated linearly between the time instants.
P_ref_seq = Sequence(times=np.array([0, 0.1, 0.1, 0.3]),
                     values=np.array([1, 1, 0, 0]))
Q_ref_seq = Sequence(times=np.array([0, 0.2, 0.2, 0.3]),
                     values=np.array([0, 0, 0.5, 0.5]))
ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, Q_ref_seq=Q_ref_seq)

# Define the outer loop of the control system, which generates the grid current references based on
# the power references.
ref_ctr = lin.GridCurrRefGen()

# Define the direct MPC current controller, which tracks the grid current references. Start by
# defining the solver for the MPC to be the branch and bound solver.
solver = mpc.solvers.MpcBnB(conv=config.conv)

# Uncomment to use enumeration based solver instead of branch and bound
# solver = mpc.solvers.MpcEnum(conv=config.conv)

# Create the MPC current controller
ctr = mpc.controllers.RLGridMpcCurrCtr(solver=solver, lambda_u=10e-3, Np=1)

# Define the complete control system
ctr_sys = common.ControlSystem(control_loops=[ref_ctr, ctr],
                               ref_seq=ref_seq,
                               Ts=100e-6)

# Simulate the system
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=5e-6)
sim_data = sim.simulate(t_stop=0.3)

# Save the simulation data to a .mat file
sim.save_data()

# Plot the results
plotter = Plotter(data=sim_data, sys=sys)
plotter.plot_states(states_to_plot=['ig'], frames=['abc'], plot_u_abc=True)
plotter.plot_control_signals_grid(plot_P=True,
                                  plot_Q=True,
                                  P_ref=P_ref_seq,
                                  Q_ref=Q_ref_seq)
plotter.show_all()
