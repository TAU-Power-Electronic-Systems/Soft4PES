soft4pes.model.machine.base_machine
===================================

.. py:module:: soft4pes.model.machine.base_machine

.. autoapi-nested-parse::

   Base values for a machine.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.machine.base_machine.BaseMachine


Module Contents
---------------

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

