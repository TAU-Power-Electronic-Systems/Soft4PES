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

