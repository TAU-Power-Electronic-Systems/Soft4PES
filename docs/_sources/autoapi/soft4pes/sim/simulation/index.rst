soft4pes.sim.simulation
=======================

.. py:module:: soft4pes.sim.simulation

.. autoapi-nested-parse::

   Simulation environment for power electronic systems.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.sim.simulation.ProgressPrinter
   soft4pes.sim.simulation.SwitchingLogic
   soft4pes.sim.simulation.Simulation


Module Contents
---------------

.. py:class:: ProgressPrinter(total_steps)

   
   A class used to print the progress of the simulation process.

   :param total_steps: The total number of steps in the process.
   :type total_steps: int

   .. attribute:: total_steps

      The total number of steps in the process.

      :type: int

   .. attribute:: last_printed_percent

      The last printed percentage of progress.

      :type: int















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(current_step)

      
      Prints the current progress with steps of 5 percent.

      :param current_step: The number of the current step in the process.
      :type current_step: int















      ..
          !! processed by numpydoc !!


.. py:class:: SwitchingLogic(Ts_sim, Ts)

   
   A class to handle switching-related logic, such as quantizing switching time instants and
   extracting the three-phase switch position or modulating signal.

   :param Ts_sim: Simulation sampling interval [s].
   :type Ts_sim: float
   :param Ts: Control system sampling interval [s].
   :type Ts: float

   .. attribute:: Ts_sim

      Simulation sampling interval [s].

      :type: float

   .. attribute:: Ts

      Control system sampling interval [s].

      :type: float

   .. attribute:: k_switch

      Quantized switching times.

      :type: ndarray

   .. attribute:: u_abc

      Three-phase switch position or modulating signal.

      :type: ndarray















   ..
       !! processed by numpydoc !!

   .. py:method:: quantize_switching_time_instants(t_switch)

      
      Quantize the switching time instants.

      :param t_switch: Switching time instants.
      :type t_switch: ndarray

      :returns: Quantized switching time instants.
      :rtype: ndarray















      ..
          !! processed by numpydoc !!


   .. py:method:: get_switch_positions(ctr_output, k_sim)

      
      Get the three-phase switch position or modulating signal for the current discrete time
      instant. The switching time instants are quantized to the simulation sampling interval in
      the beginning of the control interval.

      :param ctr_output: Output from the controller including the switching time instants and the corresponding
                         switch position or modulating signal.
      :type ctr_output: SimpleNamespace
      :param k_sim: The current simulation step within the control interval.
      :type k_sim: int

      :returns: Three-phase switch positions or modulating signal for current simulation step.
      :rtype: ndarray















      ..
          !! processed by numpydoc !!


.. py:class:: Simulation(sys, ctr, Ts_sim, disc_method='forward_euler')

   
   Simulation environment.

   :param sys: System model.
   :type sys: system object
   :param ctr: Control system.
   :type ctr: controller object
   :param Ts_sim: Simulation sampling interval [s].
   :type Ts_sim: float

   .. attribute:: sys

      System model.

      :type: system object

   .. attribute:: ctr

      Control system.

      :type: controller object.

   .. attribute:: Ts_sim

      Simulation sampling interval [s].

      :type: float

   .. attribute:: t_stop

      Simulation stop time [s].

      :type: float

   .. attribute:: matrices

      Discrete state-space matrices of the simulated system.

      :type: SimpleNamespace

   .. attribute:: simulation_data

      Data from the simulation.

      :type: dict

   .. attribute:: switching_logic

      Object for handling switching logic.

      :type: SwitchingLogic















   ..
       !! processed by numpydoc !!

   .. py:method:: simulate(t_stop)

      
      Simulate the system.

      :param t_stop: Simulation length [s]. Simulation start time is always 0 s, i.e. kTs = 0.
      :type t_stop: float















      ..
          !! processed by numpydoc !!


   .. py:method:: save_data(filename='sim_data.mat', path='')

      
      Save the simulation data to a .mat file.

      :param filename: Name of the file to save the data to. The default filename is 'sim_data.mat'.
      :type filename: str, optional
      :param path: Directory path to save the file to. The path can be absolute or relative to the current
                   directory. The default saving directory is the current directory.
      :type path: str, optional















      ..
          !! processed by numpydoc !!


   .. py:method:: process_simulation_data(data)

      
      Recursively convert lists of arrays in a SimpleNamespace to NumPy arrays.

      :param data: The data to be converted. Can be a SimpleNamespace or a list of arrays.
      :type data: SimpleNamespace or list of ndarray

      :returns: A SimpleNamespace with lists of arrays converted to NumPy arrays, or a NumPy array if
                the input is a list of arrays.
      :rtype: SimpleNamespace or ndarray















      ..
          !! processed by numpydoc !!


