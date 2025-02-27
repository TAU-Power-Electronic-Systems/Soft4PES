"""
Plotter for grid-forming control examples.
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_gfm_example(data, t_start=0):
    """
    Plot the grid-forming control example results.

    Parameters
    ----------
    data : SimpleNamespace
        The simulation data containing system and control data.
    t_start : float, optional
        The start time for plotting to exclude initial transients. Default is 0.
    """
    # Adjust the font size for all text elements
    plt.rcParams.update({'font.size': 14})

    # Extract time vectors and adjust for start time
    t_sim = data.sys.t - t_start
    t_ctr = data.ctr.t - t_start

    # Extract system state variables
    x = data.sys.x
    i_conv = x[:, 0:2]  # Converter currents
    ig = x[:, 2:4]  # Grid currents
    vc = x[:, 4:6]  # Capacitor voltages
    vg = data.sys.vg  # Grid voltages

    # Calculate power and capacitor voltage magnitude
    P = vg[:, 0] * ig[:, 0] + vg[:, 1] * ig[:, 1]
    P_ref = data.ctr.RFPSC.input.P_ref
    V_ref = data.ctr.RFPSC.input.V_ref
    Vc = np.sqrt(vc[:, 0]**2 + vc[:, 1]**2)

    # Define plot limits
    x_lim = [0, t_sim[-1]]

    # Create subplots
    fig, axs = plt.subplots(2, 1, figsize=(10, 6))

    # Plot power
    axs[0].plot(t_sim, P, label='P')
    axs[0].plot(t_ctr, P_ref, '--', color='black', label='P_ref')
    axs[0].set_xlim(x_lim)
    axs[0].set_xticklabels([])
    axs[0].set_ylim([-0.1, 1.1])
    axs[0].set_ylabel('P [p.u.]')
    axs[0].set_yticks(np.arange(0, 1.1, 0.25))
    axs[0].grid(True)
    axs[0].legend()

    # Plot capacitor voltage magnitude
    axs[1].plot(t_sim, Vc, label='Vc')
    axs[1].plot(t_ctr, V_ref, '--', color='black', label='V_ref')
    axs[1].set_xlim(x_lim)
    axs[1].set_xlabel('Time [s]')
    axs[1].set_ylim([0.75, 1.25])
    axs[1].set_ylabel(r'$||v_c||_2$ [p.u.]')
    axs[1].set_yticks(np.arange(0.8, 1.25, 0.2))
    axs[1].grid(True)
    axs[1].legend()

    # Align y-axis labels and adjust layout
    fig.align_ylabels()
    plt.tight_layout()
    plt.show()
