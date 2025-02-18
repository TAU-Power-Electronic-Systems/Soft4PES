soft4pes.control.lin
====================

.. py:module:: soft4pes.control.lin

.. autoapi-nested-parse::

   
   Linear control algorithms for power electronic systems.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/control/lin/grid_curr_ref_gen/index
   /autoapi/soft4pes/control/lin/lcl_conv_curr_ctr/index
   /autoapi/soft4pes/control/lin/lcl_vc_ctr/index
   /autoapi/soft4pes/control/lin/state_space_curr_ctr/index


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.GridCurrRefGen
   soft4pes.control.lin.RLGridStateSpaceCurrCtr
   soft4pes.control.lin.LCLConvCurrCtr
   soft4pes.control.lin.LCLVcCtr


Package Contents
----------------

.. py:class:: GridCurrRefGen

   Bases: :py:obj:`soft4pes.control.common.Controller`


   
   Grid current reference generator. This class generates the grid current reference based on the
   active and reactive power references using grid voltage. The equations are in per unit. Grid
   voltage orientation is assumed, i.e. vg_d is aligned with d-axis of the dq-reference frame.
   Moreover, the positive grid current flows from the converter to the grid.
















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, conv, kTs)

      
      Generate the current reference.

      :param sys: System model.
      :type sys: object
      :param conv: Converter model.
      :type conv: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **output** -- The output of the controller, containing the current reference in dq frame.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


.. py:class:: RLGridStateSpaceCurrCtr(sys, base, Ts, ig_ref_seq_dq)

   
   State-space current controller with anti-windup scheme for grid-connected converter with
   RL load.

   :param sys: System model.
   :type sys: system object
   :param base: Base values.
   :type base: base-value object
   :param Ts: Sampling interval [s].
   :type Ts: float
   :param ig_ref_seq_dq: Current reference sequence instance in dq-frame [p.u.].
   :type ig_ref_seq_dq: Sequence object

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

   .. attribute:: ig_ref_seq_dq

      Current reference sequence instance in dq-frame [p.u.].

      :type: Sequence object

   .. attribute:: data

      Controller data.

      :type: dict















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, conv, kTs)

      
      Perform control.

      :param sys: System model.
      :type sys: system object
      :param conv: Converter model.
      :type conv: converter object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

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


   .. py:method:: save_data(ig_ref, uk_abc, kTs)

      
      Save controller data.

      :param ig_ref: Current reference in alpha-beta frame.
      :type ig_ref: 1 x 2 ndarray of floats
      :param uk_abc: Converter three-phase switch position or modulating signal.
      :type uk_abc: 1 x 3 ndarray of floats
      :param kTs: Current discrete time instant [s].
      :type kTs: float















      ..
          !! processed by numpydoc !!


   .. py:method:: get_control_system_data()

      
      This is a empty method to make different controllers compatible when building the new
      control system structure.
















      ..
          !! processed by numpydoc !!


.. py:class:: LCLConvCurrCtr(sys)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Current Controller for converter current with an LC(L) filter.

   :param sys: System model containing electrical parameters and base values.
   :type sys: object

   .. attribute:: u_ii_comp

      Integrator state for the converter voltage reference in the dq-frame.

      :type: complex

   .. attribute:: v_conv_kp1_comp

      Next converter voltage reference in the dq-frame.

      :type: complex

   .. attribute:: u_km1_abc

      Previous converter voltage reference in the abc-frame.

      :type: ndarray (3,)

   .. attribute:: sys

      System model containing electrical parameters and base values.

      :type: object

   .. attribute:: ctr_pars

      Controller parameters including delta, K_i, k_ii, and K_ti.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: set_sampling_interval(Ts)

      
      Set the sampling interval and compute controller parameters.

      :param Ts: Sampling interval [s].
      :type Ts: float















      ..
          !! processed by numpydoc !!


   .. py:method:: execute(sys, conv, kTs)

      
      Execute the Current Controller (CC) and save the controller data.

      :param sys: System model.
      :type sys: object
      :param conv: Converter model.
      :type conv: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Three-phase modulating signal.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


.. py:class:: LCLVcCtr(sys, i_conv_lim, curr_ctr)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Voltage Controller for the control of the capacitor voltage.

   :param sys: The system model containing electrical parameters and base values.
   :type sys: object
   :param i_conv_lim: The maximum converter current in per unit (p.u.).
   :type i_conv_lim: float
   :param curr_ctr: The current controller containing its controller parameters and attributes.
   :type curr_ctr: object

   .. attribute:: u_iu_comp

      Integrator state for the converter voltage reference in the dq-frame.

      :type: complex

   .. attribute:: sys

      System model containing electrical parameters and base values.

      :type: object

   .. attribute:: i_conv_lim

      The maximum converter current in per unit (p.u.).

      :type: float

   .. attribute:: ctr_pars

      Controller parameters including delta, K_u, k_iu, and K_tu.

      :type: SimpleNamespace

   .. attribute:: curr_ctr

      The current controller containing its controller parameters and attributes.

      :type: object















   ..
       !! processed by numpydoc !!

   .. py:method:: set_sampling_interval(Ts)

      
      Set the sampling interval and compute controller parameters.

      [Ref.]. H.-S. Kim, H.-S. Jung, and S.-K. Sul, “Discrete-time voltage controller for voltage
      source converters with LC ﬁlter based on state-space models,” IEEE Trans. Ind. Appl.,
      vol. 55, no. 1, pp. 529-540, Jan./Feb. 2019.

      :param Ts: Sampling interval [s].
      :type Ts: float















      ..
          !! processed by numpydoc !!


   .. py:method:: execute(sys, conv, kTs)

      
      Execute the Voltage Controller (VC) and save the controller data.

      :param sys: System model.
      :type sys: object
      :param conv: Converter model.
      :type conv: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: The converter current reference in dq-frame for Current Controller (CC).
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


