"""
Example of grid-following control of a converter with an L filter with open-loop OPPs.
"""

from types import SimpleNamespace
import numpy as np

from pars.grid_config import get_default_system
from soft4pes import model
from soft4pes.control import common, lin, opp
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define power reference sequences
# The first array contains the time instants (in seconds) and the second array the corresponding
# reference values (in per unit). The reference is interpolated linearly between the time instants.
P_ref_seq = Sequence(np.array([0, 0.2]), np.array([1, 1]))
Q_ref_seq = Sequence(
    np.array([0, 0.2]),
    np.array([0, 0]),
)
ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, Q_ref_seq=Q_ref_seq)

# Define the base values
config = get_default_system(name='Strong_MV_Grid_L_Filter_3L_conv')
sys = model.grid.RLGridLFilter(par_grid=config.grid_params,
                               par_l_filter=config.filter_params,
                               conv=config.conv,
                               base=config.base)

# PLL implementation
pll = lin.PLL(sys=sys, zeta=1, wn=2 * np.pi * 5)

# Build the current reference
curr_ref = lin.GridCurrRefGen()

# Build the open-loop current controller
i_conv_ctr = opp.RLGridLFilterOpenLoopOPP(sys=sys,
                                          d=5,
                                          opp_file='3L_d5_opp_inductive.nc')

# Define the control loops: the PLL is used for synchronization, the outer loop generates
# the grid current reference from the power references, and the inner loop applies the open-loop control.
control_loops = [pll, curr_ref, i_conv_ctr]
ctr_sys = common.ControlSystem(control_loops=control_loops,
                               ref_seq=ref_seq,
                               Ts=50e-6)

# Simulate the system
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=5e-6)
sim_data = sim.simulate(t_stop=0.2)
sim.save_data()

# Plot the results
plotter = Plotter(sim_data, sys)
plotter.plot_states(states_to_plot=['ig'], frames=['abc'], plot_u_abc=True)
plotter.plot_control_signals_grid(plot_P=True,
                                  plot_Q=True,
                                  P_ref=P_ref_seq,
                                  Q_ref=Q_ref_seq)
plotter.plot_spectra(states_to_plot=['ig'],
                     f_fund_SI=50.0,
                     f_max_SI_plot=7500,
                     start_time=0.075,
                     n_cycles=1)
plotter.show_all()
