#pylint: disable=wrong-import-position

import sys as system
import os
import time

import numpy as np

## ---------------------------------- ##
# These allow using soft4pes from this folder ##
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python paths
system.path.append(parent_dir)
## ---------------------------------- ##

from soft4pes import model, control
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

base = model.grid.BaseGrid(Vgr=3300, Igr=1575, fgr=50)
sys = model.grid.RLGrid(Vgr=3300, fgr=50, Rg=0.01815, Lg=5.7773e-4, base=base)

conv = model.conv.Converter(v_dc=5200, nl=3, base=base)

i_ref_dq = Sequence(np.array([0, 1]), np.array([[1, 0], [1, 0]]), base.w)

ctr = control.lin.RLGridStateSpaceCurrCtr(sys=sys,
                                          base=base,
                                          Ts=100e-6,
                                          i_ref_seq_dq=i_ref_dq)
sim = Simulation(sys=sys, conv=conv, ctr=ctr, Ts_sim=5e-6)

start_time = time.time()

sim.simulate(t_stop=0.1)

end_time = time.time()
execution_time = end_time - start_time
print("Execution time:", execution_time, "seconds")
