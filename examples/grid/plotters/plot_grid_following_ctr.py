"""
Plotter for grid-following control examples.
"""

import numpy as np
import matplotlib.pyplot as plt
from soft4pes.utils import alpha_beta_2_dq

def plot_gfl_example(data, t_start=0):
    """
    Plot the grid-following control example results.

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

    # Converter current (always first two states)
    i_conv = x[:, 0:2]

    # Grid current: if extra states exist, take columns 2:4, else fall back to i_conv
    ig = x[:, 2:4] if x.shape[1] >= 4 else i_conv

    # Current-reference: prefer LConvCurrCtr, else fall back to LCLConvCurrCtr
    i_conv_ref_dq = None
    ctr = getattr(data, "ctr", None)

    if ctr is not None:
        # Try LConvCurrCtr
        lctr = getattr(ctr, "LConvCurrCtr", None)
        if lctr is not None and hasattr(lctr, "input"):
            i_conv_ref_dq = getattr(lctr.input, "ig_ref_dq", None)

        # Fallback to LCLConvCurrCtr if needed
        if i_conv_ref_dq is None:
            lclctr = getattr(ctr, "LCLConvCurrCtr", None)
            if lclctr is not None and hasattr(lclctr, "input"):
                i_conv_ref_dq = getattr(lclctr.input, "ig_ref_dq", None)
            if i_conv_ref_dq is None:
                raise AttributeError(
                    "Could not find ig_ref_dq in LConvCurrCtr or LCLConvCurrCtr inputs."
                    )
    vg = data.sys.vg  # Grid voltages

    # Calculate power and capacitor voltage magnitude
    P = vg[:, 0] * ig[:, 0] + vg[:, 1] * ig[:, 1]
    Q = vg[:, 1] * ig[:, 0] - vg[:, 0] * ig[:, 1]
    P_ref = data.ctr.GridCurrRefGen.input.P_ref
    Q_ref = data.ctr.GridCurrRefGen.input.Q_ref
    
    # Calculate the transformation angle
    theta = np.arctan2(vg[:, 1], vg[:, 0])
    # Get dq frame current (converter current equals grid current due to lack of a filter)
    i_conv_dq = np.empty_like(i_conv)
    for k in range(i_conv.shape[0]):
        i_conv_dq[k, :] = alpha_beta_2_dq(i_conv[k, :], theta[k])

    # Define plot limits
    x_lim = [0, t_sim[-1]]

    # Create subplots
    fig, axs = plt.subplots(2, 1, figsize=(10, 6))

    # Plot power
    axs[0].plot(t_sim, P, color='blue', label='P')
    axs[0].plot(t_ctr, P_ref, '--', color='blue', label='P_ref')
    axs[0].plot(t_sim, Q, color='red', label='Q')
    axs[0].plot(t_ctr, Q_ref, '--', color='red', label='Q_ref') 
    axs[0].set_xlim(x_lim)
    axs[0].set_xticklabels([])
    axs[0].set_ylabel('P and Q [p.u.]')
    axs[0].grid(True)
    axs[0].legend()

    # Plot capacitor voltage magnitude
    axs[1].plot(t_sim, i_conv_dq[:, 0], color='blue', label='id')
    axs[1].plot(t_ctr, i_conv_ref_dq[:, 0], '--', color='blue', label='i_ref_d')
    axs[1].plot(t_sim, i_conv_dq[:, 1], color='red', label='iq')
    axs[1].plot(t_ctr, i_conv_ref_dq[:, 1], '--', color='red', label='i_ref_q')
    axs[1].set_xlim(x_lim)
    axs[1].set_xlabel('Time [s]')
    axs[1].set_ylabel('i_dq [p.u.]')
    axs[1].grid(True)
    axs[1].legend()

    # Align y-axis labels and adjust layout
    fig.align_ylabels()
    plt.tight_layout()
    plt.show()
