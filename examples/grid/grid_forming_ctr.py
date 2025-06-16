"""
Example of grid-forming control of converter with LC filter using reference-feedforward power
synchronization control (RFPSC) and cascade controller or model predictive control (MPC). The RFPSC 
synchronizes with the grid and generates the capacitor voltage reference, which is subsequently 
tracked by the cascade controller or MPC. MPC can also be replaced by a cascade controller. 
"""

from types import SimpleNamespace
import numpy as np

from soft4pes import model
from soft4pes.control import common, lin, mpc, modulation
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define the base values
base = model.grid.BaseGrid(Vg_R_SI=400, Ig_R_SI=18, fg_R_SI=50)

# Define the active power and capacitor voltage magnitude reference sequences
P_ref_seq = Sequence(
    times=np.array([0, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.4]),
    values=np.array([0, 0, 0.5, 0.5, 1, 1, 0, 0]),
)
V_ref_seq = Sequence(
    times=np.array([0, 0.4]),
    values=np.array([1, 1]),
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

# Define indirect MPC. When PWM is used, lambda_u, which penalizes the control effort, should be set
# to relatively low value to prevent MPC from reacting to the switching ripple.
solver = mpc.solvers.IndirectMpcQP()
vc_mpc = mpc.controllers.LCLVcMpcCtr(solver=solver,
                                     lambda_u=1e-2,
                                     Np=4,
                                     I_conv_max=1.3)

# Select the control loops
control_loops = [rfpsc, vc_mpc]  # Use MPC with RFPSC

# Uncomment the following line to use the cascade controller instead of MPC
ic_ctr = lin.LCLConvCurrCtr(sys=sys)
vc_ctr = lin.LCLVcCtr(sys=sys, I_conv_max=1.3, curr_ctr=ic_ctr)
control_loops = [rfpsc, vc_ctr, ic_ctr]

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
plotter = Plotter(sim_data, sys, t_start=0.05)
plotter.plot_states(states_to_plot=['vc', 'i_conv', 'ig'],
                    frames=['abc', 'abc', 'abc'],
                    plot_u_abc_ref=True)
plotter.plot_control_signals_grid(plot_P=True,
                                  plot_Q=True,
                                  plot_V=True,
                                  P_ref=P_ref_seq,
                                  V_ref=V_ref_seq)
plotter.show_all()
