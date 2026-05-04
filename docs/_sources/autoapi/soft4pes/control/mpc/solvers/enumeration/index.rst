soft4pes.control.mpc.solvers.enumeration
========================================

.. py:module:: soft4pes.control.mpc.solvers.enumeration

.. autoapi-nested-parse::

   Enumeration-based solver for direct model predictive control (MPC) with integer optimization
   problems.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.solvers.enumeration.Enumeration


Module Contents
---------------

.. py:class:: Enumeration

   Bases: :py:obj:`soft4pes.control.mpc.common.solver_base.MPCSolverBase`


   
   Enumeration-based solver for direct MPC with integer optimization problems.

   This solver exhaustively evaluates all possible three-phase switching sequences over the
   prediction horizon, computing the cost for each sequence. The sequence with the minimum cost is
   selected as the optimal solution.

   "Slack variables" can be included in the cost function. In the enumeration-based solvers, slack
   variables are not explicit optimization variables. Instead, they are represented as a function
   of the predicted state that quantifies constraint violation and enters the objective function as
   a penalty term. Therefore, the direct enumeration problem remains a discrete search over three-
   phase switching sequences with an augmented cost, rather than a mixed-integer optimization with
   explicit continuous slack optimization variables.

   .. attribute:: U_seq

      Precomputed array of all possible switching sequences (three-phase switch positions).

      :type: conv.nl^(3*Np) x 3*Np ndarray of ints















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, ctr, y_ref_pred, d_pred=None)

      
      Solve the MPC optimization problem using exhaustive enumeration.

      :param sys: System model.
      :type sys: system object
      :param ctr: Controller object.
      :type ctr: controller object
      :param y_ref_pred: Reference trajectory over the prediction horizon [p.u.].
      :type y_ref_pred: ndarray of floats
      :param d_pred: Disturbance trajectory over the prediction horizon [p.u.].
      :type d_pred: ndarray of floats, optional

      :returns: **u_abc** -- Optimal three-phase switch position for the current time step.
      :rtype: 1 x 3 ndarray of ints















      ..
          !! processed by numpydoc !!


   .. py:method:: solve(sys, ctr, xk, y_ref_pred, u_km1_abc, d_pred)

      
      Compute the cost for all possible three-phase switching sequences.

      This method evaluates the total cost of each precomputed three-phase switching sequence by
      stepping through the prediction horizon. Sequences that violate switching constraints are
      assigned infinite cost.

      :param sys: System model.
      :type sys: system object
      :param ctr: Controller object.
      :type ctr: controller object.
      :param xk: Current state vector at time step k [p.u.].
      :type xk: ndarray of floats
      :param y_ref_pred: Reference trajectory over the prediction horizon [p.u.].
      :type y_ref_pred: ndarray of floats
      :param u_km1_abc: Three-phase switch position applied at step k-1.
      :type u_km1_abc: 1 x 3 ndarray of ints
      :param d_pred: Disturbance trajectory over the prediction horizon [p.u.].
      :type d_pred: ndarray of floats, optional

      :returns: **J** -- Cost array with one entry per switching sequence.
      :rtype: 1 x nl^(3*Np) ndarray of floats















      ..
          !! processed by numpydoc !!


