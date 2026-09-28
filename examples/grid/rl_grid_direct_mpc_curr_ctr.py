"""
Example of model predictive control (MPC) for a grid-connected power converter. MPC is 
designed as a current controller, thus the main objective is to track the reference of the grid 
current. The current references are generated based on the power references. 
"""

from types import SimpleNamespace
import numpy as np

from pars.grid_config import get_custom_system
from soft4pes import model
from soft4pes.control import modulation, mpc, common, lin
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Get the system parameters from the ready made components. All the available components and systems
# are defined in the examples/grid/pars/grid_parameter_sets.json file, and given in the
# documentation. Here, a 3-level converter connected to a strong, low voltage grid without a filter
# is used.
config = get_custom_system(grid_name='Strong_LV_Grid',
                           filter_name='LV_L_Filter',
                           converter_name='3L_LV_Converter')

# Create the system model consisting of the grid and converter
sys = model.grid.RLGridLFilter(par_grid=config.grid_params,
                               par_l_filter=config.filter_params,
                               conv=config.conv,
                               base=config.base)

# Define power reference sequences
# The first array contains the time instants (in seconds) and the second array the corresponding
# reference values (in per unit). The reference is interpolated linearly between the time instants.
P_ref_seq = Sequence(np.array([0, 0.05, 0.05, 0.1, 0.1, 0.2]),
                     np.array([0, 0, 1, 1, 0, 0]))
Q_ref_seq = Sequence(
    np.array([0, 0.1, 0.1, 0.2]),
    np.array([0, 0, 1, 1]),
)
ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, Q_ref_seq=Q_ref_seq)

# Define control loops, the outer loop generates the grid current reference based on the power
# references, acting as a feedforward term. The inner loop (MPC) is used to track the grid
# current reference.

# PLL implementation
pll = lin.PLL(sys=sys, zeta=1, wn=2 * np.pi * 5)

# Grid current reference generator
ref_ctr = lin.GridCurrRefGen()

# Choose the current control strategy.
# "FCSMPC" for finite-control-set model predictive control,
# "GP3C" for gradient-based predictive pulse pattern control

CTR_STRATEGY = "GP3C"

match CTR_STRATEGY:
    case "FCSMPC":
        # Define solver to be Branch-and-Bound
        solver = mpc.solvers.BranchAndBound()

        # Define the MPC controller
        ctr = mpc.algorithms.RLGridCurrCtr(solver=solver, lambda_u=5e-3, Np=2)

        control_loops = [pll, ref_ctr, ctr]

    case "GP3C":
        # Define the QP solver for the GP3C algorithm
        solver = mpc.solvers.MPCQP()

        # Define the OPP loader to get the optimal pulse pattern for the current control
        pat_load = modulation.OPPLoader(sys=sys, switching_frequency=300)

        # Define the GP3C controller
        ctr = mpc.algorithms.GridGP3CCurrCtr(solver=solver,
                                             lambda_u=1e6,
                                             Np=10)

        control_loops = [pll, ref_ctr, pat_load, ctr]

ctr_sys = common.ControlSystem(control_loops=control_loops,
                               ref_seq=ref_seq,
                               Ts=50e-6)

# Simulate the system
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=5e-6)
sim_data = sim.simulate(t_stop=0.2)
sim.save_data()

# Plot the results
plotter = Plotter(data=sim_data, sys=sys)
plotter.plot_states(states_to_plot=['ig'], frames=['abc'], plot_u_abc=True)
plotter.plot_control_signals_grid(plot_P=True,
                                  plot_Q=True,
                                  P_ref=P_ref_seq,
                                  Q_ref=Q_ref_seq)
plotter.show_all()
