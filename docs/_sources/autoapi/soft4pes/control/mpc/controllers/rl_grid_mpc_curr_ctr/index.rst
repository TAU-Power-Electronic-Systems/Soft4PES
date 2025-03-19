soft4pes.control.mpc.controllers.rl_grid_mpc_curr_ctr
=====================================================

.. py:module:: soft4pes.control.mpc.controllers.rl_grid_mpc_curr_ctr

.. autoapi-nested-parse::

   Model predictive control (MPC) for the control of the grid current (RL grid).

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.controllers.rl_grid_mpc_curr_ctr.RLGridMpcCurrCtr


Module Contents
---------------

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


