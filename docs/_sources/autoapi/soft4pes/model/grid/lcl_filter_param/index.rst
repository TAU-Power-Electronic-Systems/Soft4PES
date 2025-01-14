soft4pes.model.grid.lcl_filter_param
====================================

.. py:module:: soft4pes.model.grid.lcl_filter_param

.. autoapi-nested-parse::

   Parameters for an LCL-filter.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.lcl_filter_param.LCLFilterParameters


Module Contents
---------------

.. py:class:: LCLFilterParameters(L_fc_SI, C_SI, base, L_fg_SI=0, R_fc_SI=0, R_c_SI=0, R_fg_SI=0)

   
   Parameters for an LCL-filter.

   :param L_fc_SI: Inductance of the converter side filter inductor [H].
   :type L_fc_SI: float
   :param C_SI: Capacitance of the filter capacitor [F].
   :type C_SI: float
   :param base: Base values.
   :type base: base value object
   :param L_fg_SI: Inductance of the grid side filter inductor [H].
   :type L_fg_SI: float, optional
   :param R_fc_SI: Resistance of the converter side filter inductor [Ohm].
   :type R_fc_SI: float, optional
   :param R_c_SI: Resistance of the filter capacitor [Ohm].
   :type R_c_SI: float, optional
   :param R_fg_SI: Resistance of the grid side filter inductor [Ohm].
   :type R_fg_SI: float, optional

   .. attribute:: X_fc

      Reactance of the converter side filter inductor [p.u.].

      :type: float

   .. attribute:: R_fc

      Resistance of the converter side filter inductor [p.u.].

      :type: float

   .. attribute:: Xc

      Reactance of the filter capacitor [p.u.].

      :type: float

   .. attribute:: Rc

      Resistance of the filter capacitor [p.u.].

      :type: float

   .. attribute:: X_fg

      Reactance of the grid side filter inductor [p.u.].

      :type: float

   .. attribute:: R_fg

      Resistance of the grid side filter inductor [p.u.].

      :type: float

   .. attribute:: base

      :type: base value object















   ..
       !! processed by numpydoc !!

