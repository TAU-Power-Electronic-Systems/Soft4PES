soft4pes.model.machine.induction_machine_param
==============================================

.. py:module:: soft4pes.model.machine.induction_machine_param

.. autoapi-nested-parse::

   Parameters for an induction machine.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.machine.induction_machine_param.InductionMachineParameters


Module Contents
---------------

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

