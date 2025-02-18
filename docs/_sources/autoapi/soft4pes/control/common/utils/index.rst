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

.. py:function:: magnitude_limiter(input_signal, limit)

   
   Limit the input in to maximum magnitude. The input can be in alpha-beta or dq-frame, and given
   as a vector or complex number.

   :param limit: Maximum magnitude [p.u.].
   :type limit: float
   :param input_signal: Unlimited input [p.u.].
   :type input_signal: 1 x 2 ndarray of floats or complex

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


