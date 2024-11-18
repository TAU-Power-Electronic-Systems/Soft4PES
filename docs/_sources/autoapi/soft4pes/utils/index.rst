soft4pes.utils
==============

.. py:module:: soft4pes.utils

.. autoapi-nested-parse::

   
   Reference frame transformations and reference sequence generation.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/utils/conversions/index
   /autoapi/soft4pes/utils/sequence/index


Classes
-------

.. autoapisummary::

   soft4pes.utils.Sequence


Functions
---------

.. autoapisummary::

   soft4pes.utils.abc_2_alpha_beta
   soft4pes.utils.alpha_beta_2_abc
   soft4pes.utils.alpha_beta_2_dq
   soft4pes.utils.dq_2_alpha_beta
   soft4pes.utils.dq_2_abc


Package Contents
----------------

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

.. py:class:: Sequence(times, values)

   
   Sequence class can be used to generate a sequence of values over time.

   The time array must be increasing. The output values are interpolated
   between the data points.

   :param times: Time instants is seconds.
   :type times: n x 1 ndarray of floats
   :param values: Output values.
   :type values: n x m ndarray of floats

   .. attribute:: times

      Time instants is seconds.

      :type: n x 1 ndarray of floats

   .. attribute:: values

      Output values.

      :type: n x m ndarray of floats















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(kTs)

      
      Interpolate the output.

      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Interpolated output.
      :rtype: 1 x m ndarray of floats















      ..
          !! processed by numpydoc !!


