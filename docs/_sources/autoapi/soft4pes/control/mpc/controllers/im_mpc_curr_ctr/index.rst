soft4pes.control.mpc.controllers.im_mpc_curr_ctr
================================================

.. py:module:: soft4pes.control.mpc.controllers.im_mpc_curr_ctr

.. autoapi-nested-parse::

   Model predictive current control for an induction machine.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.controllers.im_mpc_curr_ctr.IMMpcCurrCtr


Module Contents
---------------

.. py:class:: IMMpcCurrCtr(solver, lambda_u, Np)

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

   .. attribute:: lambda_u

      Weighting factor for the control effort.

      :type: float

   .. attribute:: Np

      Prediction horizon steps.

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

   .. attribute:: C

      Output matrix.

      :type: 2 x 4 ndarray of ints















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, conv, kTs)

      
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


