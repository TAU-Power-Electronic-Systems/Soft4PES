soft4pes.model.grid.base_grid
=============================

.. py:module:: soft4pes.model.grid.base_grid

.. autoapi-nested-parse::

   Base values for a grid.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.base_grid.BaseGrid


Module Contents
---------------

.. py:class:: BaseGrid(Vg_R_SI, Ig_R_SI, fg_R_SI)

   
   Base values for a grid.

   The class computes the base values for a grid based on the rated values.

   :param Vg_R_SI: Rated voltage [V] (line-to-line rms voltage).
   :type Vg_R_SI: float
   :param Ig_R_SI: Rated current [A] (line rms current).
   :type Ig_R_SI: float
   :param fg_R_SI: Rated frequency [Hz].
   :type fg_R_SI: float

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

