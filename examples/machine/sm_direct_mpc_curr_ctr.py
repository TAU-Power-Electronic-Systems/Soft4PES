"""
Example of direct model predictive control (MPC) for a permanent magnet synchronous machine (PMSM) 
drive system. The controller aims to track the stator current reference calculated based on the 
reference values of the maximum torque per ampere (MTPA) trajectory and torque. The machine operates
at a constant (nominal) speed.
"""

from types import SimpleNamespace
import numpy as np

from soft4pes import model
from soft4pes.control import mpc, common
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define base values
# Example PMSM (https://ieeexplore.ieee.org/document/10227497)
base = model.machine.BaseMachine(Vm_R_SI=318,
                                 Im_R_SI=138,
                                 fm_R_SI=120,
                                 npp=4,
                                 pf=0.86)

# Define torque reference sequence
# The first array contains the time instants (in seconds) and the second array the corresponding
# reference values (in per unit). The reference is interpolated linearly between the time instants.
T_ref_seq = Sequence(
    np.array([0, 0.05, 0.05, 0.1, 0.1, 0.15]),
    np.array([0, 0, 0.5, 0.5, 1, 1]),
)
ref_seq = SimpleNamespace(T_ref_seq=T_ref_seq)

# Define PMSM parameters
sm_params = model.machine.PMSMParameters(fs_SI=120,
                                         pf_SI=0.86,
                                         Rs_SI=0.046,
                                         Lsd_SI=1.58e-3,
                                         Lsq_SI=6.48e-3,
                                         LambdaPM_SI=0.684,
                                         base=base)

# Create a MTPA lookup table for current reference calculation
MPTA_lut = common.MTPALookupTable(par=sm_params)

# Define system models. The MTPA lookup table is passed to the PMSM model to set the initial state.
conv = model.conv.Converter(v_dc_SI=980, nl=2, base=base)
sys = model.machine.PMSM(par=sm_params,
                         conv=conv,
                         base=base,
                         T_ref_init=T_ref_seq(0),
                         mtpa_lut=MPTA_lut)

# Use Branch-and-Bound solver
solver = mpc.solvers.MpcBnB(conv=conv)

# Define current controller
ctr = mpc.controllers.SMMpcCurrCtr(solver,
                                   lambda_u=1e-3,
                                   Np=2,
                                   disc_method='forward_euler')

# Define control system, which includes the MTPA lookup table as an outer control loop and the MPC
# current controller as an inner control loop
ctr_sys = common.ControlSystem(control_loops=[MPTA_lut, ctr],
                               ref_seq=ref_seq,
                               Ts=25e-6)

# Simulate system
sim = Simulation(sys=sys,
                 ctr=ctr_sys,
                 Ts_sim=25e-6,
                 disc_method='forward_euler')
sim_data = sim.simulate(t_stop=0.15)
sim.save_data()

# Plot results
plotter = Plotter(sim_data, sys)
plotter.plot_states(states_to_plot=['iS'], frames=['dq'], plot_u_abc=True)
plotter.plot_control_signals_machine(plot_T=True, T_ref=T_ref_seq)
plotter.show_all()
