soft4pes.control.common.utils
=============================

.. py:module:: soft4pes.control.common.utils

.. autoapi-nested-parse::

   Utility functions and classes for the control module.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.common.utils.FirstOrderFilter


Functions
---------

.. autoapisummary::

   soft4pes.control.common.utils.wrap_theta
   soft4pes.control.common.utils.get_modulating_signal
   soft4pes.control.common.utils.magnitude_limiter


Module Contents
---------------

.. py:function:: wrap_theta(theta)

   
   Wrap the angle theta to the range [-pi, pi].

   :param theta: The angle in radians.
   :type theta: float

   :returns: The wrapped angle in radians.
   :rtype: float















   ..
       !! processed by numpydoc !!

.. py:function:: get_modulating_signal(v_ref, v_dc)

   
   Convert a voltage reference to a modulating signal.

   :param v_ref: The reference voltage in alpha-beta frame.
   :type v_ref: ndarray
   :param v_dc: The DC link voltage.
   :type v_dc: float

   :returns: The modulating signal in abc frame.
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: magnitude_limiter(unlimited_input, maximum_output)

   
   Limit the input in dq-frame. The instantaneous limiting function is used
   to limit the amplitude of the current and voltage reference in dq-frame.

   :param maximum_output: Maximum magnitude [p.u.].
   :type maximum_output: float
   :param unlimited_input: Unlimited input [p.u.].
   :type unlimited_input: 1 x 2 ndarray of floats

   :returns: Limited output [p.u.].
   :rtype: 1 x 2 ndarray of floats















   ..
       !! processed by numpydoc !!

.. py:class:: FirstOrderFilter(wb, size)

   
   General first order filter.

   :param wb: The bandwidth of the filter [p.u.].
   :type wb: float
   :param size: The size of the signal to be filtered.
   :type size: int

   .. attribute:: wb

      The bandwidth of the filter [p.u.].

      :type: float

   .. attribute:: output

      The filtered signal.

      :type: ndarray















   ..
       !! processed by numpydoc !!

   .. py:method:: update(value_in, Ts, base)

      
      Update the filter with a new input signal.

      :param value_in: The input signal to be filtered.
      :type value_in: ndarray
      :param Ts: The sampling interval [s].
      :type Ts: float
      :param base: The base values object containing the base angular frequency.
      :type base: object















      ..
          !! processed by numpydoc !!


