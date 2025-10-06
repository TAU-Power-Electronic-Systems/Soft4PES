soft4pes.model.machine.pmsm_param
=================================

.. py:module:: soft4pes.model.machine.pmsm_param

.. autoapi-nested-parse::

   Parameters for a permanent magnet synchronous machine (PMSM).

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.machine.pmsm_param.PMSMParameters


Module Contents
---------------

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

