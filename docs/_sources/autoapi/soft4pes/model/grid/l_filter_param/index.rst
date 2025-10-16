soft4pes.model.grid.l_filter_param
==================================

.. py:module:: soft4pes.model.grid.l_filter_param

.. autoapi-nested-parse::

   Parameters for an L-filter.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.l_filter_param.LFilterParameters


Module Contents
---------------

.. py:class:: LFilterParameters(L_fc_SI, base, R_fc_SI=0)

   
   Parameters for an L-filter.

   :param L_fc_SI: Inductance of the filter inductor [H].
   :type L_fc_SI: float
   :param base: Base values.
   :type base: base value object
   :param R_fc_SI: Resistance of the filter inductor [Ohm].
   :type R_fc_SI: float, optional

   .. attribute:: X_fc

      Reactance of the filter inductor [p.u.].

      :type: float

   .. attribute:: R_fc

      Resistance of the filter inductor [p.u.].

      :type: float

   .. attribute:: base

      :type: base value object















   ..
       !! processed by numpydoc !!

