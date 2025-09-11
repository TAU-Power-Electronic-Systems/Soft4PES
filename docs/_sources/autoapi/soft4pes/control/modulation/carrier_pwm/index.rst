soft4pes.control.modulation.carrier_pwm
=======================================

.. py:module:: soft4pes.control.modulation.carrier_pwm

.. autoapi-nested-parse::

   Asynchronous carrier-based pulse width modulation (CB-PWM) for two and three-level converters.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.modulation.carrier_pwm.CarrierPWM


Module Contents
---------------

.. py:class:: CarrierPWM

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Base class for controllers.

   .. attribute:: data

      Data storage for the controller, containing input and output namespaces.

      :type: SimpleNamespace

   .. attribute:: input

      Namespace for storing input data.

      :type: SimpleNamespace

   .. attribute:: output

      Namespace for storing output data.

      :type: SimpleNamespace

   .. attribute:: Ts

      Sampling interval [s].

      :type: float















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Generate switching time instants and switch positions using asynchronous carrier-based pulse
      width modulation (CB-PWM). The modulating signal is sampled at the peaks of the carrier,
      resulting in the device switching frequency of 1/(2Ts) for two-level converters. For three-
      level converters, the device switching frequency is roughly half the apparent switching, ie.
      the carrier frequency, when phase-disposition PWM is used.

      The produced output is presented below. Note that the switching times are in ascending
      order.

                              |      Switch positions       |
      Switching time instants | Phase A | Phase B | Phase C |
      ---------------         |---------|---------|---------|
                  0           | state   | state   | state
                  t_switch[1] | state   | state   | state
                  t_switch[2] | state   | state   | state
                  t_switch[3] | state   | state   | state

      :param sys: The system model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: * **t_switch** (*ndarray*) -- Switching time instants.
                * **switch_array** (*ndarray*) -- Switch positions.















      ..
          !! processed by numpydoc !!


