"""
Example of grid-following control of converter with L or LCL filter.
"""

from types import SimpleNamespace
import numpy as np

from plotters.plot_grid_following_ctr import plot_gfl_example
from soft4pes import model
from soft4pes.control import common, lin, modulation
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

# Define the base values
base = model.grid.BaseGrid(Vg_R_SI=400, Ig_R_SI=18, fg_R_SI=50)

# Define the active power and capacitor voltage magnitude reference sequences
P_ref_seq = Sequence(
    times=np.array([0, 0.3, 0.3, 1]),
    values=np.array([1, 1, 0.8, 0.8]),
)

Q_ref_seq = Sequence(
    times=np.array([0, 0.6, 0.6, 1]),
    values=np.array([0, 0, 0.2, 0.2]),
)

ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, Q_ref_seq=Q_ref_seq)

# Define the grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=400,
                                          fg_SI=50,
                                          Rg_SI=0.07,
                                          Lg_SI=3e-3,
                                          base=base)

# Define the LC-filter parameters
lcl_params = model.grid.LCLFilterParameters(L_fc_SI=3e-3,
                                            R_fc_SI=0.1,
                                            C_SI=10e-6,
                                            R_c_SI=0.001,
                                            base=base)

# Define the system model
conv = model.conv.Converter(v_dc_SI=750, nl=2, base=base)
sys = model.grid.RLGridLCLFilter(grid_params, lcl_params, conv, base)

# Build the current reference
curr_ref = lin.GridCurrRefGen()

# Build the cascade controller loops
ic_ctr = lin.LCLConvCurrCtr(sys=sys)

control_loops = [curr_ref, ic_ctr]

# Define the control system. Set pwm to None to disable PWM.
ctr_sys = common.ControlSystem(control_loops=control_loops,
                               ref_seq=ref_seq,
                               Ts=100e-6,
                               pwm=modulation.CarrierPWM())

# Simulate the system
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=1e-6)
sim_data = sim.simulate(t_stop=1)

# Save the simulation data to a .mat file
sim.save_data()
# Plot the simulation results.
plot_gfl_example(sim_data)