"""
Example of controlling grid current of a resistive inductive grid with direct model predictive 
control (MPC). The controller aims to track the grid current reference. 
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
from soft4pes.control import mpc
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

# Define base values
base = model.grid.BaseGrid(Vgr=3300, Igr=1575, fgr=50)

# Define system models
sys = model.grid.RLGrid(Vgr=3300, fgr=50, Rg=0.01815, Lg=5.7773e-4, base=base)
conv = model.conv.Converter(v_dc=5200, nl=3, base=base)

# Define current reference sequence
i_ref_dq = Sequence(np.array([0, 0.1, 0.1, 1]),
                    np.array([[1, 0], [1, 0], [0.3, 0.3], [0.3, 0.3]]))

# Define solver to be enumeration based
solver = mpc.solvers.MpcEnum(conv=conv)

# Comment in to use Branch and Bound solver
# solver = mpc.solvers.MpcBnB(conv=conv)

# Define controller
ctr = mpc.controllers.RLGridMpcCurrCtr(solver,
                                       lambda_u=10e-3,
                                       Np=1,
                                       Ts=100e-6,
                                       i_ref_seq_dq=i_ref_dq)

# Simulate the system
sim = Simulation(sys=sys, conv=conv, ctr=ctr, Ts_sim=5e-6)
sim.simulate(t_stop=0.2)
