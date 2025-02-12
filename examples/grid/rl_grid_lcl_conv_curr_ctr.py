"""
Example of Current Controller (CC) for a grid-connected power converter with LC(L) filter. 
The objective is to track the reference of the converter current. 
The current references are given externally in this example. 
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
base = model.grid.BaseGrid(Vg_R_SI=3300, Ig_R_SI=1575, fg_R_SI=50)

# Define converter current reference sequences
i_conv_ref_dq_seq = Sequence(
    np.array([0, 0.1, 0.1, 1]),
    np.array([[1, 0], [1, 0], [0.8, -0.1], [0.8, -0.1]]))
ref_seq = SimpleNamespace(i_conv_ref_dq_seq=i_conv_ref_dq_seq)

# Define grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=3300,
                                          fg_SI=50,
                                          Rg_SI=0.01815,
                                          Lg_SI=5.7773e-4,
                                          base=base)

filter_params = model.grid.LCLFilterParameters(L_fc_SI=2.8e-3,
                                               C_SI=15e-6,
                                               base=base,
                                               R_fc_SI=1e-3)

# Define system models
sys = model.grid.RLGridLCLFilter(par_grid=grid_params,
                                 par_lcl_filter=filter_params,
                                 base=base)
conv = model.conv.Converter(v_dc_SI=5529, nl=3, base=base)

# Define control strategy
ctr = lin.LCLConvCurrCtr(sys=sys)
ctrSys = common.ControlSystem(control_loops=[ctr], ref_seq=ref_seq, Ts=100e-6)

# Simulate the system
sim = Simulation(sys=sys, conv=conv, ctr=ctrSys, Ts_sim=5e-6)
sim.simulate(t_stop=0.2)
sim.save_data()
