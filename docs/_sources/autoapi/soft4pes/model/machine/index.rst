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


Classes
-------

.. autoapisummary::

   soft4pes.model.machine.BaseMachine
   soft4pes.model.machine.InductionMachineParameters


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

