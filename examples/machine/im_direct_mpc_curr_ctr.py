"""
Example of direct model predictive control (MPC) for an induction machine drive system. The 
controller aims to track the stator current reference calculated based on the reference values of 
the stator flux magnitude and torque. The machine operates at a constant (nominal) speed.
"""

from types import SimpleNamespace
import numpy as np

from soft4pes import model
from soft4pes.control import mpc, common
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation
from soft4pes.utils.plotter import Plotter

# Define base values
base = model.machine.BaseMachine(Vm_R_SI=400,
                                 Im_R_SI=4.4,
                                 fm_R_SI=50,
                                 npp=1,
                                 pf=0.85)

# Define torque reference sequence using a sequence object
# The first array contains the time instants (in seconds) and the second array the corresponding
# reference values (in per unit). The reference is interpolated linearly between the time instants.
T_ref_seq = Sequence(
    np.array([0, 0.05, 0.05, 0.15, 0.15, 0.2]),
    np.array([0, 0, 1, 1, 0.5, 0.5]),
)
ref_seq = SimpleNamespace(T_ref_seq=T_ref_seq)

# Define induction machine parameters
im_params = model.machine.InductionMachineParameters(fs_SI=50,
                                                     pf=0.85,
                                                     Rs_SI=2.7,
                                                     Rr_SI=2.4,
                                                     Lls_SI=9.868e-3,
                                                     Llr_SI=11.777e-3,
                                                     Lm_SI=394.704e-3,
                                                     base=base)

# Define system models
conv = model.conv.Converter(v_dc_SI=650, nl=3, base=base)
sys = model.machine.InductionMachine(
    par=im_params,
    conv=conv,
    base=base,
    psiS_mag_ref=1,
    T_ref_init=T_ref_seq(0),
)

# Use Branch-and-Bound solver
solver = mpc.solvers.MpcBnB(conv=conv)

# Uncomment to use enumeration based solver
# solver = mpc.solvers.MpcEnum(conv=conv)

# Define controller
ctr = mpc.controllers.IMMpcCurrCtr(solver,
                                   lambda_u=10e-3,
                                   Np=2,
                                   disc_method='exact_discretization')
ctr_sys = common.ControlSystem(control_loops=[ctr], ref_seq=ref_seq, Ts=100e-6)

# Simulate system
sim = Simulation(sys=sys,
                 ctr=ctr_sys,
                 Ts_sim=5e-6,
                 disc_method='exact_discretization')
sim_data = sim.simulate(t_stop=0.2)
sim.save_data()

plotter = Plotter(sim_data, sys)
plotter.plot_states(states_to_plot=['iS', 'psiR'],
                    frames=['dq', 'abc'],
                    plot_u_abc=True)
plotter.plot_control_signals_machine(plot_T=True, T_ref=T_ref_seq)
plotter.show_all()
