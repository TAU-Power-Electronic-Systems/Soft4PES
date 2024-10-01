soft4pes.utils.conversions
==========================

.. py:module:: soft4pes.utils.conversions

.. autoapi-nested-parse::

   Reference-frame conversions.

   ..
       !! processed by numpydoc !!


Functions
---------

.. autoapisummary::

   soft4pes.utils.conversions.abc_2_alpha_beta
   soft4pes.utils.conversions.alpha_beta_2_abc
   soft4pes.utils.conversions.alpha_beta_2_dq
   soft4pes.utils.conversions.dq_2_alpha_beta
   soft4pes.utils.conversions.dq_2_abc


Module Contents
---------------

.. py:function:: abc_2_alpha_beta(abc)

   
   Convert a quantity from abc-frame to alpha-beta frame using the reduced
   Clarke transformation. The common-mode component is neglected.

   :param abc: Input quantity in abc-frame.
   :type abc: 1 x 3 ndarray of floats

   :returns: Quantity in alpha-beta frame.
   :rtype: 1 x 2 ndarray of floats















   ..
       !! processed by numpydoc !!

.. py:function:: alpha_beta_2_abc(alpha_beta)

   
   Convert a quantity from abc-frame to alpha-beta frame using the inverse
   reduced Clarke transformation. The common-mode component is neglected.

   :param abc: Input quantity in abc-frame.
   :type abc: 1 x 3 ndarray of floats

   :returns: Quantity in alpha-beta frame.
   :rtype: 1 x 2 ndarray of floats















   ..
       !! processed by numpydoc !!

.. py:function:: alpha_beta_2_dq(alpha_beta, theta)

   
   Convert a quantity from alpha-beta frame to dq-frame. The common-mode
   component is neglected.

   :param alpha_beta: Quantity in alpha-beta frame.
   :type alpha_beta: 1 x 2 ndarray of floats
   :param theta: Angle of the reference frame in radians.
   :type theta: float

   :returns: Quantity in dq-frame.
   :rtype: 1 x 2 ndarray of floats















   ..
       !! processed by numpydoc !!

.. py:function:: dq_2_alpha_beta(dq, theta)

   
   Convert a quantity from dq-frame to alpha-beta frame. The common-mode
   component is neglected.

   :param dq: Quantity in dq-frame.
   :type dq: 1 x 2 ndarray of floats
   :param theta: Angle of the reference frame in radians.
   :type theta: float

   :returns: Quantity in alpha-beta frame.
   :rtype: 1 x 2 ndarray of floats















   ..
       !! processed by numpydoc !!

.. py:function:: dq_2_abc(dq, theta)

   
   Convert a quantity from dq-frame to abc-frame using the inverse reduced Park
   trasformation. The common-mode component is neglected.

   :param dq: Quantity in dq-frame.
   :type dq: 1 x 2 ndarray of floats
   :param theta: Angle of the reference frame in radians.
   :type theta: float

   :returns: Quantity in abc-frame.
   :rtype: 1 x 3 ndarray of floats















   ..
       !! processed by numpydoc !!

