soft4pes.control.common
=======================

.. py:module:: soft4pes.control.common

.. autoapi-nested-parse::

   
   Common control system components.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/control/common/control_system/index
   /autoapi/soft4pes/control/common/controller/index


Classes
-------

.. autoapisummary::

   soft4pes.control.common.ControlSystem
   soft4pes.control.common.Controller


Package Contents
----------------

.. py:class:: ControlSystem(control_loops, ref_seq, Ts, pwm=None)

   
   ControlSystem class to manage and execute a set of control loops. The class accepts any number
   of control loops and combines them to a complete control system.

   :param control_loops: List of controller instances. The control loops are executed in the order they appear in the
                         list.
   :type control_loops: list
   :param ref_seq: Reference sequences for the control system. The sequences must be of class Sequence. The
                   references are given to the first control loop in the list.
   :type ref_seq: SimpleNamespace
   :param Ts: Sampling interval [s].
   :type Ts: float
   :param pwm: Modulator for generating three-phase switch positions.
   :type pwm: modulator, optional

   .. attribute:: ref_seq

      Reference sequences for the control system. The sequences must be of class Sequence.

      :type: SimpleNamespace

   .. attribute:: data

      Data storage for the control system.

      :type: SimpleNamespace

   .. attribute:: Ts

      Sampling interval [s].

      :type: float

   .. attribute:: pwm

      Modulator for generating three-phase switch positions.

      :type: modulator, optional

   .. attribute:: control_loops

      List of controller instances.

      :type: list















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, conv, kTs)

      
      Execute the control system for a given discrete time step. The control system
      1. Gets the references for the current time step.
      2. Executes the control loops in the order they appear in the list.
      3. Generates the three-phase switch position if modulator is used.

      :param sys: System model.
      :type sys: object
      :param conv: Converter model.
      :type conv: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **uk_abc** -- Three-phase switch position or modulating signal.
      :rtype: ndarray















      ..
          !! processed by numpydoc !!


   .. py:method:: get_references(kTs)

      
      Get the references for the current time step. A new SimpleNamespace object is created and
      the '_seq' subscript is removed from the attribute names.

      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **ref** -- References for the first control loop of the control system.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: save_data(kTs)

      
      Save the current time step to the control system data.

      :param kTs: Current discrete time instant [s].
      :type kTs: float















      ..
          !! processed by numpydoc !!


   .. py:method:: get_control_system_data()

      
      Fetch and save the data of the individual control loops. The data is saved with the name of
      the control loop class.
















      ..
          !! processed by numpydoc !!


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


   .. py:method:: execute(sys, conv, kTs)
      :abstractmethod:


      
      Execute the controller.

      :param sys: System model.
      :type sys: object
      :param conv: Converter model.
      :type conv: object
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


