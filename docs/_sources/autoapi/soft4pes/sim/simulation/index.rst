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

      :returns: A SimpleNamespace with lists of arrays converted to NumPy arrays, or a NumPy array if the input is a list of arrays.
      :rtype: SimpleNamespace or ndarray















      ..
          !! processed by numpydoc !!


