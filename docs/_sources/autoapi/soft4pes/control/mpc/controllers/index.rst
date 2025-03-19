soft4pes.control.mpc.controllers
================================

.. py:module:: soft4pes.control.mpc.controllers

.. autoapi-nested-parse::

   
   Model predictive control (MPC) for power electronic systems.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/control/mpc/controllers/im_mpc_curr_ctr/index
   /autoapi/soft4pes/control/mpc/controllers/lcl_vc_mpc_ctr/index
   /autoapi/soft4pes/control/mpc/controllers/rl_grid_mpc_curr_ctr/index


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.controllers.LCLVcMpcCtr
   soft4pes.control.mpc.controllers.IMMpcCurrCtr
   soft4pes.control.mpc.controllers.RLGridMpcCurrCtr


Package Contents
----------------

.. py:class:: LCLVcMpcCtr(solver, lambda_u, Np, I_conv_max=1.2, xi_I_conv=1000000.0, disc_method='exact_discretization')

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Model predictive control (MPC) for the control of the capacitor voltage.

   :param solver: Solver for an MPC algorithm.
   :type solver: solver object
   :param lambda_u: Weighting factor for the control effort.
   :type lambda_u: float
   :param Np: Prediction horizon steps.
   :type Np: int
   :param disc_method: Discretization method for the state-space model. Default is 'exact_discretization'.
   :type disc_method: str, optional
   :param I_conv_max: Maximum converter current [p.u.].
   :type I_conv_max: float
   :param xi_I_conv: Slack variable weight for the current constraint.
   :type xi_I_conv: float

   .. attribute:: solver

      Solver for MPC.

      :type: solver object

   .. attribute:: lambda_u

      Weighting factor for the control effort.

      :type: float

   .. attribute:: Np

      Prediction horizon.

      :type: int

   .. attribute:: disc_method

      Discretization method for the state-space model.

      :type: str

   .. attribute:: u_km1_abc

      Previous (step k-1) three-phase switch position or modulating signal.

      :type: 1 x 3 ndarray of floats

   .. attribute:: state_space

      The state-space model of the system.

      :type: SimpleNamespace

   .. attribute:: vg

      Grid voltage [p.u.].

      :type: 1 x 2 ndarray of floats

   .. attribute:: R

      Weight matrix for the soft constraints.

      :type: 1 x 1 ndarray of floats

   .. attribute:: c

      State constraints.

      :type: 1 x 1 ndarray of floats

   .. attribute:: C_constr

      Output matrix for the constrained states.

      :type: 2 x 6 ndarray of ints

   .. attribute:: C

      System output matrix.

      :type: 2 x 6 ndarray of ints

   .. attribute:: Q

      Weighting matrix for the output variables.

      :type: 2 x 2 ndarray of ints















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Perform MPC and save the controller data.

      :param sys: System model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: SimpleNameSpace containing the converter three-phase switch position or modulating
                signal.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(sys, xk, uk_abc, k)

      
      Get the next state of the system.

      :param sys: The system model.
      :type sys: system object
      :param xk: The current state of the system.
      :type xk: 1 x 6 ndarray of floats
      :param uk_abc: Converter three-phase switch position or modulating signal.
      :type uk_abc: 1 x 3 ndarray of floats
      :param k: The solver prediction step.
      :type k: int

      :returns: The next state of the system.
      :rtype: 1 x 6 ndarray of floats















      ..
          !! processed by numpydoc !!


.. py:class:: IMMpcCurrCtr(solver, lambda_u, Np, disc_method='forward_euler')

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Model predictive current control for an induction machine. The controller aims to track
   the stator current in the alpha-beta frame. The current reference is calculated based on the
   torque reference.

   :param solver: Solver for an MPC algorithm.
   :type solver: solver object
   :param lambda_u: Weighting factor for the control effort.
   :type lambda_u: float
   :param Np: Prediction horizon.
   :type Np: int
   :param disc_method: Discretization method for the state-space model. Default is 'forward_euler'.
   :type disc_method: str, optional

   .. attribute:: lambda_u

      Weighting factor for the control effort.

      :type: float

   .. attribute:: Np

      Prediction horizon steps.

      :type: int

   .. attribute:: disc_method

      Discretization method for the state-space model.

      :type: str

   .. attribute:: u_km1_abc

      Previous (step k-1) three-phase switch position or modulating signal.

      :type: 1 x 3 ndarray of floats

   .. attribute:: state_space

      The state-space model of the system.

      :type: SimpleNamespace

   .. attribute:: solver

      Solver for MPC.

      :type: solver object

   .. attribute:: C

      Output matrix.

      :type: 2 x 4 ndarray of ints















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Perform MPC.

      :param sys: System model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Three-phase switch position or modulating signals.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(sys, xk, uk_abc, k)

      
      Get the next state of the system.

      :param sys: The system model.
      :type sys: system object
      :param xk: The current state of the system.
      :type xk: 1 x 4 ndarray of floats
      :param uk_abc: Converter three-phase switch position or modulating signal.
      :type uk_abc: 1 x 3 ndarray of floats
      :param k: The solver prediction step.
      :type k: int

      :returns: The next state of the system.
      :rtype: 1 x 4 ndarray of floats















      ..
          !! processed by numpydoc !!


.. py:class:: RLGridMpcCurrCtr(solver, lambda_u, Np, disc_method='forward_euler')

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Model predictive control (MPC) for RL grid. The controller aims to track
   the grid current in the alpha-beta frame.

   :param solver: Solver for an MPC algorithm.
   :type solver: solver object
   :param lambda_u: Weighting factor for the control effort.
   :type lambda_u: float
   :param Np: Prediction horizon steps.
   :type Np: int
   :param disc_method: Discretization method for the state-space model. Default is 'forward_euler'.
   :type disc_method: str, optional

   .. attribute:: lambda_u

      Weighting factor for the control effort.

      :type: float

   .. attribute:: Np

      Prediction horizon.

      :type: int

   .. attribute:: disc_method

      Discretization method for the state-space model.

      :type: str

   .. attribute:: u_km1_abc

      Previous (step k-1) three-phase switch position or modulating signal.

      :type: 1 x 3 ndarray of floats

   .. attribute:: state_space

      The state-space model of the system.

      :type: SimpleNamespace

   .. attribute:: solver

      Solver for MPC.

      :type: solver object

   .. attribute:: vg

      Grid voltage [p.u.].

      :type: 1 x 2 ndarray of floats

   .. attribute:: C

      Output matrix.

      :type: 2 x 2 ndarray of ints















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Perform MPC and save the controller data.

      :param sys: System model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Three-phase switch position or modulating signals.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(sys, xk, uk_abc, k)

      
      Get the next state of the system.

      :param sys: The system model.
      :type sys: system object
      :param xk: The current state of the system.
      :type xk: 1 x 2 ndarray of floats
      :param uk_abc: Converter three-phase switch position or modulating signal.
      :type uk_abc: 1 x 3 ndarray of floats
      :param k: The solver prediction step.
      :type k: int

      :returns: The next state of the system.
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


