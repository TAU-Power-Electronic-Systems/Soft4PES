soft4pes.model.conv
===================

.. py:module:: soft4pes.model.conv

.. autoapi-nested-parse::

   
   Converter model.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/model/conv/converter/index


Classes
-------

.. autoapisummary::

   soft4pes.model.conv.Converter


Package Contents
----------------

.. py:class:: Converter(v_dc_SI, nl, base)

   
   Class representing a 2- or 3-level converter with constant dc-link voltage.

   :param v_dc_SI: Dc-link voltage [V].
   :type v_dc_SI: float
   :param nl: Number of voltage levels in the converter.
   :type nl: int
   :param base: Base values.
   :type base: base value object

   .. attribute:: v_dc

      Dc-link voltage [p.u.]

      :type: float

   .. attribute:: nl

      Number of voltage levels in the converter.

      :type: int

   .. attribute:: sw_pos_3ph

      Possible one-phase switch positions.

      :type: list of ints















   ..
       !! processed by numpydoc !!

