soft4pes.control.modulation.common_mode_injection
=================================================

.. py:module:: soft4pes.control.modulation.common_mode_injection

.. autoapi-nested-parse::

   Common-mode injection for modulating signal.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.modulation.common_mode_injection.CommonModeInjection


Module Contents
---------------

.. py:class:: CommonModeInjection(mode='MinMax')

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Common-mode injection for modulating signal. The selected common-mode injection method
   computes a common-mode voltage component that is added to the three-phase modulating signal.
   Common-mode injection is applicable for carrier-based PWM schemes and for modulating-signal
   feedforward.

   Available common-mode injection methods:
   - MinMax: Adds a common-mode component u_cm = -0.5 * (max(u_ref_abc) + min(u_ref_abc)) to the
     modulating signal. For a two level converter, this method is equivalent to space-vector
     modulation (SVM).

   :param mode: Common-mode injection method. Default is 'MinMax', which is the only available method.
   :type mode: str, optional

   .. attribute:: mode

      Common-mode injection method.

      :type: str















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Apply common-mode injection.

      :param sys: The system model (not used).
      :type sys: system object
      :param kTs: Current discrete time instant [s] (not used).
      :type kTs: float

      :returns: **u_ref_abc_cm** -- Three-phase modulating signal with common-mode injection.
      :rtype: 3 x 1 ndarray















      ..
          !! processed by numpydoc !!


