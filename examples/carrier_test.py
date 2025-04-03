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

from soft4pes.sim.carrier_pwm import CarrierPWM

# Sampling times
Ts_ctr = 1 / (30 * 50)
Ts_sim = 10e-6

# Init carrier module
nl = 3
pmw = CarrierPWM(Ts_ctr, Ts_sim, nl)

# Time vector
t_stop = 0.02
t = np.arange(0, t_stop, Ts_sim)

# Reference signal
f = 50
A = 0.9
phi = 0
ref = np.zeros((len(t), 3))  # Initialize a 2D array for three-phase signals

# Generate three-phase signals
ref[:, 0] = A * np.sin(2 * np.pi * f * t + phi)  # Phase A
ref[:, 1] = A * np.sin(2 * np.pi * f * t + phi - 2 * np.pi / 3)  # Phase B
ref[:, 2] = A * np.sin(2 * np.pi * f * t + phi + 2 * np.pi / 3)  # Phase C

# Preallocate data for plotting
carrier_val = np.zeros((len(t), nl - 1))
switch_pos = np.zeros((len(t), 3))

# Run simulation
for i, time in enumerate(t):
    carrier_val[i, 0] = pmw.lower_carrier.value
    if nl == 3:
        carrier_val[i, 1] = pmw.upper_carrier.value
    switch_pos[i] = pmw(ref[i])

# Plot results
plt.figure(figsize=(15, 15))
# Colors for reference signals and switch positions
colors = ['blue', 'green', 'orange']

# Plot reference signals and carrier signals
plt.subplot(4, 1, 1)
for phase in range(3):
    plt.step(t,
             ref[:, phase],
             label=f'Reference signal Phase {phase + 1}',
             color=colors[phase],
             linewidth=2)
for i in range(nl - 1):
    plt.step(t,
             carrier_val[:, i],
             where='post',
             label=f'Carrier {i+1}',
             color='grey',
             linewidth=1,
             linestyle='-')
plt.title('Reference signal and carrier signals')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.grid(True)
plt.legend()

# Plot switch positions for each phase
for phase in range(3):
    plt.subplot(4, 1, phase + 2)
    plt.step(t,
             switch_pos[:, phase],
             where='post',
             label=f'PWM signal Phase {phase + 1}',
             color=colors[phase],
             linewidth=2)
    plt.title(f'PWM signal Phase {phase + 1}')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()

plt.tight_layout()
plt.show()

# class SamplingWaveforms:
#     """
#     Sampling waveforms based on carrier signals.

#     Attributes
#     ----------
#     sampling_value : ndarray
#         Array to store sampled waveform values [p.u.].
#     ref_val : ndarray
#         Reference waveform values [p.u.].
#     time_index : int
#         Current time index in the simulation.
#     last_sampled_value : ndarray
#         Last sampled values of the reference waveforms [p.u.].
#     carriers : list of Carrier
#         List of Carrier objects [p.u.].
#     eps : float
#         Tolerance for carrier signal comparison.
#     """

#     def __init__(self, ref_val, Ts_car, Ts_sim, n1):
#         """
#         Initialize SamplingWaveforms.

#         Parameters
#         ----------
#         ref_val : ndarray
#             Reference waveform values [p.u.].
#         Ts_car : float
#             Period time of carrier signal [s].
#         Ts_sim : float
#             Simulation step time [s].
#         n1 : int
#             Number of levels (2 or 3).
#         """
#         self.sampling_value = np.zeros(
#             ref_val.shape)  # Initialize the sampling value array
#         self.ref_val = ref_val  # Set the reference waveform values
#         self.time_index = 0  # Initialize the time index
#         self.last_sampled_value = np.zeros(
#             ref_val.shape[0])  # Initialize the last sampled value array
#         self.carriers = [Carrier(Ts_car, Ts_sim, -1, 1, 1)] if n1 == 2 else [
#             Carrier(Ts_car, Ts_sim, -1, 0, -0.5),
#             Carrier(Ts_car, Ts_sim, 0, 1, 0.5)
#         ]  # Initialize carriers based on the number of levels
#         self.eps = self.carriers[0].step  # Set the tolerance for comparison

#     def sample(self):
#         """
#         Sample the reference waveforms based on carrier signals.

#         Returns
#         -------
#         ndarray
#             Sampled waveform values [p.u.].
#         """
#         for carrier in self.carriers:  # Iterate through each carrier
#             carrier_value = carrier.value  # Get the current value of the carrier
#             if abs(carrier_value - 1) < self.eps or abs(
#                     carrier_value + 1
#             ) < self.eps:  # Check if the carrier value is close to its limits
#                 self.last_sampled_value = self.ref_val[:, self.
#                                                        time_index]  # Update the last sampled value with the current reference value
#         self.sampling_value[:, self.
#                             time_index] = self.last_sampled_value  # Store the last sampled value in the sampling value array
#         self.time_index += 1  # Increment the time index
#         return self.sampling_value  # Return the sampling value array

# # Simulation class to run and plot the PWM simulation
# class SimulationPWM:
#     """
#     Run and plot the PWM simulation.

#     Attributes
#     ----------
#     Ts_sim : float
#         Simulation step time [s].
#     stop_time : float
#         Total simulation time [s].
#     Ts_car : float
#         Period time of carrier signal [s].
#     n1 : int
#         Number of levels (2 or 3).
#     waveforms : list of dict
#         List of waveform specifications.
#     time : ndarray
#         Array of time steps.
#     ref_waveforms : ndarray
#         Reference waveform values [p.u.].
#     sampling_waveforms : SamplingWaveforms
#         Sampling waveforms object.
#     carrier_comparison : CarrierComparison
#         Carrier comparison object.
#     """

#     def __init__(self, Ts_sim, stop_time, Ts_car, n1, waveforms):
#         """
#         Initialize Simulation.

#         Parameters
#         ----------
#         Ts_sim : float
#             Simulation step time [s].
#         stop_time : float
#             Total simulation time [s].
#         Ts_car : float
#             Period time of carrier signal [s].
#         n1 : int
#             Number of levels (2 or 3).
#         waveforms : list of dict
#             List of waveform specifications.
#         """
#         self.Ts_sim = Ts_sim  # Set the simulation step time
#         self.stop_time = stop_time  # Set the total simulation time
#         self.Ts_car = Ts_car  # Set the period time of the carrier signal
#         self.n1 = n1  # Set the number of levels (2 or 3)
#         self.waveforms = waveforms  # Set the waveform specifications
#         self.time = np.arange(0, stop_time,
#                               Ts_sim)  # Create an array of time steps
#         self.ref_waveforms = self.generate_ref_waveforms(
#         )  # Generate the reference waveforms
#         self.sampling_waveforms = SamplingWaveforms(
#             self.ref_waveforms, Ts_car, Ts_sim,
#             n1)  # Initialize the SamplingWaveforms object
#         self.carrier_comparison = CarrierComparison(
#             Ts_car, Ts_sim, n1)  # Initialize the CarrierComparison object

#     def generate_ref_waveforms(self):
#         """
#         Generate reference waveforms based on the specifications.

#         Returns
#         -------
#         ndarray
#             Reference waveform values.
#         """
#         ref_waveforms = np.zeros(
#             (len(self.waveforms),
#              len(self.time)))  # Initialize the reference waveform array
#         for i, waveform in enumerate(
#                 waveforms):  # Iterate through each waveform specification
#             if waveform[
#                     'type'] == 'sine':  # Check if the waveform type is sinusoidal
#                 f = waveform['frequency']
#                 Amp = waveform['amplitude']
#                 phase = waveform['phase']
#                 omega = 2 * np.pi * f
#                 ref_waveforms[i] = Amp * np.sin(
#                     omega * self.time +
#                     phase)  # Generate a sinusoidal waveform
#             elif waveform['type'] == 'custom':
#                 ref_waveforms[i] = waveform['function'](self.time)

#         return ref_waveforms  # Return the reference waveforms

#     def run(self):
#         num_phases = self.ref_waveforms.shape[0]
#         sampled_waveforms = np.zeros((num_phases, len(self.time)))
#         carrier_signals = np.zeros(
#             (len(self.sampling_waveforms.carriers), len(self.time)))
#         pwm_signals = np.zeros((num_phases, len(self.time)))

#         for i, t in enumerate(self.time):
#             sampled_waveforms[:, i] = self.sampling_waveforms.sample()[:, i]
#             for j, carrier in enumerate(self.sampling_waveforms.carriers):
#                 carrier_value = carrier()
#                 carrier_signals[j, i] = carrier_value
#                 if self.n1 == 2:
#                     for k in range(num_phases):
#                         pwm_signals[k, i] = self.carrier_comparison(
#                             sampled_waveforms[k, i], carrier_value)
#                 elif self.n1 == 3:
#                     lower_carrier, upper_carrier = [
#                         c() for c in self.sampling_waveforms.carriers
#                     ]
#                     for k in range(num_phases):
#                         pwm_signals[k, i] = self.carrier_comparison(
#                             sampled_waveforms[k, i],
#                             [lower_carrier, upper_carrier])

#         self.sampled_waveforms = sampled_waveforms
#         self.carrier_signals = carrier_signals
#         self.pwm_signals = pwm_signals

#     def plot(self):
#         num_phases = self.ref_waveforms.shape[0]
#         plt.figure(figsize=(15, 10))
#         plt.subplot(2, 1, 1)
#         colors = [
#             'blue', 'green', 'red', 'orange', 'purple', 'brown', 'pink',
#             'gray', 'olive', 'cyan'
#         ]
#         for i in range(num_phases):
#             plt.plot(self.time,
#                      self.ref_waveforms[i],
#                      label=f'Phase {i+1}',
#                      color=colors[i % len(colors)],
#                      linewidth=2)
#             plt.plot(self.time,
#                      self.sampled_waveforms[i],
#                      label=f'Sampled Phase {i+1}',
#                      color=colors[i % len(colors)],
#                      linestyle='--',
#                      linewidth=2)
#         for i, carrier_signal in enumerate(self.carrier_signals):
#             plt.step(self.time,
#                      carrier_signal,
#                      where='post',
#                      label=f'Carrier {i+1}',
#                      color='grey',
#                      linewidth=1,
#                      linestyle='-')
#         plt.title('Waveforms, Carrier Signals, Sampled Waveforms')
#         plt.xlabel('Time [s]')
#         plt.ylabel('Amplitude')
#         plt.grid(True)
#         # plt.legend()
#         # plt.subplot(2, 1, 2)
#         # for i in range(num_phases):
#         #     plt.plot(self.time,
#         #              self.pwm_signals[i],
#         #              label=f'PWM Signal {i+1}',
#         #              color=colors[i % len(colors)],
#         #              linewidth=3)
#         # plt.title('PWM Signals')
#         # plt.xlabel('Time [s]')
#         # plt.ylabel('Amplitude')
#         # plt.legend()

#         plt.tight_layout()
#         plt.show()

# # Example usage
# Ts_sim = 10e-6
# stop_time = 10
# Ts_car = 1 / (30 * 50)
# n1 = 3

# waveforms = [{
#     'type':
#     'custom',
#     'function':
#     lambda t: 0.9 * np.sin(2 * np.pi * 50 * t) + 0.1 * np.cos(2 * np.pi * 2000
#                                                               * t)
# }, {
#     'type':
#     'custom',
#     'function':
#     lambda t: 0.8 * np.sin(2 * np.pi * 50 * t - 2 * np.pi / 3) + 0.05 * np.cos(
#         2 * np.pi * 1400 * t)
# }]

# sim = SimulationPWM(Ts_sim, stop_time, Ts_car, n1, waveforms)
# sim.run()
# sim.plot()
