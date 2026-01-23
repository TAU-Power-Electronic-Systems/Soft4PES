soft4pes.model.machine.pmsm
===========================

.. py:module:: soft4pes.model.machine.pmsm

.. autoapi-nested-parse::

   Permanent magnet synchronous machine (PMSM) model. The machine operates at a constant electrical
   angular rotor speed.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.machine.pmsm.PMSM


Module Contents
---------------

.. py:class:: PMSM(par, conv, base, T_ref_init, mtpa_lut)

   Bases: :py:obj:`soft4pes.model.common.system_model.SystemModel`


   
   Permanent magnet synchronous machine (PMSM) model. The system is modeled in a alpha-beta frame,
   and the machine operates at a constant electrical angular rotor speed. The state of the system
   is the stator current, and the permanent-magnet flux (i.e., rotor flux) is considered as a
   disturbance. The system input is the converter three-phase switch position or modulating signal.
   The initial state of the model is based on the torque reference.

   :param par: Permanent magnet synchronous machine parameters in p.u.
   :type par: PMSMParameters
   :param conv: Converter object.
   :type conv: converter object
   :param base: Base values.
   :type base: base value object
   :param T_ref_init: Initial torque reference [p.u.].
   :type T_ref_init: float
   :param mtpa_lut: MTPA lookup table for optimal current calculation.
   :type mtpa_lut: MTPALookupTable

   .. attribute:: data

      Namespace for storing simulation data.

      :type: SimpleNamespace

   .. attribute:: par

      Permanent magnet synchronous machine parameters in p.u.

      :type: PMSMParameters

   .. attribute:: conv

      Converter object.

      :type: converter object

   .. attribute:: base

      Base values.

      :type: base value object

   .. attribute:: x

      Current state of the machine [p.u.].

      :type: 1 x 2 ndarray of floats

   .. attribute:: cont_state_space

      The continuous-time state-space model of the system.

      :type: SimpleNamespace

   .. attribute:: state_map

      A dictionary mapping state names to elements of the state vector.

      :type: dict

   .. attribute:: time_varying_model

      Indicates if the system model is time-varying.

      :type: bool

   .. attribute:: theta_el

      Electrical angle of the machine [rad].

      :type: float















   ..
       !! processed by numpydoc !!

   .. py:method:: set_initial_state(**kwargs)

      
      Calculate the initial state of the machine based on the torque reference.

      :param \*\*kwargs: Keyword arguments containing:
                         - T_ref_init : float
                             The initial torque reference [p.u.].
                         - mtpa_lut : MTPALookupTable
                             MTPA lookup table for optimal current calculation.
      :type \*\*kwargs: dict















      ..
          !! processed by numpydoc !!


   .. py:method:: get_stator_current_ref_dq(T_ref)

      
      Get the optimal steady-state stator current using MTPA.

      :param T_ref: The torque reference [p.u.].
      :type T_ref: float

      :returns: The optimal stator current in the dq frame [p.u.].
      :rtype: ndarray















      ..
          !! processed by numpydoc !!


   .. py:method:: get_continuous_state_space()

      
      Calculate the continuous-time state-space model of the system.

      :returns: A SimpleNamespace object containing matrices F and G of the continuous-time state-space
                model.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(matrices, u_abc, kTs, Ts)

      
      Calculate the next state of the system.

      :param matrices: A SimpleNamespace object containing the state-space model matrices A and B.
      :type matrices: SimpleNamespace
      :param u_abc: Converter three-phase switch position or modulating signal [p.u.].
      :type u_abc: 1 x 3 ndarray of floats
      :param kTs: Current discrete time instant [s].
      :type kTs: float
      :param Ts: Sampling interval [s].
      :type Ts: float

      :returns: The next state of the system.
      :rtype: 1 x 4 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_measurements(kTs)

      
      Get the measurement data of the system.

      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: A SimpleNamespace object containing the machine electromagnetic torque Te [p.u.].
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


