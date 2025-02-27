"""
Example of grid-forming control of converter with LCL filter using reference-feedforward power
synchronization control (RFPSC) and cascade controller. The RFPSC synchronizes with the 
grid and generates the capacitor voltage reference, which is subsequently tracked by the cascade 
controller.
"""

#pylint: disable=wrong-import-position
#pylint: disable=wrong-import-order
import sys as system
import os
import numpy as np

from types import SimpleNamespace

## -------------------------------------------------------------------- ##
# These allow using soft4pes from this folder
# Get the directory of the current file and add the grandparent directory
# (soft4pes) to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
system.path.append(os.path.abspath(os.path.join(current_dir, '..')))
system.path.append(os.path.abspath(os.path.join(current_dir, '..', '..')))
## -------------------------------------------------------------------- ##

from soft4pes import model
from soft4pes.control import common, lin
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from plotters.plot_grid_forming_ctr import plot_gfm_example

# Define base values
base = model.grid.BaseGrid(Vg_R_SI=400, Ig_R_SI=18, fg_R_SI=50)

# Define power reference sequences
P_ref_seq = Sequence(
    times=np.array([0, 0.3, 0.3, 1]),
    values=np.array([0.5, 0.5, 1, 1]),
)
V_ref_seq = Sequence(
    times=np.array([0, 0.4, 0.4, 1]),
    values=np.array([1, 1, 0.9, 0.9]),
)
ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, V_ref_seq=V_ref_seq)

# Define grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=400,
                                          fg_SI=50,
                                          Rg_SI=0.07,
                                          Lg_SI=30e-3,
                                          base=base)

# Define LCL filter parameters
lcl_params = model.grid.LCLFilterParameters(L_fc_SI=3e-3,
                                            R_fc_SI=0.1,
                                            C_SI=10e-6,
                                            R_c_SI=0.001,
                                            base=base)

# Define system model
sys = model.grid.RLGridLCLFilter(grid_params, lcl_params, base)

# Define converter properties
conv = model.conv.Converter(v_dc_SI=750, nl=2, base=base)

# Build the control system from RFPSC and cascade controller
rfpsc = lin.RFPSC(sys)
ic_ctr = lin.LCLConvCurrCtr(sys=sys)
vc_ctr = lin.LCLVcCtr(sys=sys, i_conv_lim=1.2, curr_ctr=ic_ctr)
ctr_sys = common.ControlSystem(control_loops=[rfpsc, vc_ctr, ic_ctr],
                               ref_seq=ref_seq,
                               Ts=100e-6)

# Simulate the system
sim = Simulation(sys=sys, conv=conv, ctr=ctr_sys, Ts_sim=5e-6)
sim_data = sim.simulate(t_stop=0.5)

# Save the simulation data to a .mat file
sim.save_data()

# Plot the simulation results. Exclude the initial transient by setting t_start to 0.2 s.
plot_gfm_example(sim_data, t_start=0.2)
