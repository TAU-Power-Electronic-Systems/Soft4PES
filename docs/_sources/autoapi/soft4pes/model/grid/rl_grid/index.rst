soft4pes.model.grid.rl_grid
===========================

.. py:module:: soft4pes.model.grid.rl_grid

.. autoapi-nested-parse::

   Model of a grid with a voltage source and an RL impedance in alpha-beta frame. The magnitude of
   the grid voltage is configurable as a function of time.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.rl_grid.RLGrid


Module Contents
---------------

.. py:class:: RLGrid(par, conv, base, ig_ref_init=None)

   Bases: :py:obj:`soft4pes.model.common.system_model.SystemModel`


   
   Model of a grid with a voltage source and an RL impedance in alpha-beta frame. The state of the
   system is the grid current (same as the converter current). The system input is the converter
   three-phase switch position or modulating signal. The grid voltage is considered to be a
   disturbance and the magnitude of the grid voltage is configurable as a function of time using a
   Sequence object.

   This class can be used as a base class for other grid models.

   :param par: Grid parameters in p.u.
   :type par: RLGridParameters
   :param conv: Converter object.
   :type conv: converter object
   :param base: Base values.
   :type base: base value object
   :param ig_ref_init: Reference at discrete time instant kTs = 0 for starting simulation from steady state.
   :type ig_ref_init: 1 x 2 ndarray of floats, optional

   .. attribute:: data

      Namespace for storing simulation data.

      :type: SimpleNamespace

   .. attribute:: par

      Grid parameters in p.u.

      :type: RLGridParameters

   .. attribute:: conv

      Converter object.

      :type: converter object

   .. attribute:: x

      Current state of the grid [p.u.].

      :type: 1 x 2 ndarray of floats

   .. attribute:: base

      Base values.

      :type: base value object

   .. attribute:: cont_state_space

      The continuous-time state-space model of the system.

      :type: SimpleNamespace

   .. attribute:: state_map

      A dictionary mapping states to elements of the state vector.

      :type: dict















   ..
       !! processed by numpydoc !!

   .. py:method:: set_initial_state(**kwargs)

      
      Set the initial state of the system based on the grid current reference, if provided.

      :param ig_ref_init: Reference at discrete time instant kTs = 0 for starting simulation from steady state.
      :type ig_ref_init: 1 x 2 ndarray of floats, optional















      ..
          !! processed by numpydoc !!


   .. py:method:: get_continuous_state_space()

      
      Calculate the continuous-time state-space model of the system.

      :returns: A SimpleNamespace object containing matrices F, G1 and G2 of the continuous-time
                state-space model.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: get_grid_voltage(kTs)

      
      Get the grid voltage at a specific discrete time instant.

      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Grid voltage in alpha-beta frame [p.u.].
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(matrices, u_abc, kTs)

      
      Calculate the next state of the system.

      :param u_abc: Converter three-phase switch position or modulating signal.
      :type u_abc: 1 x 3 ndarray of floats
      :param matrices: A SimpleNamespace object containing the state-space model matrices.
      :type matrices: SimpleNamespace
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: The next state of the system.
      :rtype: ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_measurements(kTs)

      
      Update the measurement data of the system.

      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: A SimpleNamespace object containing the grid voltage in alpha-beta frame.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: update_internal_variables(kTs)

      
      Update internal variables of the system.

      :param kTs: Current discrete time instant [s].
      :type kTs: float















      ..
          !! processed by numpydoc !!


