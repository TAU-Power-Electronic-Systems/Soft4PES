soft4pes.sim
============

.. py:module:: soft4pes.sim

.. autoapi-nested-parse::

   
   Simulation environment.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/sim/simulation/index


Classes
-------

.. autoapisummary::

   soft4pes.sim.Simulation


Package Contents
----------------

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


