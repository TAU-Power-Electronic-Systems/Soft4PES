"""
Example of direct model predictive control (MPC) for a grid-connected power converter. MPC is 
designed as a current controller, thus the main objective is to track the reference of the grid 
current. The current references are generated based on the power references. 
"""

from types import SimpleNamespace
import numpy as np

from soft4pes import model
from soft4pes.control import mpc, common, lin
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

# Define base values
base = model.grid.BaseGrid(Vg_R_SI=3300, Ig_R_SI=1575, fg_R_SI=50)

# Define power reference sequences
P_ref_seq = Sequence(np.array([0, 0.1, 0.1, 1]), np.array([1, 1, 0, 0]))
Q_ref_seq = Sequence(np.array([0, 0.1, 0.1, 1]), np.array([0, 0, 0, 0]))
ref_seq = SimpleNamespace(P_ref_seq=P_ref_seq, Q_ref_seq=Q_ref_seq)

# Define grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=3300,
                                          fg_SI=50,
                                          Rg_SI=0.01815,
                                          Lg_SI=5.7773e-4,
                                          base=base)
# Define system models
conv = model.conv.Converter(v_dc_SI=5200, nl=3, base=base)
sys = model.grid.RLGrid(grid_params, conv, base)

# Define solver to be enumeration based
solver = mpc.solvers.MpcEnum(conv=conv)

# Uncomment to use Branch-and-Bound solver
# solver = mpc.solvers.MpcBnB(conv=conv)

# Define control loops, the outer loop generates the grid current reference based on the power
# references, acting as a feedforward term. The inner loop (direct MPC) is used to track the grid
# current reference.
ref_ctr = lin.GridCurrRefGen()
ctr = mpc.controllers.RLGridMpcCurrCtr(solver=solver, lambda_u=10e-3, Np=1)
ctr_sys = common.ControlSystem(control_loops=[ref_ctr, ctr],
                               ref_seq=ref_seq,
                               Ts=100e-6)

# Simulate the system
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=5e-6)
sim.simulate(t_stop=0.2)
sim.save_data()
