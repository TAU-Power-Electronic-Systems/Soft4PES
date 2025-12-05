"""
Plotting functionality for system states and control signals.
"""

import matplotlib.pyplot as plt
import numpy as np

from soft4pes.model.grid import RLGrid
from soft4pes.model.machine import InductionMachine, PMSM

from soft4pes.utils.conversions import (alpha_beta_2_abc, alpha_beta_2_dq,
                                        abc_2_alpha_beta)


class Plotter:
    """
    This class provides methods to plot system states, switching behavior, and control signals. It 
    supports multiple reference frames (abc, alpha-beta, dq). The main functions of the class are:
    - plot_states: Plot system states in specified reference frames.
    - plot_control_signals_grid: Plot control signals for grid-connected systems (active/reactive
      power, voltage magnitude).
    - plot_control_signals_machine: Plot control signals for electric machines (torque).
    - show_all: Display all generated plots.
    
    Parameters
    ----------
    data : SimulationData
        Simulation data containing system and controller results
    sys : System
        System object with state mapping and configuration
    t_start : float, optional
        Start time for all plots (default: 0)
    t_end : float, optional
        End time for all plots (default: None, uses full simulation time)
    
    Examples
    --------
    >>> plotter = SystemPlotter(data, sys, t_start=0, t_end=0.2)
    >>> plotter.plot_states(['vc', 'ig'], frames=['abc', 'alpha-beta'])
    >>> plotter.plot_control_signals_grid(plot_P=True, plot_Q=True, P_ref=P_ref_seq)
    >>> plotter.show_all()
    """

    def __init__(self, data, sys, t_start=0, t_end=None):
        self.data = data
        self.sys = sys
        self.t_start = t_start
        self.t_end = t_end
        self._figures = []

        # Define consistent phase colors: Blue, Red, Green for phases a, b, c
        self.phase_colors = [
            [0, 0, 1],  # Blue for phase a / alpha / d
            [1, 0, 0],  # Red for phase b / beta / q  
            [0, 0.5, 0],  # Green for phase c
        ]

        # Define signal-specific colors for control plots
        self.signal_colors = {
            'reference': [0.55, 0.55, 0.55],  # Grey for all reference signals
            'P': [0.75, 0, 0.75],  # Magenta for active power
            'Q': [0, 0.5, 0],  # Green for reactive power
            'V': [0, 0, 1],  # Blue for voltage magnitude
            'torque': [0.75, 0, 0.75]  # Magenta for torque
        }

    def _register_figure(self, fig):
        """Store figure to keep it alive until show_all() is called."""
        self._figures.append(fig)

    def _get_time_mask_and_plot(self, t_sys, t_start, t_end, n_vars):
        """Create time mask and subplot structure for control signal plots."""
        t_idx = (t_sys >= t_start)
        if t_end is not None:
            t_idx = t_idx & (t_sys <= t_end)
        t_plot = t_sys[t_idx]
        fig, axs = plt.subplots(n_vars,
                                1,
                                figsize=(8, 2.5 * n_vars),
                                sharex=True)
        self._register_figure(fig)
        if n_vars == 1:
            axs = [axs]
        return t_idx, t_plot, axs

    def _plot_signal(self, ax, t_plot, y, label, signal_type=None):
        """Plot a signal with specified color based on signal type."""
        color = self.signal_colors.get(signal_type, None)
        ax.plot(t_plot, y, label=label, color=color)

    def _plot_reference(self, ax, ref_seq, label, linestyle):
        """Plot a reference sequence with grey color and specified linestyle."""
        if ref_seq is not None:
            ax.plot(ref_seq.times,
                    ref_seq.values,
                    label=label,
                    linestyle=linestyle,
                    color=self.signal_colors['reference'])

    def _finalize_axis(self, ax, t_start, t_end, t_sys):
        """Apply consistent formatting to subplot axes."""
        handles, labels = ax.get_legend_handles_labels()
        if labels:
            ax.legend(loc='upper left')
        ax.grid(True)
        ax.set_xlim([t_start, t_end if t_end is not None else t_sys[-1]])

    def plot_control_signals_grid(self,
                                  plot_P=False,
                                  plot_Q=False,
                                  plot_V=False,
                                  P_ref=None,
                                  Q_ref=None,
                                  V_ref=None):
        """
        Plot grid-connected system control signals (active/reactive power, voltage magnitude). The 
        voltage magnitude corresponds to converter output voltage (no LCL filter) or capacitor
        voltage (with LCL filter).

        Parameters
        ----------
        plot_P : bool, optional
            Plot active power P (default: False)
        plot_Q : bool, optional
            Plot reactive power Q (default: False)
        plot_V : bool, optional
            Plot voltage magnitude (converter or capacitor) (default: False)
        P_ref : Sequence, optional
            Active power reference trajectory
        Q_ref : Sequence, optional
            Reactive power reference trajectory
        V_ref : Sequence, optional
            Voltage magnitude reference trajectory
        
        Notes
        -----
        - If both plot_P and plot_Q are True, they are plotted together
        - Voltage plots either converter voltage (if no capacitor) or capacitor voltage
        - Power is calculated as:
          P = vg_alpha*ig_alpha + vg_beta*ig_beta, 
          Q = vg_beta*ig_alpha - vg_alpha*ig_beta
        """
        if not hasattr(self.data.sys, 'vg'):
            raise KeyError(
                "No 'vg' attribute in system. This system is not a grid.")

        x_data = self.data.sys.x
        t_sys = self.data.sys.t
        state_map = self.sys.state_map
        vg = self.data.sys.vg

        variables = []
        if plot_P and plot_Q:
            variables.append('PQ')
        elif plot_P:
            variables.append('P')
        elif plot_Q:
            variables.append('Q')
        if plot_V:
            variables.append('V')

        if not variables:
            print("No variables selected for plotting.")
            return

        t_idx, t_plot, axs = self._get_time_mask_and_plot(
            t_sys, self.t_start, self.t_end, len(variables))

        # Calculate instantaneous power if needed
        if any(var in ['PQ', 'P', 'Q'] for var in variables):
            ig = x_data[:, state_map['ig']]
            P = vg[t_idx, 0] * ig[t_idx, 0] + vg[t_idx, 1] * ig[t_idx, 1]
            Q = vg[t_idx, 1] * ig[t_idx, 0] - vg[t_idx, 0] * ig[t_idx, 1]

        for i, var in enumerate(variables):
            ax = axs[i]
            if var == 'PQ':
                self._plot_signal(ax, t_plot, P, r"$P$", signal_type='P')
                self._plot_reference(ax,
                                     P_ref,
                                     r"$P_{\mathrm{ref}}$",
                                     linestyle='--')
                self._plot_signal(ax, t_plot, Q, r"$Q$", signal_type='Q')
                self._plot_reference(ax,
                                     Q_ref,
                                     r"$Q_{\mathrm{ref}}$",
                                     linestyle='-.')
                ax.set_ylabel(r"Power [p.u.]")
            elif var == 'P':
                self._plot_signal(ax, t_plot, P, r"$P$", signal_type='P')
                self._plot_reference(ax,
                                     P_ref,
                                     r"$P_{\mathrm{ref}}$",
                                     linestyle='--')
                ax.set_ylabel(r"Power [p.u.]")
            elif var == 'Q':
                self._plot_signal(ax, t_plot, Q, r"$Q$", signal_type='Q')
                self._plot_reference(ax,
                                     Q_ref,
                                     r"$Q_{\mathrm{ref}}$",
                                     linestyle='--')
                ax.set_ylabel(r"Power [p.u.]")
            elif var == 'V':
                # Determine voltage source: converter output or capacitor
                if 'vc' not in state_map:
                    # Plot converter voltage magnitude
                    v_abc = self.data.sys.u_abc * self.sys.conv.v_dc / 2
                    v_alpha_beta = np.array(
                        [abc_2_alpha_beta(v) for v in v_abc])
                    V_mag = np.linalg.norm(v_alpha_beta[t_idx, :], axis=1)
                    label = r"$V_{\mathrm{conv}}$"
                    ref_label = r"$V_{\mathrm{conv,ref}}$"
                else:
                    # Plot capacitor voltage magnitude
                    vc = x_data[:, state_map['vc']]
                    V_mag = np.linalg.norm(vc[t_idx, :], axis=1)
                    label = r"$V_c$"
                    ref_label = r"$V_{c,\mathrm{ref}}$"

                self._plot_signal(ax, t_plot, V_mag, label, signal_type='V')
                self._plot_reference(ax, V_ref, ref_label, linestyle='--')
                ax.set_ylabel(r"Voltage [p.u.]")
            self._finalize_axis(ax, self.t_start, self.t_end, t_sys)

    def plot_control_signals_machine(self, plot_T=False, T_ref=None):
        """
        Plot machine control signals (electromagnetic torque).
        
        Parameters
        ----------
        plot_T : bool, optional
            Plot electromagnetic torque Te (default: False)
        T_ref : Sequence, optional
            Torque reference trajectory
        """
        t_sys = self.data.sys.t

        variables = []
        if plot_T:
            variables.append('Te')

        if not variables:
            print("No variables selected for plotting.")
            return

        t_idx, t_plot, axs = self._get_time_mask_and_plot(
            t_sys, self.t_start, self.t_end, len(variables))

        for i, var in enumerate(variables):
            ax = axs[i]
            if var == 'Te':
                if hasattr(self.data.sys, 'Te'):
                    Te = self.data.sys.Te
                else:
                    raise KeyError(
                        "System is not a machine (no Te available).")
                self._plot_signal(ax,
                                  t_plot,
                                  Te[t_idx],
                                  r"$T_e$",
                                  signal_type='torque')
                self._plot_reference(ax,
                                     T_ref,
                                     r"$T_{\mathrm{ref}}$",
                                     linestyle='--')
                ax.set_ylabel(r"$T_e [p.u.]$")
            self._finalize_axis(ax, self.t_start, self.t_end, t_sys)

        axs[-1].set_xlabel("Time [s]")
        plt.tight_layout()

    def plot_states(self,
                    states_to_plot,
                    frames=None,
                    plot_u_abc_ref=False,
                    plot_u_abc=False):
        """
        Plot system states in specified reference frames. Moreover, the modulating signal u_abc_ref
        and/or the actual converter output can be plotted. In case modulator is not used, 
        u_abc_ref=u_abc. 

        Parameters
        ----------
        states_to_plot : list of str
            List of state names to plot (e.g., ['vc', 'ig', 'i_conv']). The existing states can be
            confirmed by checking the model class documentation. 
        frames : list of str, optional
            Reference frames for each state ('abc', 'alpha-beta', 'dq').
            If None, defaults to 'alpha-beta' for all states. The dq-frame is aligned with 
            - the grid voltage for grid-connected systems 
            - the rotor flux for induction machines
            - the rotor angle for PMSMs
        plot_u_abc_ref : bool, optional
            Plot modulating signal u_abc_ref in one subplot (default: False)
        plot_u_abc : bool, optional
            Plot actual converter output u_abc in separate subplots (default: False)
        
        Examples
        --------
        >>> plotter.plot_states(['vc', 'ig'], frames=['abc', 'alpha-beta'])
        >>> plotter.plot_states(['i_conv'], frames=['dq'], plot_u_abc=True)
        """
        data_sys = self.data.sys
        data_ctr = self.data.ctr
        t_sys = data_sys.t
        t_ctr = data_ctr.t

        # Default to alpha-beta frame for all states if not specified
        if frames is None:
            frames = ['alpha-beta'] * len(states_to_plot)

        t_idx_sys, t_plot_sys = self._get_time_mask(t_sys, self.t_start,
                                                    self.t_end)
        t_idx_ctr, t_plot_ctr = self._get_time_mask(t_ctr, self.t_start,
                                                    self.t_end)

        # Convert states to requested reference frames
        state_data = self._get_masked_states_in_frames(states_to_plot, frames,
                                                       t_idx_sys)

        n_states = len(states_to_plot)
        n_plots = n_states + (1 if plot_u_abc_ref else 0) + (3 if plot_u_abc
                                                             else 0)

        # Configure subplot heights: normal for states/u_abc_ref, smaller for individual u_abc
        heights = [1] * n_states
        if plot_u_abc_ref:
            heights.append(1)
        if plot_u_abc:
            heights.extend([0.3, 0.3, 0.3])

        fig, axs = plt.subplots(n_plots,
                                1,
                                figsize=(8, sum(heights) * 3),
                                gridspec_kw={'height_ratios': heights},
                                sharex=True)
        self._register_figure(fig)
        if n_plots == 1:
            axs = [axs]

        # Plot system states
        for i, (state, frame) in enumerate(zip(states_to_plot, frames)):
            y = state_data[(state, frame)]
            ax = axs[i]
            ref_frame_subscripts = self._get_frame_components(
                frame, y.shape[1])

            for j, frame_subscript in enumerate(ref_frame_subscripts):
                label = self._make_label(state, frame_subscript)
                # Apply consistent colors based on reference frame
                if frame == 'abc' and j < len(self.phase_colors):
                    color = self.phase_colors[j]
                elif frame in ['alpha-beta', 'dq'] and j < 2:
                    color = self.phase_colors[j]  # Blue for α/d, Red for β/q
                else:
                    color = None  # Use matplotlib default colors
                ax.plot(t_plot_sys,
                        y[:, j],
                        label=label,
                        color=color,
                        linewidth=1)

            state_label = self._make_label(state) + " [p.u.]"
            ax.set_ylabel(state_label)
            ax.set_xlim([
                self.t_start,
                self.t_end if self.t_end is not None else t_sys[-1]
            ])
            ax.grid(True)
            ax.legend(loc='upper left')

        current_subplot = n_states

        # Plot reference voltage waveforms (all phases in one subplot)
        if plot_u_abc_ref:
            u_abc = data_ctr.u_abc_ref[t_idx_ctr, :]
            phase_labels = ['a', 'b', 'c']
            ax = axs[current_subplot]
            for phase in range(3):
                ax.plot(t_plot_ctr,
                        u_abc[:, phase],
                        label=fr"$u_{{{phase_labels[phase]},\mathrm{{ref}}}}$",
                        color=self.phase_colors[phase],
                        linewidth=0.8)
            ax.set_ylabel(r"$u_{\mathrm{abc,ref}}$")
            ax.grid(True)
            ax.legend(loc='upper left')
            ax.set_xlim([
                self.t_start,
                self.t_end if self.t_end is not None else t_sys[-1]
            ])
            current_subplot += 1

        # Plot actual voltage waveforms (separate subplot per phase)
        if plot_u_abc:
            u_abc = data_sys.u_abc[t_idx_sys, :]
            phase_labels = ['a', 'b', 'c']
            for phase in range(3):
                ax = axs[current_subplot + phase]
                ax.step(t_plot_sys,
                        u_abc[:, phase],
                        color=self.phase_colors[phase],
                        linewidth=0.8,
                        where='post')
                ax.set_ylabel(fr"$u_{{{phase_labels[phase]}}}$")
                ax.grid(True)
                ax.set_xlim([
                    self.t_start,
                    self.t_end if self.t_end is not None else t_sys[-1]
                ])

        axs[-1].set_xlabel("Time [s]")
        plt.tight_layout()

    def show_all(self):
        """
        Display all registered figures and keep them open.
        
        This method should be called after creating all desired plots to display
        them simultaneously. Figures remain open until manually closed by the user.
        """
        plt.show()

    def _get_time_mask(self, t, t_start, t_end):
        """
        Create boolean mask for time vector within specified window.
        
        Parameters
        ----------
        t : ndarray
            Time vector
        t_start : float
            Start time
        t_end : float or None
            End time (if None, use full time range)
            
        Returns
        -------
        t_idx : ndarray
            Boolean mask for time indices
        t_plot : ndarray
            Masked time vector
        """
        t_idx = (t >= t_start)
        if t_end is not None:
            t_idx = t_idx & (t <= t_end)
        t_plot = t[t_idx]
        return t_idx, t_plot

    def _get_masked_states_in_frames(self, states_to_plot, frames, t_idx):
        """
        Extract and convert states to specified reference frames.

        Parameters
        ----------
        states_to_plot : list of str
            State names to extract
        frames : list of str
            Target reference frames for each state
        t_idx : ndarray
            Boolean mask for time indices

        Returns
        -------
        dict
            Dictionary mapping (state, frame) tuples to converted data arrays
        """
        data_sys = self.data.sys
        x = data_sys.x
        state_map = self.sys.state_map
        result = {}
        for state, frame in zip(states_to_plot, frames):
            if state not in state_map:
                available = ', '.join(state_map.keys())
                raise KeyError(
                    f"State '{state}' not found in state_map. Available states: {available}"
                )
            idx_state = state_map[state]
            quantity_ab = x[:, idx_state]
            converted = self._to_frame(quantity_ab, frame)
            result[(state, frame)] = converted[t_idx, ...]
        return result

    def _get_frame_components(self, frame, n_comp):
        """Get subscript labels for reference frame components."""
        frame_letters = {
            'alpha-beta': [r'\alpha', r'\beta'],
            'abc': ['a', 'b', 'c'],
            'dq': ['d', 'q']
        }
        return frame_letters.get(frame, [str(j) for j in range(n_comp)])

    def _make_label(self, state, comp=None):
        """
        Generate LaTeX-formatted labels for states and components.
        
        Handles special cases for flux linkages (psiR, psiS) and composite
        state names with underscores.
        """
        if state in ['psiR', 'psiS']:
            if comp is not None:
                return fr"$\psi_{{{state[-1]},{comp}}}$"
            else:
                return fr"$\psi_{{{state[-1]}}}$"
        elif '_' in state:
            var, sub = state.split('_', 1)
            if comp is not None:
                return fr"${var}_{{{sub},{comp}}}$"
            else:
                return fr"${var}_{{{sub}}}$"
        elif len(state) == 2:
            if comp is not None:
                return fr"${state[0]}_{{{state[1]},{comp}}}$"
            else:
                return fr"${state[0]}_{{{state[1]}}}$"
        else:
            if comp is not None:
                return fr"${state}_{{{comp}}}$"
            else:
                return fr"${state}$"

    def _to_frame(self, quantity_ab, frame):
        """
        Convert quantities from alpha-beta to specified reference frame.
        
        Parameters
        ----------
        quantity_ab : ndarray
            Data in alpha-beta coordinates (N x 2)
        frame : str
            Target reference frame ('alpha-beta', 'abc', 'dq')
        
        Returns
        -------
        ndarray
            Converted data in target frame
        """
        if frame == 'alpha-beta':
            return quantity_ab
        elif frame == 'abc':
            return np.array([alpha_beta_2_abc(q) for q in quantity_ab])
        elif frame == 'dq':
            if isinstance(self.sys, RLGrid):
                # Use grid angle for RL grid systems
                theta = np.arctan2(
                    self.data.sys.vg[:, 1],
                    self.data.sys.vg[:, 0],
                )

            elif isinstance(self.sys, InductionMachine):
                # Use rotor flux angle for induction machines
                theta = np.arctan2(
                    self.data.sys.x[:, 3],
                    self.data.sys.x[:, 2],
                )
            elif isinstance(self.sys, PMSM):
                # Use machine electrical angle for PMSM
                theta = self.data.sys.theta_el
            else:
                theta = 2 * np.pi * 50 * self.data.sys.t - np.pi / 2
            return np.array(
                [alpha_beta_2_dq(q, th) for q, th in zip(quantity_ab, theta)])
        else:
            raise ValueError(f"Unknown frame: {frame}")
