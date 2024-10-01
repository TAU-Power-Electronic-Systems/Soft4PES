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

.. py:class:: RLGrid(Vgr, fgr, Rg, Lg, base)

   
   Model of a grid with stiff voltage source and RL-load in alpha-beta frame.
   The state of the system is the grid current in the alpha-beta frame.
   The system input is the converter three-phase switch position.
   The grid voltage is considered to be a disturbance.

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

   .. attribute:: data_sim

      System data.

      :type: dict















   ..
       !! processed by numpydoc !!

   .. py:method:: get_discrete_state_space(v_dc, Ts)

      
      Get the discrete state-space model of the grid in alpha-beta frame.
      Discretization is done using the forward Euler method.

      :param v_dc: Converter dc-link voltage [p.u.].
      :type v_dc: float
      :param Ts: Sampling interval [s].
      :type Ts: float

      :returns: A SimpleNamespace object containing matrices A, B1 and B2 of the
                state-space model.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: get_grid_voltage(t)

      
      Get the grid voltage at a specific time instant.

      :param t: Current time [s].
      :type t: float

      :returns: Grid voltage in alpha-beta frame [p.u.].
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: update_state(u, matrices, t)

      
      Get the next state of the grid.

      :param u: Converter three-phase switch position.
      :type u: 1 x 3 ndarray of floats
      :param matrices: A SimpleNamespace object containing matrices A, B1 and B2 of the
                       state-space model.
      :type matrices: SimpleNamespace

      :returns: Next state of the grid [p.u.].
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: save_data(vg, t)

      
      Save system data.

      :param vg: Grid voltage in alpha-beta frame [p.u.].
      :type vg: 1 x 2 ndarray of floats
      :param t: Current time [s].
      :type t: float















      ..
          !! processed by numpydoc !!


