soft4pes.model.grid
===================

.. py:module:: soft4pes.model.grid

.. autoapi-nested-parse::

   
   Grid models.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/model/grid/base_grid/index
   /autoapi/soft4pes/model/grid/rl_grid/index


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.BaseGrid
   soft4pes.model.grid.RLGrid


Package Contents
----------------

.. py:class:: BaseGrid(Vgr, Igr, fgr)

   
   Base values for a grid.

   The class computes the base values for a grid based on the rated values.

   :param Vgr: Rated voltage [V] (line-to-line rms voltage).
   :type Vgr: float
   :param Igr: Rated current [A] (line rms current).
   :type Igr: float
   :param fgr: Rated frequency [Hz].
   :type fgr: float

   .. attribute:: V

      Base voltage [V].

      :type: float

   .. attribute:: I

      Base current [A].

      :type: float

   .. attribute:: w

      Base angular frequency [rad/s].

      :type: float

   .. attribute:: S

      Base apparent power [VA].

      :type: float

   .. attribute:: Z

      Base impedance [Ohm].

      :type: float

   .. attribute:: L

      Base inductance [H].

      :type: float

   .. attribute:: C

      Base capacitance [F].

      :type: float















   ..
       !! processed by numpydoc !!

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


