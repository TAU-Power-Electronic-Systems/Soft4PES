soft4pes.model.machine.induction_machine
========================================

.. py:module:: soft4pes.model.machine.induction_machine

.. autoapi-nested-parse::

   Induction machine model. The machine operates at a constant electrical angular rotor speed.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.machine.induction_machine.InductionMachine


Module Contents
---------------

.. py:class:: InductionMachine(par, conv, base, psiS_mag_ref, T_ref_init)

   Bases: :py:obj:`soft4pes.model.common.system_model.SystemModel`


   
   Induction machine model operating at a constant electrical angular rotor speed.
   The state of the system is the stator current and rotor flux in the alpha-beta frame, i.e.,
   [iS_alpha, iS_beta, psiR_alpha, psiR_beta]^T. The machine is modelled with rotor flux alignment.
   The system input is the converter three-phase switch position or modulating signal. The initial
   state of the model is based on the stator flux magnitude reference and torque reference.

   :param par: Induction machine parameters in p.u.
   :type par: InductionMachineParameters
   :param conv: Converter object.
   :type conv: converter object
   :param base: Base values.
   :type base: base value object
   :param psiS_mag_ref: Stator flux magnitude reference [p.u.].
   :type psiS_mag_ref: float
   :param T_ref_init: Initial torque reference [p.u.].
   :type T_ref_init: float

   .. attribute:: data

      Namespace for storing simulation data.

      :type: SimpleNamespace

   .. attribute:: par

      Induction machine parameters in p.u.

      :type: InductionMachineParameters

   .. attribute:: conv

      Converter object.

      :type: converter object

   .. attribute:: base

      Base values.

      :type: base value object

   .. attribute:: x

      Current state of the machine [p.u.].

      :type: 1 x 4 ndarray of floats

   .. attribute:: psiR_mag_ref

      Rotor flux magnitude reference [p.u.].

      :type: float

   .. attribute:: wr

      Electrical angular rotor speed [p.u.].

      :type: float

   .. attribute:: cont_state_space

      The continuous-time state-space model of the system.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: set_initial_state(**kwargs)

      
      Calculates the initial state of the machine based on the torque reference and
      stator flux magnitude reference.

      :param psiS_mag_ref: The stator flux magnitude reference [p.u.].
      :type psiS_mag_ref: float
      :param T_ref_init: The initial torque reference [p.u.].
      :type T_ref_init: float















      ..
          !! processed by numpydoc !!


   .. py:method:: get_steady_state_psir(psiS_mag_ref, T_ref)

      
      Calculates the steady-state rotor flux and rotor speed.

      :param psiS_mag_ref: The stator flux magnitude reference [p.u.].
      :type psiS_mag_ref: float
      :param T_ref: The torque reference [p.u.].
      :type T_ref: float

      :returns: * **psiR_dq** (*1 x 2 ndarray*) -- The steady-state rotor flux in the dq frame [p.u.].
                * **wr** (*float*) -- The steady-state (electrical angular) rotor speed [p.u.].















      ..
          !! processed by numpydoc !!


   .. py:method:: calc_stator_current(psiR_dq, T_ref)

      
      Calculate the steady-state stator current.

      :param psiR_dq: The rotor flux in the dq frame [p.u.].
      :type psiR_dq: 1 x 2 ndarray
      :param T_ref: The torque reference [p.u.].
      :type T_ref: float

      :returns: The stator current in the dq frame [p.u.].
      :rtype: 1 x 2 ndarray















      ..
          !! processed by numpydoc !!


   .. py:method:: get_continuous_state_space()

      
      Calculate the continuous-time state-space model of the system.

      :returns: A SimpleNamespace object containing matrices F and G of the continuous-time state-space
                model.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(matrices, uk_abc, kTs)

      
      Calculate the next state of the system.

      :param uk_abc: Converter three-phase switch position or modulating signal.
      :type uk_abc: 1 x 3 ndarray of floats
      :param matrices: A SimpleNamespace object containing the state-space model matrices.
      :type matrices: SimpleNamespace
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: The next state of the system.
      :rtype: 1 x 4 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_measurements(kTs)

      
      Update the measurement data of the system.

      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: A SimpleNamespace object containing the machine torque.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


