"""
Example of cascade control (voltage control and current control) of voltage-source converter 
equipped with an LC(L) filter. The objective is to track the reference of the capacitor voltage.
Also, the controller has inherent overcurrent protection.
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
from soft4pes.control import common, lin
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

# Define base values
base = model.grid.BaseGrid(Vg_R_SI=400, Ig_R_SI=18, fg_R_SI=50)

# Define converter current reference sequences
vc_ref_dq_seq = Sequence(np.array([0, 0.2, 0.2, 1]),
                         np.array([[1, 0], [1, 0], [0.6, 0], [0.6, 0]]))
ref_seq = SimpleNamespace(vc_ref_dq_seq=vc_ref_dq_seq)

# Define grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=400,
                                          fg_SI=50,
                                          Rg_SI=0,
                                          Lg_SI=1.96e-3,
                                          base=base)

filter_params = model.grid.LCLFilterParameters(L_fc_SI=2.94e-3,
                                               C_SI=10e-6,
                                               base=base,
                                               R_fc_SI=92e-3)

# Define system models
sys = model.grid.RLGridLCLFilter(par_grid=grid_params,
                                 par_lcl_filter=filter_params,
                                 base=base)
conv = model.conv.Converter(v_dc_SI=650, nl=3, base=base)

# Define control strategy
curr_ctr = lin.LCLConvCurrCtr(sys=sys)
volt_ctr = lin.LCLVcCtr(sys=sys, i_conv_lim=1.2, curr_ctr=curr_ctr)

ctrSys = common.ControlSystem(control_loops=[volt_ctr, curr_ctr],
                              ref_seq=ref_seq,
                              Ts=125e-6)

# Simulate the system
sim = Simulation(sys=sys, conv=conv, ctr=ctrSys, Ts_sim=5e-6)
sim.simulate(t_stop=0.4)
sim.save_data()
