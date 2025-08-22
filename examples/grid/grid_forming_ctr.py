"""
Example of grid-forming control of converter with LC filter using reference-feedforward power
synchronization control (RFPSC) and cascade controller or model predictive control (MPC). The RFPSC 
synchronizes with the grid and generates the capacitor voltage reference, which is subsequently 
tracked by the cascade controller or MPC.
"""

from types import SimpleNamespace
import numpy as np

from plotters.plot_grid_forming_ctr import plot_gfm_example
from soft4pes import model
from soft4pes.control import common, lin, mpc
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

# Define the base values
base = model.grid.BaseGrid(Vg_R_SI=400, Ig_R_SI=18, fg_R_SI=50)

# Define the active power and capacitor voltage magnitude reference sequences
P_ref_seq = Sequence(
    times=np.array([0, 0.3, 0.3, 1]),
    values=np.array([0.5, 0.5, 1, 1]),
)
V_ref_seq = Sequence(
    times=np.array([0, 0.4, 0.4, 1]),
    values=np.array([1, 1, 0.9, 0.9]),
)
ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, V_ref_seq=V_ref_seq)

# Define the grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=400,
                                          fg_SI=50,
                                          Rg_SI=0.07,
                                          Lg_SI=30e-3,
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

# Build the reference-feedforward power synchronization control (RFPSC)
rfpsc = lin.RFPSC(sys)

# Define indirect MPC
solver = mpc.solvers.IndirectMpcQP()
vc_mpc = mpc.controllers.LCLVcMpcCtr(solver=solver,
                                     lambda_u=1e-4,
                                     Np=4,
                                     I_conv_max=1.3)

# Build the cascade controller loops
ic_ctr = lin.LCLConvCurrCtr(sys=sys)
vc_ctr = lin.LCLVcCtr(sys=sys, I_conv_max=1.3, curr_ctr=ic_ctr)

# Select the control loops
control_loops = [rfpsc, vc_mpc]  # Use MPC with RFPSC

# Uncomment the following line to use the cascade controller instead of MPC
# control_loops = [rfpsc, vc_ctr, ic_ctr] # Use cascade controller with RFPSC

# Define the control system
ctr_sys = common.ControlSystem(control_loops=control_loops,
                               ref_seq=ref_seq,
                               Ts=100e-6)

# Simulate the system
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=5e-6)
sim_data = sim.simulate(t_stop=0.5)

# Save the simulation data to a .mat file
sim.save_data()

# Plot the simulation results. Exclude the initial transient by setting t_start to 0.2 s.
plot_gfm_example(sim_data, t_start=0.2)
