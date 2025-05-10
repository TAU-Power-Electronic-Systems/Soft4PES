soft4pes.control.lin.rfpsc
==========================

.. py:module:: soft4pes.control.lin.rfpsc

.. autoapi-nested-parse::

   Reference-feedforward power synchronization control (RFPSC).

   Reference:
   L. Harnefors, F. M. M. Rahman, M. Hinkkanen, and M. Routimo, “Reference-feedforward
   power-synchronization control,” IEEE Trans. Power Electron., vol. 35, no. 9, pp. 8878-8881, Sep.
   2020.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.rfpsc.RFPSC


Module Contents
---------------

.. py:class:: RFPSC(sys, Ra=0.2, Kp=None, w_bw=0.1)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Reference-feedforward power synchronization control (RFPSC).

   :param sys: System model.
   :type sys: system object
   :param Ra: Virtual damping resistance [p.u.].
   :type Ra: float, optional
   :param Kp: Proportional gain of the active power droop control [p.u.]. If not provided, it is
              calculated based on the nominal frequency, nominal grid peak voltage and the virtual
              damping resistance.
   :type Kp: float, optional
   :param w_bw: Current filter bandwidth [p.u.].
   :type w_bw: float, optional

   .. attribute:: Ra

      Virtual damping resistance [p.u.].

      :type: float

   .. attribute:: theta_c

      The angle of the synchronous reference frame set by the droop control. The initial angle
      is set to -pi/2 to align the q-axis with the grid voltage.

      :type: float

   .. attribute:: ig_filter

      First-order filter for the current.

      :type: FirstOrderFilter

   .. attribute:: Kp

      Proportional gain of the active power droop control [p.u.]. Recommended selection is
      Kp = wg * Ra / Vg, where wg is the nominal grid angular frequency, Ra is the virtual damping
      resistance (default 0.2 p.u.) and Vg is the nominal grid peak voltage. If value is not
      provided, nominal grid angular frequency and nominal grid peak voltage are assumed to be
      1 p.u. For more details on the tuning and default values, see the reference above.

      :type: float















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Execute the RFPSC control algorithm.

      :param sys: The system model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: A SimpleNamespace object containing the modulating signal for the converter (u_abc) and
                a capacitor voltage reference in case LC(L) filter is used (vc_ref).
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


