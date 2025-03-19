soft4pes.control.lin.lcl_vc_ctr
===============================

.. py:module:: soft4pes.control.lin.lcl_vc_ctr

.. autoapi-nested-parse::

   Voltage Controller (VC) for the control of the capacitor voltage in the three-phase voltage-source
   converter equipped with an LC(L) filter.
   Provide the converter current reference in dq-frame for Current Controller (CC).

   [Ref.]. V. Pirsto, J. Kukkola and M. Hinkkanen, "Multifunctional Cascade Control of Voltage-Source
   Converters Equipped With an LC Filter," IEEE Trans. Ind. Electron., vol. 69, no. 3, pp. 2610-2620,
   March 2022.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.lcl_vc_ctr.LCLVcCtr


Module Contents
---------------

.. py:class:: LCLVcCtr(sys, curr_ctr, I_conv_max=1.2)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Voltage Controller for the control of the capacitor voltage.

   :param sys: The system model containing electrical parameters and base values.
   :type sys: object
   :param curr_ctr: The current controller containing its controller parameters and attributes.
   :type curr_ctr: object
   :param I_conv_max: The maximum converter current in per unit (p.u.).
   :type I_conv_max: float (optional)

   .. attribute:: u_iu_comp

      Integrator state for the converter voltage reference in the dq-frame.

      :type: complex

   .. attribute:: sys

      System model containing electrical parameters and base values.

      :type: object

   .. attribute:: I_conv_max

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


   .. py:method:: execute(sys, kTs)

      
      Execute the Voltage Controller (VC) and save the controller data.

      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: The converter current reference in dq-frame for Current Controller (CC).
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


