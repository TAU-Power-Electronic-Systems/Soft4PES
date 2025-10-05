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
   /autoapi/soft4pes/control/common/utils/index


Classes
-------

.. autoapisummary::

   soft4pes.control.common.ControlSystem
   soft4pes.control.common.Controller
   soft4pes.control.common.FirstOrderFilter


Functions
---------

.. autoapisummary::

   soft4pes.control.common.wrap_theta
   soft4pes.control.common.get_modulating_signal
   soft4pes.control.common.magnitude_limiter


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

   .. py:method:: __call__(sys, kTs)

      
      Execute the control system for a given discrete time step. The control system
      1. Gets the references for the current time step.
      2. Executes the control loops in the order they appear in the list.
      3. Outputs a three-phase switch position and the corresponding switching times.

      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **u_abc** -- Three-phase switch position or modulating signal.
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


   .. py:method:: save_data(kTs, u_abc_ref)

      
      Save the current time step to the control system data.

      :param kTs: Current discrete time instant [s].
      :type kTs: float
      :param u_abc_ref: Three-phase switch position or modulating signal.
      :type u_abc_ref: 1 x 3 ndarray















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
   :param v_dc: The dc-link voltage.
   :type v_dc: float

   :returns: The modulating signal in abc-frame.
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

.. py:class:: FirstOrderFilter(w_bw, size)

   
   General first-order filter.

   :param w_bw: The bandwidth of the filter [p.u.].
   :type w_bw: float
   :param size: The size of the signal to be filtered, i.e. the length of the input vector.
   :type size: int

   .. attribute:: w_bw

      The bandwidth of the filter [p.u.].

      :type: float

   .. attribute:: output

      The filtered signal.

      :type: ndarray















   ..
       !! processed by numpydoc !!

   .. py:method:: update(value_in, Ts, base)

      
      Update the filter with a new input signal of the defined size.

      :param value_in: The input signal to be filtered.
      :type value_in: ndarray
      :param Ts: The sampling interval [s].
      :type Ts: float
      :param base: The base values object containing the base angular frequency.
      :type base: object















      ..
          !! processed by numpydoc !!


