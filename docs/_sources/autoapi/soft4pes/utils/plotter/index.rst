soft4pes.utils.plotter
======================

.. py:module:: soft4pes.utils.plotter

.. autoapi-nested-parse::

   Plotting functionality for system states and control signals.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.utils.plotter.Plotter


Module Contents
---------------

.. py:class:: Plotter(data, sys, t_start=0, t_end=None)

   
   This class provides methods to plot system states, switching behavior, and control signals. It
   supports multiple reference frames (abc, alpha-beta, dq). The main functions of the class are:
   - plot_states: Plot system states in specified reference frames.
   - plot_control_signals_grid: Plot control signals for grid-connected systems (active/reactive
     power, voltage magnitude).
   - plot_control_signals_machine: Plot control signals for electric machines (torque).
   - show_all: Display all generated plots.

   :param data: Simulation data containing system and controller results
   :type data: SimulationData
   :param sys: System object with state mapping and configuration
   :type sys: System
   :param t_start: Start time for all plots (default: 0)
   :type t_start: float, optional
   :param t_end: End time for all plots (default: None, uses full simulation time)
   :type t_end: float, optional

   .. rubric:: Examples

   >>> plotter = SystemPlotter(data, sys, t_start=0, t_end=0.2)
   >>> plotter.plot_states(['vc', 'ig'], frames=['abc', 'alpha-beta'])
   >>> plotter.plot_control_signals_grid(plot_P=True, plot_Q=True, P_ref=P_ref_seq)
   >>> plotter.show_all()















   ..
       !! processed by numpydoc !!

   .. py:method:: plot_control_signals_grid(plot_P=False, plot_Q=False, plot_V=False, P_ref=None, Q_ref=None, V_ref=None)

      
      Plot grid-connected system control signals (active/reactive power, voltage magnitude). The
      voltage magnitude corresponds to converter output voltage (no LCL filter) or capacitor
      voltage (with LCL filter).

      :param plot_P: Plot active power P (default: False)
      :type plot_P: bool, optional
      :param plot_Q: Plot reactive power Q (default: False)
      :type plot_Q: bool, optional
      :param plot_V: Plot voltage magnitude (converter or capacitor) (default: False)
      :type plot_V: bool, optional
      :param P_ref: Active power reference trajectory
      :type P_ref: Sequence, optional
      :param Q_ref: Reactive power reference trajectory
      :type Q_ref: Sequence, optional
      :param V_ref: Voltage magnitude reference trajectory
      :type V_ref: Sequence, optional

      .. rubric:: Notes

      - If both plot_P and plot_Q are True, they are plotted together
      - Voltage plots either converter voltage (if no capacitor) or capacitor voltage
      - Power is calculated as:
        P = vg_alpha*ig_alpha + vg_beta*ig_beta,
        Q = vg_beta*ig_alpha - vg_alpha*ig_beta















      ..
          !! processed by numpydoc !!


   .. py:method:: plot_control_signals_machine(plot_T=False, T_ref=None)

      
      Plot machine control signals (electromagnetic torque).

      :param plot_T: Plot electromagnetic torque Te (default: False)
      :type plot_T: bool, optional
      :param T_ref: Torque reference trajectory
      :type T_ref: Sequence, optional















      ..
          !! processed by numpydoc !!


   .. py:method:: plot_states(states_to_plot, frames=None, plot_u_abc_ref=False, plot_u_abc=False)

      
      Plot system states in specified reference frames. Moreover, the modulating signal u_abc_ref
      and/or the actual converter output can be plotted. In case modulator is not used,
      u_abc_ref=u_abc.

      :param states_to_plot: List of state names to plot (e.g., ['vc', 'ig', 'i_conv']). The existing states can be
                             confirmed by checking the model class documentation.
      :type states_to_plot: list of str
      :param frames: Reference frames for each state ('abc', 'alpha-beta', 'dq').
                     If None, defaults to 'alpha-beta' for all states. The dq-frame is aligned with
                     - the grid voltage for grid-connected systems
                     - the rotor flux for induction machines
                     - the rotor angle for PMSMs
      :type frames: list of str, optional
      :param plot_u_abc_ref: Plot modulating signal u_abc_ref in one subplot (default: False)
      :type plot_u_abc_ref: bool, optional
      :param plot_u_abc: Plot actual converter output u_abc in separate subplots (default: False)
      :type plot_u_abc: bool, optional

      .. rubric:: Examples

      >>> plotter.plot_states(['vc', 'ig'], frames=['abc', 'alpha-beta'])
      >>> plotter.plot_states(['i_conv'], frames=['dq'], plot_u_abc=True)















      ..
          !! processed by numpydoc !!


   .. py:method:: show_all()

      
      Display all registered figures and keep them open.

      This method should be called after creating all desired plots to display
      them simultaneously. Figures remain open until manually closed by the user.















      ..
          !! processed by numpydoc !!


