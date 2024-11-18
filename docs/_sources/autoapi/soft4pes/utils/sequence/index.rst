soft4pes.utils.sequence
=======================

.. py:module:: soft4pes.utils.sequence

.. autoapi-nested-parse::

   Sequence class can be used to generate a sequence of values over time.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.utils.sequence.Sequence


Module Contents
---------------

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


