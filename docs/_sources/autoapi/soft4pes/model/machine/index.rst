soft4pes.model.machine
======================

.. py:module:: soft4pes.model.machine

.. autoapi-nested-parse::

   
   Machine models.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/model/machine/base_machine/index
   /autoapi/soft4pes/model/machine/induction_machine/index
   /autoapi/soft4pes/model/machine/induction_machine_param/index
   /autoapi/soft4pes/model/machine/pmsm/index
   /autoapi/soft4pes/model/machine/pmsm_param/index


Classes
-------

.. autoapisummary::

   soft4pes.model.machine.BaseMachine
   soft4pes.model.machine.InductionMachineParameters
   soft4pes.model.machine.PMSM
   soft4pes.model.machine.PMSMParameters


Package Contents
----------------

.. py:class:: BaseMachine(Vm_R_SI, Im_R_SI, fm_R_SI, npp, pf)

   
   Base values for a machine.

   The class computes the base values for a machine based on the rated values.

   :param Vm_R_SI: Rated voltage of the machine [V] (line-to-line rms voltage).
   :type Vm_R_SI: float
   :param Im_R_SI: Rated current of the machine [A] (line rms current).
   :type Im_R_SI: float
   :param fm_R_SI: Rated frequency [Hz].
   :type fm_R_SI: float
   :param npp: Number of pole pairs.
   :type npp: int
   :param pf: Power factor.
   :type pf: float

   .. attribute:: V

      Base voltage [V].

      :type: float

   .. attribute:: I

      Base current [A].

      :type: float

   .. attribute:: w

      Base angular frequency [rad/s].

      :type: float

   .. attribute:: S

      Base apparent power [VA].

      :type: float

   .. attribute:: Z

      Base impedance [Ohm].

      :type: float

   .. attribute:: L

      Base inductance [H].

      :type: float

   .. attribute:: T

      Base torque [Nm].

      :type: float















   ..
       !! processed by numpydoc !!

.. py:class:: InductionMachineParameters(fs_SI, pf, Rs_SI, Rr_SI, Lls_SI, Llr_SI, Lm_SI, base)

   
   Parameters for the InductionMachine.

   :param fs_SI: Synchronous (stator) electrical frequency [Hz].
   :type fs_SI: float
   :param pf_SI: Power factor.
   :type pf_SI: float
   :param Rs_SI: Stator resistance [Ohm].
   :type Rs_SI: float
   :param Rr_SI: Rotor resistance [Ohm].
   :type Rr_SI: float
   :param Lls_SI: Stator leakage inductance [H].
   :type Lls_SI: float
   :param Llr_SI: Rotor leakage inductance [H].
   :type Llr_SI: float
   :param Lm_SI: Mutual inductance [H].
   :type Lm_SI: float
   :param base: Base values.
   :type base: base value object

   .. attribute:: ws

      Synchronous (stator) electrical angular frequency [p.u.].

      :type: float

   .. attribute:: pf

      Power factor.

      :type: float

   .. attribute:: Rs

      Stator resistance [p.u.].

      :type: float

   .. attribute:: Rr

      Rotor resistance [p.u.].

      :type: float

   .. attribute:: Lls

      Stator leakage inductance [p.u.].

      :type: float

   .. attribute:: Llr

      Rotor leakage inductance [p.u.].

      :type: float

   .. attribute:: Lm

      Mutual inductance [p.u.].

      :type: float















   ..
       !! processed by numpydoc !!

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


.. py:class:: PMSMParameters(fs_SI, pf_SI, Rs_SI, Lsd_SI, Lsq_SI, LambdaPM_SI, base)

   
   Parameters for a permanent magnet synchronous machine (PMSM).

   :param fs_SI: Synchronous electrical frequency [Hz].
   :type fs_SI: float
   :param pf_SI: Power factor.
   :type pf_SI: float
   :param Rs_SI: Stator resistance [Ohm].
   :type Rs_SI: float
   :param Lsd_SI: Stator d-axis inductance [H].
   :type Lsd_SI: float
   :param Lsq_SI: Stator q-axis inductance [H].
   :type Lsq_SI: float
   :param LambdaPM_SI: Permanent magnet flux linkage [Wb].
   :type LambdaPM_SI: float
   :param base: Base values.
   :type base: base value object

   .. attribute:: ws

      Synchronous electrical angular frequency [p.u.].

      :type: float

   .. attribute:: pf

      Power factor.

      :type: float

   .. attribute:: Rs

      Stator resistance [p.u.].

      :type: float

   .. attribute:: Xsd

      Stator d-axis reactance [p.u.].

      :type: float

   .. attribute:: Xsq

      Stator q-axis reactance [p.u.].

      :type: float

   .. attribute:: PsiPM

      Permanent magnet flux linkage [p.u.].

      :type: float

   .. attribute:: kT

      Torque factor [p.u.].

      :type: float















   ..
       !! processed by numpydoc !!

