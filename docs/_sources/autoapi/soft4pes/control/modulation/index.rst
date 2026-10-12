soft4pes.control.modulation
===========================

.. py:module:: soft4pes.control.modulation

.. autoapi-nested-parse::

   
   Modulation methods for power electronic converters.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/control/modulation/carrier_pwm/index
   /autoapi/soft4pes/control/modulation/common_mode_injection/index
   /autoapi/soft4pes/control/modulation/opp_computation/index


Classes
-------

.. autoapisummary::

   soft4pes.control.modulation.CarrierPWM
   soft4pes.control.modulation.CommonModeInjection
   soft4pes.control.modulation.OPPComputation


Package Contents
----------------

.. py:class:: CarrierPWM

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Asynchronous carrier-based pulse width modulation (CB-PWM) for two and three-level converters.
   The modulating signal is sampled at the peaks of the carrier, resulting in the device switching
   frequency of 1/(2Ts) for two-level converters. For three-level converters, the device switching
   frequency is roughly half the apparent switching, ie. the carrier frequency, when
   phase-disposition PWM is used.

   :param None:

   .. attribute:: carrier_rising

      Flag indicating whether the carrier is rising or falling.

      :type: bool















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Generate switching time instants and switch positions using asynchronous carrier-based pulse
      width modulation (CB-PWM).

      The produced output is presented below. Note that the switching times are in ascending
      order.

                              |      Switch positions       |
      Switching time instants | Phase A | Phase B | Phase C |
      ---------------         |---------|---------|---------|
                  0           | state   | state   | state
                  t_switch[1] | state   | state   | state
                  t_switch[2] | state   | state   | state
                  t_switch[3] | state   | state   | state

      :param sys: The system model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: * **t_switch** (*ndarray*) -- Switching time instants.
                * **switch_array** (*ndarray*) -- Switch positions.















      ..
          !! processed by numpydoc !!


.. py:class:: CommonModeInjection(mode='MinMax')

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Common-mode injection for modulating signal. The selected common-mode injection method
   computes a common-mode voltage component that is added to the three-phase modulating signal.
   Common-mode injection is applicable for carrier-based PWM schemes and for modulating-signal
   feedforward.

   Available common-mode injection methods:
   - MinMax: Adds a common-mode component u_cm = -0.5 * (max(u_ref_abc) + min(u_ref_abc)) to the
     modulating signal. For a two level converter, this method is equivalent to space-vector
     modulation (SVM).

   :param mode: Common-mode injection method. Default is 'MinMax', which is the only available method.
   :type mode: str, optional

   .. attribute:: mode

      Common-mode injection method.

      :type: str















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Apply common-mode injection.

      :param sys: The system model (not used).
      :type sys: system object
      :param kTs: Current discrete time instant [s] (not used).
      :type kTs: float

      :returns: **u_ref_abc_cm** -- Three-phase modulating signal with common-mode injection.
      :rtype: 3 x 1 ndarray















      ..
          !! processed by numpydoc !!


.. py:class:: OPPComputation(sys, d=5, symmetry='QaHWS', n_m=256, n_ini_points=1000, max_harmonics=500, modulation_indices=None)

   
   Offline OPP computation.

   :param sys: System model.
   :type sys: SystemModel
   :param d: Base number of switching transitions used to construct the OPP.
             For example, this corresponds to the pulse number for three-level
             QaHWS OPPs.
   :type d: int, default=5
   :param symmetry: Waveform symmetry.















   ..
       !! processed by numpydoc !!

   .. py:method:: build_problem()

      
      Build all quantities required for OPP computation.
















      ..
          !! processed by numpydoc !!


   .. py:method:: build_harmonics()

      
      Build the set of considered non-triplen odd harmonic orders.
















      ..
          !! processed by numpydoc !!


   .. py:method:: build_switching_sequence()

      
      Build switching-angle and switching-sequence information.
















      ..
          !! processed by numpydoc !!


   .. py:method:: build_system_model()

      
      Build harmonic weighting factors used in the objective function.

      For systems with an LCL filter, the weighting factors are based on the
      gain of the transfer function from the switch position to the output
      current. All other currently supported systems use 1/n weighting
      factors.















      ..
          !! processed by numpydoc !!


   .. py:method:: build_constraints()

      
      Build bound and ordering constraints for the switching angles.
















      ..
          !! processed by numpydoc !!


   .. py:method:: build_initial_points()

      
      Generate Halton initial points for multistart optimization.
















      ..
          !! processed by numpydoc !!


   .. py:method:: get_worker_data()

      
      Collect data required by multiprocessing workers.

      :returns: Data shared with worker processes.
      :rtype: dict















      ..
          !! processed by numpydoc !!


   .. py:method:: compute(use_parallel=True)

      
      Compute OPPs.

      :param use_parallel: If True, the multistart initial points are solved in parallel.
      :type use_parallel: bool, default=True

      :returns: Computed OPP lookup-table data, including switching angles,
                modulation indices, and switch positions.
      :rtype: dict















      ..
          !! processed by numpydoc !!


   .. py:method:: compute_loop(results, pool)

      
      Main loop over modulation indices and switching sequences.

      :param results: Dictionary used to store computed OPP data.
      :type results: dict
      :param pool: Worker pool used for parallel execution.
      :type pool: multiprocessing.Pool or None















      ..
          !! processed by numpydoc !!


   .. py:method:: save_results(filename=None)

      
      Save computed OPPs to a NetCDF file.

      :param filename: Output file name.
                       If None, a file name is generated from the OPP configuration.
      :type filename: str, optional















      ..
          !! processed by numpydoc !!


