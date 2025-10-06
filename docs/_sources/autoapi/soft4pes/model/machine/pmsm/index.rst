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


   
   Permanent magnet synchronous machine (PMSM) model. The model operates at a constant electrical
   angular rotor speed. The system is modelled in a dq-frame, where the d-axis is aligned with the
   rotor flux. However, the state of the system is the stator current in the alpha-beta frame, and
   thus reference frame conversions are performed during state updates.

   :param par: Permanent magnet synchronous machine parameters in p.u.
   :type par: PMSMParameters
   :param conv: Converter object.
   :type conv: converter object
   :param base: Base values.
   :type base: base value object
   :param T_ref_init: Initial torque reference [p.u.].
   :type T_ref_init: float
   :param i_mag_points: Number of current magnitude points for MTPA trajectory generation. The default is 101.
   :type i_mag_points: int, optional
   :param theta_points: Number of angle points for MTPA trajectory generation. The default is 2001.
   :type theta_points: int, optional

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

      A dictionary mapping states to elements of the state vector.

      :type: dict

   .. attribute:: time_varying_model

      Indicates if the system model is time-varying.

      :type: bool

   .. attribute:: mtpa

      Maximum torque per ampere (MTPA) lookup table.

      :type: MTPALookupTable

   .. attribute:: theta_el

      Electrical angle of the machine [rad].

      :type: float















   ..
       !! processed by numpydoc !!

   .. py:method:: set_initial_state(**kwargs)

      
      Calculates the initial state (stator current) of the machine based on the torque reference.

      :param T_ref_init: The initial torque reference [p.u.].
      :type T_ref_init: float















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

      :returns: A SimpleNamespace object containing matrices F, G1, and G2 of the continuous-time
                state-space model.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(matrices, u_abc, kTs)

      
      Calculate the next state of the system.

      :param u_abc: Converter three-phase switch position or modulating signal.
      :type u_abc: 1 x 3 ndarray of floats
      :param matrices: A SimpleNamespace object containing the state-space model matrices.
      :type matrices: SimpleNamespace
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: The next state of the system.
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_measurements(kTs)

      
      Update the measurement data of the system.

      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: A SimpleNamespace object containing the machine torque and rotor electrical angle.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: update_internal_variables(kTs)

      
      Update the electrical rotor angle of the machine.

      :param kTs: Current discrete time instant [s].
      :type kTs: float















      ..
          !! processed by numpydoc !!


