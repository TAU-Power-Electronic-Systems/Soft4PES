soft4pes.control.lin.grid_curr_ref_gen
======================================

.. py:module:: soft4pes.control.lin.grid_curr_ref_gen

.. autoapi-nested-parse::

   Grid current reference generator.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.grid_curr_ref_gen.GridCurrRefGen


Module Contents
---------------

.. py:class:: GridCurrRefGen

   Bases: :py:obj:`soft4pes.control.common.Controller`


   
   Grid current reference generator. This class generates the grid current reference based on the
   active and reactive power references using grid voltage. The equations are in per unit. Grid
   voltage orientation is assumed, i.e. vg_d is aligned with d-axis of the dq-reference frame.
   Moreover, the positive grid current flows from the converter to the grid.
















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, conv, kTs)

      
      Generate the current reference.

      :param sys: System model.
      :type sys: object
      :param conv: Converter model.
      :type conv: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **output** -- The output of the controller, containing the current reference in dq frame.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


