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
   /autoapi/soft4pes/control/lin/im_foc_curr_ctr/index
   /autoapi/soft4pes/control/lin/l_conv_curr_ctr/index
   /autoapi/soft4pes/control/lin/lcl_conv_curr_ctr/index
   /autoapi/soft4pes/control/lin/lcl_grid_curr_ctr_wacfb/index
   /autoapi/soft4pes/control/lin/lcl_vc_ctr/index
   /autoapi/soft4pes/control/lin/pll/index
   /autoapi/soft4pes/control/lin/rfpsc/index


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.GridCurrRefGen
   soft4pes.control.lin.LCLConvCurrCtr
   soft4pes.control.lin.LConvCurrCtr
   soft4pes.control.lin.LCLVcCtr
   soft4pes.control.lin.RFPSC
   soft4pes.control.lin.LCLGridCurrCtrWACFB
   soft4pes.control.lin.PLL
   soft4pes.control.lin.FOCCurrCtr


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

   .. py:method:: execute(sys, kTs)

      
      Generate the current reference.

      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **output** -- The output of the controller, containing the grid current reference and the grid or PLL
                angle (theta).
      :rtype: SimpleNamespace















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


.. py:class:: LConvCurrCtr(sys)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Current Controller for converter (or grid) current with an L filter.

   :param sys: System model.
   :type sys: object

   .. attribute:: i_conv_ii_dq

      Integrator state of the PI-controller.

      :type: ndarray (2,)

   .. attribute:: sys

      System model.

      :type: object

   .. attribute:: ctr_pars

      Controller parameters.

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


.. py:class:: RFPSC(sys, Ra=0.2, Kp=None, w_bw=0.1)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Reference-feedforward power synchronization control (RFPSC).

   :param sys: System model.
   :type sys: system object
   :param Ra: Virtual damping resistance [p.u.].
   :type Ra: float, optional
   :param Kp: Proportional gain of the active power droop control [p.u.]. If not provided, it is
              calculated based on the nominal frequency, nominal grid peak voltage and the virtual
              damping resistance.
   :type Kp: float, optional
   :param w_bw: Current filter bandwidth [p.u.].
   :type w_bw: float, optional

   .. attribute:: Ra

      Virtual damping resistance [p.u.].

      :type: float

   .. attribute:: theta_c

      The angle of the synchronous reference frame set by the droop control. The initial angle
      is set to -pi/2 to align the q-axis with the grid voltage.

      :type: float

   .. attribute:: ig_filter

      First-order filter for the current.

      :type: FirstOrderFilter

   .. attribute:: Kp

      Proportional gain of the active power droop control [p.u.]. Recommended selection is
      Kp = wg * Ra / Vg, where wg is the nominal grid angular frequency, Ra is the virtual damping
      resistance (default 0.2 p.u.) and Vg is the nominal grid peak voltage. If value is not
      provided, nominal grid angular frequency and nominal grid peak voltage are assumed to be
      1 p.u. For more details on the tuning and default values, see the reference above.

      :type: float















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Execute the RFPSC control algorithm.

      :param sys: The system model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: A SimpleNamespace object containing the modulating signal for the converter (u_abc) and
                a capacitor voltage reference in case LC(L) filter is used (vc_ref).
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


.. py:class:: LCLGridCurrCtrWACFB(sys, gamma=None, xi=None, alpha_d=0.3)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Grid current controller for a converter with LCL filter based on weighted average based (WAC)
   feedback.

   :param sys: System model containing electrical parameters and base values.
   :type sys: object

   .. attribute:: sys

      System model containing electrical parameters and base values.

      :type: object

   .. attribute:: gamma

      Tuning parameter for the high-pass filter (HPF) in the damping compensation path.

      :type: float

   .. attribute:: xi

      Damping ratio for the damping compensation path.

      :type: float

   .. attribute:: alpha_d

      Tuning parameter for the integrator gain in the main control path.

      :type: float

   .. attribute:: ctr

      Controller parameters and filters.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: set_sampling_interval(Ts)

      
      Set the sampling interval and compute controller parameters.

      :param Ts: Sampling interval in seconds.
      :type Ts: float















      ..
          !! processed by numpydoc !!


   .. py:method:: execute(sys, kTs)

      
      Execute the controller.

      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **output** -- The output of the controller after execution.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


.. py:class:: PLL(sys, zeta=np.sqrt(2) / 2, wn=2 * np.pi * 20)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Phase-locked loop (PLL) implementation.
















   ..
       !! processed by numpydoc !!

   .. py:method:: set_sampling_interval(Ts)

      
      Set the sampling interval and compute controller parameters.

      :param Ts: Sampling interval [s].
      :type Ts: float















      ..
          !! processed by numpydoc !!


   .. py:method:: execute(sys, kTs)

      
      Execute the PLL control algorithm to estimate the PCC voltage angle.
      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **output** -- The output of the PLL, containing the estimated PCC voltage angle (theta) and
                the active and reactive power references.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


.. py:class:: FOCCurrCtr(sys)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Field-oriented control (FOC) for the current control of a induction machine (IM).

   :param sys: System model.
   :type sys: object

   .. attribute:: iS_ii_dq

      Integrator state of the PI-controller.

      :type: ndarray (2,)

   .. attribute:: sys

      System model.

      :type: object

   .. attribute:: ctr_pars

      Controller parameters.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: set_sampling_interval(Ts)

      
      Set the sampling interval and compute controller parameters.

      Magnitude optimum criterion based on:
      J. W. Umland and M. Safiuddin,
      "Magnitude and symmetric optimum criterion for the design
      of linear control systems: what is it and how does it compare with the others?,"
      in IEEE Transactions on Industry Applications, vol. 26, no. 3,
      pp. 489-497, May-June 1990, doi: 10.1109/28.55967

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


