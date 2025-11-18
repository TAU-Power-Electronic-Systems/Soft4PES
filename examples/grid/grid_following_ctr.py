"""
Example of grid-following control of converter with L filter.
"""

from types import SimpleNamespace
import numpy as np

from soft4pes import model
from soft4pes.control import common, lin, modulation
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define the base values
base = model.grid.BaseGrid(Vg_R_SI=3300, Ig_R_SI=1575, fg_R_SI=50)

# Define the active power and capacitor voltage magnitude reference sequences
P_ref_seq = Sequence(np.array([0, 0.1, 0.1, 0.3]), np.array([1, 1, 0, 0]))
Q_ref_seq = Sequence(np.array([0, 0.2, 0.2, 0.3]), np.array([0, 0, 0.5, 0.5]))
ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, Q_ref_seq=Q_ref_seq)

# Define the grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=3300,
                                          fg_SI=50,
                                          Rg_SI=0.01815,
                                          Lg_SI=5.7773e-4,
                                          base=base)

# Define the LC-filter parameters
l_params = model.grid.LFilterParameters(L_fc_SI=0.5e-3,
                                        R_fc_SI=0.1,
                                        base=base)

# Define the system model
conv = model.conv.Converter(v_dc_SI=6200, nl=3, base=base)
sys = model.grid.RLGridLFilter(grid_params, l_params, conv, base)

# Build the current reference
curr_ref = lin.GridCurrRefGen()

# Build the current controller
ic_ctr = lin.LConvCurrCtr(sys=sys)

control_loops = [curr_ref, ic_ctr]

# Define the control system. Set pwm to None to disable PWM.
ctr_sys = common.ControlSystem(control_loops=control_loops,
                               ref_seq=ref_seq,
                               Ts=100e-6,
                               pwm=modulation.CarrierPWM())

# Simulate the system
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=1e-6)
sim_data = sim.simulate(t_stop=0.3)
sim.save_data()

# Plot the results
plotter = Plotter(sim_data, sys)
plotter.plot_states(states_to_plot=['ig'], frames=['abc'], plot_u_abc=True)
plotter.plot_control_signals_grid(plot_P=True,
                                  plot_Q=True,
                                  P_ref=P_ref_seq,
                                  Q_ref=Q_ref_seq)
plotter.show_all()