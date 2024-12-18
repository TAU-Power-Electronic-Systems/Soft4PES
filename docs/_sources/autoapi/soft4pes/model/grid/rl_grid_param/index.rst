soft4pes.model.grid.rl_grid_param
=================================

.. py:module:: soft4pes.model.grid.rl_grid_param

.. autoapi-nested-parse::

   Parameters for a grid with a stiff voltage source and RL-load.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.rl_grid_param.RLGridParameters


Module Contents
---------------

.. py:class:: RLGridParameters(Vg_SI, fg_SI, Rg_SI, Lg_SI, base)

   
   Parameters for a grid with a stiff voltage source and RL-load.

   :param Vg_SI: Grid voltage [V] (line-to-line rms voltage).
   :type Vg_SI: float
   :param fg_SI: Grid frequency [Hz].
   :type fg_SI: float
   :param Rg_SI: Resistance [Ohm].
   :type Rg_SI: float
   :param Lg_SI: Inductance [H].
   :type Lg_SI: float
   :param base: Base values.
   :type base: base value object

   .. attribute:: Vg

      Grid voltage [p.u.] (line-to-line rms voltage).

      :type: float

   .. attribute:: wg

      Angular frequency [p.u.].

      :type: float

   .. attribute:: Rg

      Resistance [p.u.].

      :type: float

   .. attribute:: Xg

      Reactance [p.u.].

      :type: float















   ..
       !! processed by numpydoc !!

