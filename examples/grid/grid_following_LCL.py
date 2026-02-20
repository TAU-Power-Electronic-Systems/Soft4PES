"""
Example of grid-following control of a converter with an LCL filter.
"""

from types import SimpleNamespace
import numpy as np

from pars.grid_config import get_default_system
from soft4pes import model
from soft4pes.control import common, lin, modulation
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define the base values
config = get_default_system(name='Strong_LV_Grid_LCL_Filter_2L_conv')
sys = model.grid.RLGridLCLFilter(par_grid=config.grid_params,
                                 par_lcl_filter=config.lcl_params,
                                 conv=config.conv,
                                 base=config.base)

# Define power reference sequences
# The first array contains the time instants (in seconds) and the second array the corresponding
# reference values (in per unit). The reference is interpolated linearly between the time instants.
P_ref_seq = Sequence(np.array([0, 0.1, 0.1, 0.2, 0.2, 0.4]),
                     np.array([0, 0, 1, 1, 0, 0]))
Q_ref_seq = Sequence(
    np.array([0, 0.3, 0.3]),
    np.array([0, 0, 0.3]),
)
ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, Q_ref_seq=Q_ref_seq)

# Build the current reference
ig_ref_gen = lin.GridCurrRefGen()

# Build the current controller
ig_ctr = lin.LCLGridCurrCtrWACFB(sys=sys)

# Define control loops
control_loops = [ig_ref_gen, ig_ctr]
ctr_sys = common.ControlSystem(control_loops=control_loops,
                               ref_seq=ref_seq,
                               Ts=100e-6,
                               pwm=modulation.CarrierPWM())

# Simulate the system
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=1e-6)
sim_data = sim.simulate(t_stop=0.4)
sim.save_data()

# Plot the results
plotter = Plotter(sim_data, sys)
plotter.plot_states(states_to_plot=['ig'], frames=['abc'], plot_u_abc_ref=True)
plotter.plot_control_signals_grid(plot_P=True,
                                  plot_Q=True,
                                  P_ref=P_ref_seq,
                                  Q_ref=Q_ref_seq)
plotter.show_all()
