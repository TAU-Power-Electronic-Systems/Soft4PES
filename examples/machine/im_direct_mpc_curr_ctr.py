"""
Example of direct model predictive control (MPC) for an induction machine drive system. The 
controller aims to track the stator current reference calculated based on the reference values of 
the stator flux magnitude and torque. The machine operates at a constant (nominal) speed.
"""

#pylint: disable=wrong-import-position
from types import SimpleNamespace
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
from soft4pes.control import mpc, common
from soft4pes.utils import Sequence
from soft4pes.sim import Simulation

# Define base values
base = model.machine.BaseMachine(Vm_R_SI=400,
                                 Im_R_SI=4.4,
                                 fm_R_SI=50,
                                 npp=1,
                                 pf=0.85)

# Define torque reference sequence
T_ref_seq = Sequence(
    np.array([0, 0.1, 0.1, 0.2]),
    np.array([1, 1, 0, 0]),
)
ref_seq = SimpleNamespace(T_ref_seq=T_ref_seq)

# Define induction machine parameters
im_params = model.machine.InductionMachineParameters(fs_SI=50,
                                                     pf=0.85,
                                                     Rs_SI=2.7,
                                                     Rr_SI=2.4,
                                                     Lls_SI=9.868e-3,
                                                     Llr_SI=11.777e-3,
                                                     Lm_SI=394.704e-3,
                                                     base=base)

# Define system models
conv = model.conv.Converter(v_dc_SI=600, nl=3, base=base)
sys = model.machine.InductionMachine(par=im_params,
                                     conv=conv,
                                     base=base,
                                     psiS_mag_ref=1,
                                     T_ref_init=T_ref_seq(0))

# Define solver to be enumeration based
solver = mpc.solvers.MpcEnum(conv=conv)

# Uncomment to use Branch-and-Bound solver
# solver = mpc.solvers.MpcBnB(conv=conv)

# Define controller
ctr = mpc.controllers.IMMpcCurrCtr(solver, lambda_u=10e-3, Np=1)
ctr_sys = common.ControlSystem(control_loops=[ctr], ref_seq=ref_seq, Ts=100e-6)

# Simulate system
sim = Simulation(sys=sys, ctr=ctr_sys, Ts_sim=5e-6)
sim.simulate(t_stop=0.2)
sim.save_data()
