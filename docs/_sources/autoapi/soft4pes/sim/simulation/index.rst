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


.. py:class:: Simulation(sys, conv, ctr, Ts_sim)

   
   Simulation environment.

   :param sys: System model.
   :type sys: system object
   :param conv: Converter model.
   :type conv: converter object
   :param ctr: Control system.
   :type ctr: controller object
   :param Ts_sim: Simulation sampling interval [s].
   :type Ts_sim: float

   .. attribute:: sys

      System model.

      :type: system object

   .. attribute:: conv

      Converter model.

      :type: converter object

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















   ..
       !! processed by numpydoc !!

   .. py:method:: simulate(t_stop)

      
      Simulate the system.

      :param t_stop: Simulation length [s]. Simulation start time is always 0 s.
      :type t_stop: float















      ..
          !! processed by numpydoc !!


