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
from soft4pes.control import mpc
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

# Define base values
base = model.grid.BaseGrid(Vg_R_SI=3300, Ig_R_SI=1575, fg_R_SI=50)

# Define grid parameters
grid_params = model.grid.RLGridParameters(Vg_SI=3300,
                                          fg_SI=50,
                                          Rg_SI=0.01815,
                                          Lg_SI=5.7773e-4,
                                          base=base)

filter_params = model.grid.LCLFilterParameters(L_fc_SI=3.3e-3,
                                               C_SI=10e-6,
                                               base=base)

# Define system models
sys = model.grid.RLGridLCLFilter(par_grid=grid_params,
                                 par_lcl_filter=filter_params,
                                 base=base)

matrices = sys.get_discrete_state_space(v_dc=5200 / base.V, Ts=100e-6)
print(sys.get_grid_voltage(0))
sys.update_state(matrices, np.array([0, -0.87, 0.87]), 0)
print(sys.x)
sys.update_state(matrices, np.array([0, -0.87, 0.87]), 100e-6)
print(sys.x)
print(sys.data)
