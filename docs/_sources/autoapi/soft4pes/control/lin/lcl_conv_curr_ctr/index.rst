soft4pes.control.lin.lcl_conv_curr_ctr
======================================

.. py:module:: soft4pes.control.lin.lcl_conv_curr_ctr

.. autoapi-nested-parse::

   Current Controller (CC) for the control of the converter current with LC(L) filter.

   [Ref.]. V. Pirsto, J. Kukkola and M. Hinkkanen, "Multifunctional Cascade Control of Voltage-Source
   Converters Equipped With an LC Filter," IEEE Trans. Ind. Electron., vol. 69, no. 3,
   pp. 2610-2620, March 2022.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.lcl_conv_curr_ctr.LCLConvCurrCtr


Module Contents
---------------

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


   .. py:method:: execute(sys, kTs)

      
      Execute the Current Controller (CC) and save the controller data.

      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Three-phase modulating signal.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


