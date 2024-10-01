soft4pes.control.lin.lin_curr_ctr
=================================

.. py:module:: soft4pes.control.lin.lin_curr_ctr

.. autoapi-nested-parse::

   PI current controller for grid-connected converter with RL load

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.lin_curr_ctr.RLGridPICurrCtr


Module Contents
---------------

.. py:class:: RLGridPICurrCtr(sys, base, Ts, i_ref_seq_dq)

   
   PI current controller for grid-connected converter with RL load

   :param sys: System model.
   :type sys: system object
   :param base: Base values.
   :type base: base-value object
   :param Ts: Sampling interval [s].
   :type Ts: float
   :param i_ref_seq_dq: Current reference sequence instance in dq-frame [p.u.].
   :type i_ref_seq_dq: Sequence object

   .. attribute:: Rg

      Resistance [p.u.].

      :type: float

   .. attribute:: Xg

      Reactance [p.u.].

      :type: float

   .. attribute:: base

      Base values.

      :type: base-value object

   .. attribute:: Ts

      Sampling interval [s].

      :type: float

   .. attribute:: Ts_pu

      Sampling interval [p.u.].

      :type: float

   .. attribute:: alpha_c

      Controller bandwidth [p.u.]

      :type: float

   .. attribute:: k_p

      Proportional gain [p.u.]

      :type: float

   .. attribute:: k_i

      Proportional gain [p.u.]

      :type: float

   .. attribute:: integral_error_d

      Current error instance in d-frame [p.u.].

      :type: float

   .. attribute:: integral_error_q

      Current error instance in q-frame [p.u.].

      :type: float

   .. attribute:: i_ref_seq_dq

      Current reference sequence instance in dq-frame [p.u.].

      :type: Sequence object

   .. attribute:: sim_data

      Controller data.

      :type: dict















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, conv, t)

      
      Perform control.

      :param sys: System model.
      :type sys: system object
      :param conv: Converter model.
      :type conv: converter object
      :param t: Current time [s].
      :type t: float

      :returns: Modulating signal.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: pi_controller(i_dq, i_ref_dq)

      
      PI controller in dq frame.

      :param i_dq: Grid Current in dq frame [p.u.].
      :type i_dq: 1 x 2 ndarray of floats
      :param i_ref_dq: Reference current in dq frame [p.u.].
      :type i_ref_dq: 1 x 2 ndarray of floats

      :returns: Converter voltage reference in dq frame [p.u.].
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: save_data(ig_ref, u_k, t)

      
      Save controller data.

      :param ig_ref: Current reference in alpha-beta frame.
      :type ig_ref: 1 x 2 ndarray of floats
      :param u_k: Converter three-phase switch position.
      :type u_k: 1 x 3 ndarray of ints
      :param t: Current time [s].
      :type t: float















      ..
          !! processed by numpydoc !!


