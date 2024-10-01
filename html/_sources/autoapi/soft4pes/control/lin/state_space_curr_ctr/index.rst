soft4pes.control.lin.state_space_curr_ctr
=========================================

.. py:module:: soft4pes.control.lin.state_space_curr_ctr

.. autoapi-nested-parse::

   State-space current controller with anti-windup scheme for grid-connected converter with
   RL load

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.state_space_curr_ctr.RLGridStateSpaceCurrCtr


Module Contents
---------------

.. py:class:: RLGridStateSpaceCurrCtr(sys, base, Ts, i_ref_seq_dq)

   
   State-space current controller with anti-windup scheme for grid-connected converter with
   RL load.

   :param sys: System model.
   :type sys: system object
   :param base: Base values.
   :type base: base-value object
   :param Ts: Sampling interval [s].
   :type Ts: float
   :param i_ref_seq_dq: Current reference sequence instance in dq-frame [p.u.].
   :type i_ref_seq_dq: Sequence object

   .. attribute:: Rf

      Resistance [p.u.].

      :type: float

   .. attribute:: Xf

      Reactance [p.u.].

      :type: float

   .. attribute:: Ts

      Sampling interval [s].

      :type: float

   .. attribute:: Ts_pu

      Sampling interval [p.u.].

      :type: float

   .. attribute:: ctr_pars

      A SimpleNamespace object containing controller parameters delta, K_i, k_ii and K_ti

      :type: SimpleNamespace

   .. attribute:: uc_ii_dq

      Converter voltage reference after current controller integrator in dq frame [p.u.].

      :type: 1 x 2 ndarray of floats

   .. attribute:: uc_km1_dq

      Previous converter voltage reference in dq frame [p.u.].

      :type: 1 x 2 ndarray of floats

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


   .. py:method:: get_state_space_ctr_pars()

      
      Calculate state-space controller parameters.

      :returns: Controller parameters.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: state_space_controller(ic_dq, ic_ref_dq, uf_dq, u_max)

      
      State-space controller in dq frame.

      :param ic_dq: Grid Current in dq frame [p.u.].
      :type ic_dq: 1 x 2 ndarray of floats
      :param ic_ref_dq: Reference current in dq frame [p.u.].
      :type ic_ref_dq: 1 x 2 ndarray of floats
      :param uf_dq: Grid voltage in dq frame [p.u.] (In case: Without considering the filter).
      :type uf_dq: 1 x 2 ndarray of floats
      :param u_max: Maximum converter output voltage [p.u.].
      :type u_max: float

      :returns: Converter voltage reference in dq frame [p.u.].
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: voltage_reference_limiter(u_max, uc_ref_dq_unlim)

      
      limit the converter voltage reference.

      :param u_max: Maximum converter output voltage [p.u.].
      :type u_max: float
      :param uc_ref_dq_unlim: Unlimited converter voltage reference [p.u.].
      :type uc_ref_dq_unlim: 1 x 2 ndarray of floats

      :returns: Limited converter voltage reference [p.u.].
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


