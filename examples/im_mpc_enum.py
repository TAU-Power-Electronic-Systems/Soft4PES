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

from soft4pes import model
from soft4pes.control import mpc
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

base = model.machine.BaseMachine(Vr=400, Ir=4.4, fr=50, npp=1, pf=0.85)

# The torque reference has two columns, as the Sequence class does not yet support n-dimensional
# sequences. The reference is saved at the first column.
T_ref_seq = Sequence(np.array([0, 0.1, 0.1, 0.2]),
                     np.array([[1, 0], [1, 0], [0.5, 0], [0.5, 0]]))

sys = model.machine.InductionMachine(f=50,
                                     pf=0.85,
                                     Rs=2.7,
                                     Rr=2.4,
                                     Lls=9.868e-3,
                                     Llr=11.777e-3,
                                     Lm=394.704e-3,
                                     base=base,
                                     psiS_mag_ref=1,
                                     T_ref_init=T_ref_seq(0)[0])

conv = model.conv.Converter(v_dc=600, nl=3, base=base)

solver = mpc.solvers.MpcEnum(conv=conv)
ctr = mpc.controllers.IMMpcCurrCtr(solver,
                                   lambda_u=10e-3,
                                   Np=1,
                                   Ts=100e-6,
                                   T_ref=T_ref_seq)

sim = Simulation(sys=sys, conv=conv, ctr=ctr, Ts_sim=5e-6)

start_time = time.time()

sim.simulate(t_stop=0.2)

end_time = time.time()
execution_time = end_time - start_time
print("Execution time:", execution_time, "seconds")
