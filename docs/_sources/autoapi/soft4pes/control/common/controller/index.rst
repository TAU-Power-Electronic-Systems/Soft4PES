soft4pes.control.common.controller
==================================

.. py:module:: soft4pes.control.common.controller

.. autoapi-nested-parse::

   Base class for controllers.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.common.controller.Controller


Module Contents
---------------

.. py:class:: Controller

   Bases: :py:obj:`abc.ABC`


   
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

   .. py:method:: set_sampling_interval(Ts)

      
      Set the sampling interval.

      This method can be extended to set and/or calculate additional parameters.

      :param Ts: Sampling interval [s].
      :type Ts: float















      ..
          !! processed by numpydoc !!


   .. py:method:: execute(sys, kTs)
      :abstractmethod:


      
      Execute the controller.

      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **output** -- The output of the controller after execution.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: save_data()

      
      Save controller data.

      The method saves the current input and output data to the data storage.















      ..
          !! processed by numpydoc !!


