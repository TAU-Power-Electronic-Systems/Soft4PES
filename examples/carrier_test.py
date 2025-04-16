#pylint: disable=wrong-import-position

import sys as system
import os
import numpy as np
import matplotlib.pyplot as plt
## ---------------------------------- ##
# These allow using soft4pes from this folder ##
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python paths
system.path.append(parent_dir)
## ---------------------------------- ##

from soft4pes.control.modulation import CarrierPWMOld
from soft4pes.control.modulation import CarrierPWM

###################### SET SETTINGS HERE!!! ############
Ts_ctr = 100e-6
Ts_sim = 100e-6 / 10
t_stop = 0.02
nl = 2

# REFERENCE SIGNAL SETTINGS
f = 50
A = 1
phi = 0


#######################################################
# Dummy classes for testing purposes
class TestConv:
    """
    Dummy converter class for testing purposes.
    """

    def __init__(self, nl):
        self.nl = nl
        self.v_dc = 750  # Example DC voltage value


class TestSys:
    """
    Dummy system class for testing purposes.
    """

    def __init__(self, conv):
        self.conv = conv


# Create a carrier comparison object for reference
pmw = CarrierPWMOld(Ts_ctr, Ts_sim, nl)

# Create a converter and system object for testing
sys = TestSys(TestConv(nl))

# Create a CarrierPWM object for the simulation. This is the implementation we wish to include to Soft4PES
pwm2 = CarrierPWM()
pwm2.Ts = Ts_ctr

# Time vectors
t = np.arange(0, t_stop, Ts_sim)
t_ctr = np.arange(0, t_stop, Ts_ctr)

# Generate three-phase reference signals
ref = np.zeros(
    (len(t_ctr), 3))  # Initialize a 2D array for three-phase signals
ref[:, 0] = A * np.sin(2 * np.pi * f * t_ctr + phi)  # Phase A
ref[:, 1] = A * np.sin(2 * np.pi * f * t_ctr + phi - 2 * np.pi / 3)  # Phase B
ref[:, 2] = A * 0.5 * np.sin(
    2 * np.pi * f * t_ctr + phi + 2 * np.pi / 3)  # Phase C

# Preallocate data for plotting
carrier_val = np.zeros((len(t), nl - 1))
switch_pos = np.zeros((len(t), 3))
switch_pos2 = np.zeros((len(t), 3))

# Run simulation
i = 0
u_out = np.zeros(3)
for k in range(round(t_stop / Ts_ctr)):
    pwm2.input.u_abc = ref[k].copy()
    output = pwm2.execute(sys, k * Ts_ctr)
    t_switch, switch_array = output.t_switch, output.switch_pos
    k_switch = np.round(t_switch * Ts_ctr / Ts_sim)
    for index in range(round(Ts_ctr / Ts_sim)):
        carrier_val[i, 0] = pmw.lower_carrier.value
        if nl == 3:
            carrier_val[i, 1] = pmw.upper_carrier.value
        switch1 = pmw(ref[k].copy())
        switch_pos[i] = switch1

        if np.any(index == k_switch):
            u_abc = switch_array[index == k_switch]
            if u_abc.ndim == 2:
                u_abc = u_abc[-1]
        switch_pos2[i] = u_abc

        i = i + 1

# Plot results
plt.figure(figsize=(15, 15))
# Colors for reference signals and switch positions
colors = ['blue', 'blue', 'blue']

# Plot switch positions for each phase
for phase in range(3):
    plt.subplot(3, 1, phase + 1)
    plt.step(t_ctr,
             ref[:, phase],
             label=f'Reference signal Phase {phase + 1}',
             where='post',
             color='black',
             linewidth=1)
    for i in range(nl - 1):
        plt.step(t,
                 carrier_val[:, i],
                 where='post',
                 color='grey',
                 linewidth=1,
                 linestyle='-')
    plt.step(t,
             switch_pos[:, phase],
             where='post',
             label=f'Switch pos. carrier comparison',
             color=colors[phase],
             linewidth=1,
             linestyle='--')
    plt.step(t,
             switch_pos2[:, phase],
             where='post',
             label=f'Switch pos. calculated',
             color=colors[phase],
             linewidth=1)
    plt.title(f'PWM Phase {phase + 1}')
    plt.grid(True)
    plt.legend()

plt.xlabel('Time [s]')
plt.tight_layout()
plt.show()
