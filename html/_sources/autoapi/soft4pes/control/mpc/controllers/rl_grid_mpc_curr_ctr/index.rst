soft4pes.control.mpc.controllers.rl_grid_mpc_curr_ctr
=====================================================

.. py:module:: soft4pes.control.mpc.controllers.rl_grid_mpc_curr_ctr

.. autoapi-nested-parse::

   Model predictive control (MPC) for RL grid.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.controllers.rl_grid_mpc_curr_ctr.RLGridMpcCurrCtr


Module Contents
---------------

.. py:class:: RLGridMpcCurrCtr(solver, lambda_u, Np, Ts, i_ref_seq_dq)

   
   Model predictive control (MPC) for RL grid. The controller aims to track
   the grid current in the alpha-beta frame.

   :param solver: Solver for an MPC algorithm.
   :type solver: solver object
   :param lambda_u: Weighting factor for the control effort.
   :type lambda_u: float
   :param Np: Prediction horizon steps.
   :type Np: int
   :param Ts: Sampling interval [s].
   :type Ts: float
   :param i_ref_seq_dq: Current reference sequence in dq-frame [p.u.].
   :type i_ref_seq_dq: Sequence object

   .. attribute:: lambda_u

      Weighting factor for the control effort.

      :type: float

   .. attribute:: Np

      Prediction horizon.

      :type: int

   .. attribute:: Ts

      Sampling interval [s].

      :type: float

   .. attribute:: u_km1

      Previous three-phase switch position.

      :type: 1 x 3 ndarray of ints

   .. attribute:: i_ref_seq_dq

      Current reference sequence in dq-frame [p.u.].

      :type: Sequence object

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

   .. attribute:: data_sim

      Controller data.

      :type: dict















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, conv, t)

      
      Perform MPC and save the controller data.

      :param sys: System model.
      :type sys: system object
      :param conv: Converter model.
      :type conv: converter object
      :param t: Current time [s].
      :type t: float

      :returns: three-phase switch position or modulating signals.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(sys, xk, uk, k)

      
      Get the next state of the system.

      :param sys: The system model.
      :type sys: system object
      :param xk: The current state of the system.
      :type xk: 1 x 2 ndarray of floats
      :param uk: Converter three-phase switch position.
      :type uk: 1 x 3 ndarray of ints
      :param k: The solver prediction step.
      :type k: int

      :returns: The next state of the system.
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


