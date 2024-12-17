"""
Example of state-space control for a grid-connected power converter. The controllers objective is to
track the reference of the grid current.
"""

#pylint: disable=wrong-import-position
import sys as system
import os

import numpy as np

## -------------------------------------------------------------------- ##
# These allow using soft4pes from this folder
# Get the directory of the current file and add the grandparent directory
# (soft4pes) to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
system.path.append(os.path.abspath(os.path.join(current_dir, '..', '..')))
## -------------------------------------------------------------------- ##

from soft4pes import model
from soft4pes.control.lin import RLGridStateSpaceCurrCtr
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

# Define base values
base = model.grid.BaseGrid(Vg_R_SI=3300, Ig_R_SI=1575, fg_R_SI=50)

# Define current reference sequence
i_ref_dq = Sequence(np.array([0, 1]), np.array([[1, 0], [1, 0]]))

# Define grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=3300,
                                          fg_SI=50,
                                          Rg_SI=0.01815,
                                          Lg_SI=5.7773e-4,
                                          base=base)

# Define system models
sys = model.grid.RLGrid(par=grid_params, base=base, ig_ref_init=i_ref_dq(0))
conv = model.conv.Converter(v_dc_SI=5529.2, nl=3, base=base)

# Define controller
ctr = RLGridStateSpaceCurrCtr(sys=sys,
                              base=base,
                              Ts=100e-6,
                              i_ref_seq_dq=i_ref_dq)

# Simulate the system
sim = Simulation(sys=sys, conv=conv, ctr=ctr, Ts_sim=5e-6)
sim.simulate(t_stop=0.2)
