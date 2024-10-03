"""
Example of controlling an induction machine with direct model predictive control MPC.
The controller aims to track the stator current reference. The current reference is calculated based
on a constant stator flux magnitude reference and a torque reference sequence. The machine operates 
at a constant (nominal) speed.
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
base = model.machine.BaseMachine(Vr=400, Ir=4.4, fr=50, npp=1, pf=0.85)

# Define torque reference sequence
T_ref_seq = Sequence(
    np.array([0, 0.1, 0.1, 0.2]),
    np.array([1, 1, 0.5, 0.5]),
)

# Define system models
sys = model.machine.InductionMachine(f=50,
                                     pf=0.85,
                                     Rs=2.7,
                                     Rr=2.4,
                                     Lls=9.868e-3,
                                     Llr=11.777e-3,
                                     Lm=394.704e-3,
                                     base=base,
                                     psiS_mag_ref=1,
                                     T_ref_init=T_ref_seq(0))

conv = model.conv.Converter(v_dc=600, nl=3, base=base)

# Define solver to be enumeration based
solver = mpc.solvers.MpcEnum(conv=conv)

# Comment in to use Branch and Bound solver
# solver = mpc.solvers.MpcBnB(conv=conv)

# Define controller
ctr = mpc.controllers.IMMpcCurrCtr(solver,
                                   lambda_u=10e-3,
                                   Np=1,
                                   Ts=100e-6,
                                   T_ref=T_ref_seq)

# Simulate system
sim = Simulation(sys=sys, conv=conv, ctr=ctr, Ts_sim=5e-6)
sim.simulate(t_stop=0.2)
