"""
Example of direct model predictive control (MPC) for a synchronous machine drive system. The 
controller aims to track the stator current reference calculated based on the reference values of 
the maximum torque per ampere (MTPA) trajectory and torque. The machine operates at a constant 
(nominal) speed.
"""

#pylint: disable=wrong-import-position
from types import SimpleNamespace
import sys as system
import os
import numpy as np
import matplotlib.pyplot as plt

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
# Example synchronous machine (https://ieeexplore.ieee.org/document/10227497)
base = model.machine.BaseMachine(Vm_R_SI=926,
                                 Im_R_SI=138,
                                 fm_R_SI=120,
                                 npp=4,
                                 pf=0.86)

# Define torque reference sequence
T_ref_seq = Sequence(
    np.array([0, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4, 0.5, 0.5, 0.6]),
    np.array([0, 0, 0.2, 0.2, 0.4, 0.4, 0.6, 0.6, 0.8, 0.8, 1, 1]),
)
ref_seq = SimpleNamespace(T_ref_seq=T_ref_seq)

# Define induction machine parameters
sm_params = model.machine.SynchronousMachineParameters(fs_SI=120,
                                                       pf_SI=0.86,
                                                       Rs_SI=0.046,
                                                       Lsd_SI=1.58e-3,
                                                       Lsq_SI=6.48e-3,
                                                       LambdaPM_SI=0.684,
                                                       base=base)

# Define system models
conv = model.conv.Converter(v_dc_SI=1500, nl=2, base=base)
sys = model.machine.SynchronousMachine(par=sm_params,
                                       conv=conv,
                                       base=base,
                                       T_ref_init=T_ref_seq(0))

# Define solver to be enumeration based
solver = mpc.solvers.MpcEnum(conv=conv)

# Define controller
ctr = mpc.controllers.SMMpcCurrCtr(solver,
                                   lambda_u=1e-3,
                                   Np=2,
                                   disc_method='forward_euler')
ctr_sys = common.ControlSystem(control_loops=[ctr], ref_seq=ref_seq, Ts=1e-4)

# Simulate system
sim = Simulation(sys=sys,
                 ctr=ctr_sys,
                 Ts_sim=1e-4,
                 disc_method='forward_euler')
sim.simulate(t_stop=0.6)
sim.save_data()
