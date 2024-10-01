soft4pes.model.conv.converter
=============================

.. py:module:: soft4pes.model.conv.converter

.. autoapi-nested-parse::

   n-level converter model.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.conv.converter.Converter


Module Contents
---------------

.. py:class:: Converter(v_dc, nl, base)

   
   Class representing a 2- or 3-level converter with constant dc-link voltage.

   Initialize a Converter instance.

   :param v_dc: Dc-link voltage [V].
   :type v_dc: float
   :param nl: Number of voltage levels in the converter.
   :type nl: int
   :param base: Base values.
   :type base: base value object

   .. attribute:: v_dc

      Dc_link voltage [p.u.]

      :type: float

   .. attribute:: nl

      Number of voltage levels in the converter.

      :type: int

   .. attribute:: SW_COMB

      Possible converter three-phase switch positions.

      :type: 3^nl x 3 ndarray of ints















   ..
       !! processed by numpydoc !!

