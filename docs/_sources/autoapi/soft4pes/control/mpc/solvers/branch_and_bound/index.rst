soft4pes.control.mpc.solvers.branch_and_bound
=============================================

.. py:module:: soft4pes.control.mpc.solvers.branch_and_bound

.. autoapi-nested-parse::

   Branch-and-bound (BnB) solver for direct model predictive control (MPC) with integer optimization
   problems.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.solvers.branch_and_bound.BranchAndBound


Module Contents
---------------

.. py:class:: BranchAndBound

   Bases: :py:obj:`soft4pes.control.mpc.common.solver_base.MPCSolverBase`


   
   BnB solver for direct MPC with integer optimization problems.

   This solver exhaustively explores the tree of possible three-phase switching sequences using a
   recursive depth-first search with pruning. Branches are pruned when their accumulated cost
   exceeds the current best solution, significantly reducing the search space compared to
   enumeration.

   "Slack variables" can be included in the cost function. In the enumeration-based solvers, slack
   variables are not explicit optimization variables. Instead, they are represented as a function
   of the predicted state that quantifies constraint violation and enters the objective function as
   a penalty term. Therefore, the direct enumeration problem remains a discrete search over three-
   phase switching sequences with an augmented cost, rather than a mixed-integer optimization with
   explicit continuous slack optimization variables.

   .. attribute:: J_min

      Minimum cost found during the search.

      :type: float

   .. attribute:: U_seq

      Sequence of three-phase switch positions (switching sequence) with the lowest cost.

      :type: 1 x 3*Np ndarray of ints

   .. attribute:: U_temp

      Temporary array storing the incumbent switching sequence during recursion.

      :type: 1 x 3*Np ndarray of ints

   .. attribute:: SW_COMB

      All possible three-phase switch positions.

      :type: conv.nl^3 x 3 ndarray of ints















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, ctr, y_ref_pred, d_pred=None)

      
      Solve the MPC optimization problem using the BnB algorithm.

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


   .. py:method:: solve(sys, ctr, x_ell, y_ref_pred, u_ell_abc_prev, d_pred=None, ell=0, J_prev=0)

      
      Recursively explore three-phase switching sequences and prune branches with suboptimal
      costs.

      This method implements the core branch-and-bound logic: for each possible three-phase switch
      position at the current prediction step, it computes the cost and either prunes the branch
      (if cost exceeds J_min) or recursively explores deeper levels. When reaching the final
      prediction step, it updates the best solution if a lower cost is found.

      :param sys: System model.
      :type sys: object
      :param ctr: Controller object.
      :type ctr: object
      :param x_ell: State vector at prediction step ell [p.u.].
      :type x_ell: ndarray of floats
      :param y_ref_pred: Reference trajectory over the prediction horizon [p.u.].
      :type y_ref_pred: ndarray of floats
      :param u_ell_abc_prev: Three-phase switch position from the previous prediction step or the last applied switch
                             position for ell=0.
      :type u_ell_abc_prev: 1 x 3 ndarray of ints
      :param d_pred: Disturbance trajectory over the prediction horizon [p.u.].
      :type d_pred: ndarray of floats, optional
      :param ell: Current prediction step index (default is 0).
      :type ell: int, optional
      :param J_prev: Accumulated cost from previous prediction steps (default is 0).
      :type J_prev: float, optional















      ..
          !! processed by numpydoc !!


