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


Classes
-------

.. autoapisummary::

   soft4pes.model.machine.BaseMachine
   soft4pes.model.machine.InductionMachine


Package Contents
----------------

.. py:class:: BaseMachine(Vr, Ir, fr, npp, pf)

   
   Base values for a machine.

   The class computes the base values for a machine based on the rated values.

   :param Vr: Rated voltage of the machine [V] (line-to-line rms voltage).
   :type Vr: float
   :param Ir: Rated current of the machine [A] (line rms current).
   :type Ir: float
   :param fr: Rated frequency [Hz].
   :type fr: float
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

.. py:class:: InductionMachine(f, pf, Rs, Rr, Lls, Llr, Lm, base, psiS_mag_ref, T_ref_init)

   
   Induction machine model operating at a constant electrical angular rotor speed.
   The state of the system is the stator current and rotor flux in the alpha-beta frame, i.e.,
   [iS_alpha, iS_beta, psiR_alpha, psiR_beta]^T. The system input is the converter three-phase
   switch position. The initial state of the model is based on the stator flux magnitude reference
   and torque reference.

   :param f: Rated frequency [Hz].
   :type f: float
   :param pf: Power factor.
   :type pf: float
   :param Rs: Stator resistance [Ohm].
   :type Rs: float
   :param Rr: Rotor resistance [Ohm].
   :type Rr: float
   :param Lls: Stator leakage inductance [H].
   :type Lls: float
   :param Llr: Rotor leakage inductance [H].
   :type Llr: float
   :param Lm: Mutual inductance [H].
   :type Lm: float
   :param base: Base values.
   :type base: base value object
   :param psiS_mag_ref: Stator flux magnitude reference [p.u.].
   :type psiS_mag_ref: float
   :param T_ref_init: Initial torque reference [p.u.].
   :type T_ref_init: float

   .. attribute:: w

      Rated angular frequency [p.u.].

      :type: float

   .. attribute:: Rs

      Stator resistance [p.u.].

      :type: float

   .. attribute:: Rr

      Rotor resistance [p.u.].

      :type: float

   .. attribute:: Xls

      Stator leakage reactance [p.u.].

      :type: float

   .. attribute:: Xlr

      Rotor leakage reactance [p.u.].

      :type: float

   .. attribute:: Xm

      Mutual reactance [p.u.].

      :type: float

   .. attribute:: Xs

      Stator self-reactance [p.u.].

      :type: float

   .. attribute:: Xr

      Rotor self-reactance [p.u.].

      :type: float

   .. attribute:: D

      Determinant.

      :type: float

   .. attribute:: kT

      Torque correction factor (needed to have 1 p.u. nominal torque).

      :type: float

   .. attribute:: x0

      Initial state of the machine [p.u.].

      :type: 1 x 4 ndarray of floats

   .. attribute:: x

      Current state of the machine [p.u.].

      :type: 1 x 4 ndarray of floats

   .. attribute:: base

      Base values.

      :type: base value object

   .. attribute:: sim_data

      System data.

      :type: dict















   ..
       !! processed by numpydoc !!

   .. py:method:: get_initial_state(psiS_mag_ref, T_ref_init)

      
      Calculates the initial state of the machine based on the torque reference and
      stator flux magnitude reference.

      :param psiS_mag_ref: The stator flux magnitude reference [p.u.].
      :type psiS_mag_ref: float
      :param T_ref_init: The initial torque reference [p.u.].
      :type T_ref_init: float

      :returns: The initial state {iS, psiR} of the machine [p.u.].
      :rtype: 1 x 4 ndarray















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


   .. py:method:: get_discrete_state_space(v_dc, Ts)

      
      Calculates the discrete-time state-space model of the machine.

      :param v_dc: The converter dc-link voltage [p.u.].
      :type v_dc: float
      :param Ts: Sampling interval [s].
      :type Ts: float

      :returns: The discrete-time state-space model of the machine.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: update_state(u, matrices, t)

      
      Get the next state of the machine.

      :param u: Converter three-phase switch position.
      :type u: 1 x 3 ndarray of floats
      :param matrices: A SimpleNamespace object containing matrices A and B of the state-space model.
      :type matrices: SimpleNamespace
      :param t: Current time [s].
      :type t: float















      ..
          !! processed by numpydoc !!


   .. py:method:: save_data(t)

      
      Save system data.

      :param t: Current time [s].
      :type t: float















      ..
          !! processed by numpydoc !!


