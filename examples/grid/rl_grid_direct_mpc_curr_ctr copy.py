"""
Example of direct model predictive control (MPC) for a grid-connected power converter. MPC is 
designed as a current controller, thus the main objective is to track the reference of the grid 
current. The current references are generated based on the power references. 
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
system.path.append(os.path.abspath(os.path.join(current_dir, '..', '..')))
## -------------------------------------------------------------------- ##

from soft4pes import model
from soft4pes.control import mpc, common
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

# Define base values
base = model.grid.BaseGrid(Vg_R_SI=400, Ig_R_SI=18, fg_R_SI=50)

# Define power reference sequences
vc_ref_dq_seq = Sequence(np.array([0, 1]), np.array([[0.5, 0], [0.5, 0]]))
ref_seq = SimpleNamespace(vc_ref_dq_seq=vc_ref_dq_seq)

# Define grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=400,
                                          fg_SI=50,
                                          Rg_SI=0.01,
                                          Lg_SI=5e-3,
                                          base=base)
lcl_params = model.grid.LCLFilterParameters(R_fc_SI=0.01,
                                            L_fc_SI=3e-3,
                                            C_SI=10e-6,
                                            R_c_SI=0.0001,
                                            base=base)
# Define system models
sys = model.grid.RLGridLCLFilter(par_grid=grid_params,
                                 par_lcl_filter=lcl_params,
                                 base=base)
conv = model.conv.Converter(v_dc_SI=650, nl=2, base=base)

# Define solver to be enumeration based
# solver = mpc.solvers.MpcEnum(conv=conv)

# Uncomment to use Branch-and-Bound solver

# Define control loops, the outer loop generates the grid current reference based on the power
# references, acting as a feedforward term. The inner loop (direct MPC) is used to track the grid
# current reference.
solver = mpc.solvers.MpcQP()
ctr = mpc.controllers.LCLVcMpcCtr(solver=solver, lambda_u=1e-4, Np=4)
ctrSys = common.ControlSystem(control_loops=[ctr], ref_seq=ref_seq, Ts=100e-6)

# Simulate the system
sim = Simulation(sys=sys, conv=conv, ctr=ctrSys, Ts_sim=100e-6)
sim.simulate(t_stop=0.1)
sim.save_data()
