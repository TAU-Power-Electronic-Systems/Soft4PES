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
   /autoapi/soft4pes/control/mpc/controllers/rl_grid_mpc_curr_ctr/index


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.controllers.RLGridMpcCurrCtr
   soft4pes.control.mpc.controllers.IMMpcCurrCtr


Package Contents
----------------

.. py:class:: RLGridMpcCurrCtr(solver, lambda_u, Np)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Model predictive control (MPC) for RL grid. The controller aims to track
   the grid current in the alpha-beta frame.

   :param solver: Solver for an MPC algorithm.
   :type solver: solver object
   :param lambda_u: Weighting factor for the control effort.
   :type lambda_u: float
   :param Np: Prediction horizon steps.
   :type Np: int

   .. attribute:: lambda_u

      Weighting factor for the control effort.

      :type: float

   .. attribute:: Np

      Prediction horizon.

      :type: int

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

   .. py:method:: execute(sys, conv, kTs)

      
      Perform MPC and save the controller data.

      :param sys: System model.
      :type sys: system object
      :param conv: Converter model.
      :type conv: converter object
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


.. py:class:: IMMpcCurrCtr(solver, lambda_u, Np, Ts, T_ref)

   
   Model predictive current control for an induction machine. The controller aims to track
   the stator current in the alpha-beta frame. The current reference is calculated based on the
   torque reference.

   :param solver: Solver for an MPC algorithm.
   :type solver: solver object
   :param lambda_u: Weighting factor for the control effort.
   :type lambda_u: float
   :param Np: Prediction horizon.
   :type Np: int
   :param Ts: Sampling interval [s].
   :type Ts: float
   :param T_ref_seq: Torque reference sequence [p.u.].
   :type T_ref_seq: Sequence object

   .. attribute:: solver

      Solver for MPC.

      :type: solver object

   .. attribute:: lambda_u

      Weighting factor for the control effort.

      :type: float

   .. attribute:: Np

      Prediction horizon steps.

      :type: int

   .. attribute:: Ts

      Sampling interval [s].

      :type: float

   .. attribute:: T_ref_seq

      Torque reference sequence [p.u.].

      :type: Sequence object

   .. attribute:: u_km1_abc

      Previous (step k-1) three-phase switch position or modulating signal.

      :type: 1 x 3 ndarray of floats

   .. attribute:: state_space

      The state-space model of the system.

      :type: SimpleNamespace

   .. attribute:: C

      Output matrix.

      :type: 2 x 4 ndarray of ints

   .. attribute:: data

      Controller data.

      :type: dict















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, conv, kTs)

      
      Perform MPC.

      :param sys: System model.
      :type sys: system object
      :param conv: Converter model.
      :type conv: converter object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Three-phase switch position or modulating signals.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(sys, xk, uk_abc, k)

      
      Calculate the next state of the system.

      :param sys: The system object, not used in this method.
      :type sys: system object
      :param xk: The current state of the system [p.u.] (step k).
      :type xk: 1 x 2 ndarray of floats
      :param uk_abc: Converter three-phase switch position or modulating signal.
      :type uk_abc: 1 x 3 ndarray of floats
      :param k: The solver prediction step. Not used in this method.
      :type k: int

      :returns: The next state of the system [p.u.] (step k+1).
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: save_data(iS_ref, uk_abc, T_ref, kTs)

      
      Save controller data.

      :param iS_ref: Current reference in alpha-beta frame [p.u.].
      :type iS_ref: 1 x 2 ndarray of floats
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


