soft4pes.model.grid.rl_grid
===========================

.. py:module:: soft4pes.model.grid.rl_grid

.. autoapi-nested-parse::

   Model of a grid with stiff voltage source and RL-load in alpha-beta frame

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.rl_grid.RLGrid


Module Contents
---------------

.. py:class:: RLGrid(Vgr, fgr, Rg, Lg, base, ig_ref_init=None)

   Bases: :py:obj:`soft4pes.model.common.system_model.SystemModel`


   
   Model of a grid with stiff voltage source and RL-load in alpha-beta frame. The state of the
   system is the grid current in the alpha-beta frame. The system input is the converter
   three-phase switch position or modulating signal. The grid voltage is considered to be a
   disturbance.

   :param Vgr: Grid rated voltage [V] (line-to-line rms voltage).
   :type Vgr: float
   :param fgr: Grid rated frequency [Hz].
   :type fgr: float
   :param Rg: Resistance [Ohm].
   :type Rg: float
   :param Lg: Inductance [H].
   :type Lg: float
   :param base: Base values.
   :type base: base value object
   :param ig_ref_init: Reference at discrete time instant kTs = 0 for starting simulation from steady state.
   :type ig_ref_init: 1 x 2 ndarray of floats, optional

   .. attribute:: Vgr

      Grid rated voltage [p.u.] (line-to-line rms voltage).

      :type: float

   .. attribute:: wg

      Grid angular frequency [p.u.].

      :type: float

   .. attribute:: Rg

      Resistance [p.u.].

      :type: float

   .. attribute:: Xg

      Reactance [p.u.].

      :type: float

   .. attribute:: x

      Current state of the grid [p.u.].

      :type: 1 x 2 ndarray of floats

   .. attribute:: base

      Base values.

      :type: base value object















   ..
       !! processed by numpydoc !!

   .. py:method:: set_initial_state(**kwargs)

      
      Set the initial state of the system based on the grid current reference, if provided.

      :param ig_ref_init: Reference at discrete time instant kTs = 0 for starting simulation from steady state.
      :type ig_ref_init: 1 x 2 ndarray of floats, optional















      ..
          !! processed by numpydoc !!


   .. py:method:: get_discrete_state_space(v_dc, Ts)

      
      Calculates the discrete-time state-space model of the system.

      :param v_dc: The converter dc-link voltage [p.u.].
      :type v_dc: float
      :param Ts: Sampling interval [s].
      :type Ts: float

      :returns: The discrete-time state-space model of the system.
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


   .. py:method:: update_state(matrices, uk_abc, kTs)

      
      Get the next state of the system.

      :param uk_abc: Converter three-phase switch position or modulating signal.
      :type uk_abc: 1 x 3 ndarray of floats
      :param matrices: A SimpleNamespace object containing the state-space model matrices.
      :type matrices: SimpleNamespace
      :param kTs: Current discrete time instant [s].
      :type kTs: float















      ..
          !! processed by numpydoc !!


