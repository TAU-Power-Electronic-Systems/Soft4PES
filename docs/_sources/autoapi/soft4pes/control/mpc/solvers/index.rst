soft4pes.control.mpc.solvers
============================

.. py:module:: soft4pes.control.mpc.solvers

.. autoapi-nested-parse::

   
   Solvers for model predictive control (MPC) algorithms.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/control/mpc/solvers/branch_and_bound/index
   /autoapi/soft4pes/control/mpc/solvers/enumeration/index
   /autoapi/soft4pes/control/mpc/solvers/indirect_mpc_qp/index
   /autoapi/soft4pes/control/mpc/solvers/utils/index


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.solvers.iMPCQP
   soft4pes.control.mpc.solvers.BranchAndBound
   soft4pes.control.mpc.solvers.Enumeration


Functions
---------

.. autoapisummary::

   soft4pes.control.mpc.solvers.switching_constraint_violated
   soft4pes.control.mpc.solvers.squared_weighted_second_norm
   soft4pes.control.mpc.solvers.make_QP_matrices
   soft4pes.control.mpc.solvers.make_Gamma
   soft4pes.control.mpc.solvers.make_Upsilon


Package Contents
----------------

.. py:class:: iMPCQP

   Bases: :py:obj:`soft4pes.control.mpc.common.solver_base.MPCSolverBase`


   
   QP solver for indirect MPC.

   This solver reformulates the MPC problem as a quadratic program with linear constraints, solving
   it at each time step to find the optimal control action.

   .. attribute:: QP_matrices

      Namespace containing the precomputed matrices used in the QP problem.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, ctr, y_ref_pred, d_pred=None)

      
      Solve the MPC optimization problem by formulating and solving a quadratic program.

      :param sys: System model.
      :type sys: system object
      :param ctr: Controller object.
      :type ctr: controller object
      :param y_ref_pred: Reference trajectory over the prediction horizon [p.u.].
      :type y_ref_pred: ndarray of floats
      :param d_pred: Disturbance trajectory over the prediction horizon [p.u.].
      :type d_pred: ndarray of floats, optional

      :returns: **u_abc** -- Optimal three-phase modulating signal for the current time step.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


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


.. py:function:: switching_constraint_violated(nl, u_abc, u_km1_abc)

   
   Check if a candidate three-phase switch position violates a switching constraint.
   A three-level converter is not allowed to directly switch from -1 and 1 (and vice versa)
   on one phase.

   :param nl: Number of converter voltage levels (2 or 3).
   :type nl: int
   :param u_abc: Candidate three-phase switch position.
   :type u_abc: 1 x 3 ndarray of ints
   :param u_km1_abc: Previously applied three-phase switch position.
   :type u_km1_abc: 1 x 3 ndarray of ints

   :returns: True if switching constraint is violated, False otherwise.
   :rtype: bool















   ..
       !! processed by numpydoc !!

.. py:function:: squared_weighted_second_norm(vector, Q)

   
   Compute the squared weighted second norm of a vector. The elements of the norm are weighted by
   the weighting matrix Q, i.e. sqrt(x.T * Q * x)^2 = x.T * Q * x.

   :param vector: Input vector.
   :type vector: ndarray
   :param Q: Symmetric positive semi-definite weighting matrix.
   :type Q: ndarray

   :returns: Squared weighted second norm.
   :rtype: float















   ..
       !! processed by numpydoc !!

.. py:function:: make_QP_matrices(ctr)

   
   Construct matrices for the quadratic programming (QP) formulation of MPC.

   This function builds the matrices needed for the QP problem:
   minimize (1/2) * x.T @ H @ x + f.T @ x
   subject to A @ x <= b.

   :param ctr: Controller object.
   :type ctr: controller object

   :returns: Namespace containing the QP matrices.
   :rtype: SimpleNamespace















   ..
       !! processed by numpydoc !!

.. py:function:: make_Gamma(Np, C, A)

   
   Construct the Gamma matrix mapping initial state to future outputs.

   :param Np: Prediction horizon steps.
   :type Np: int
   :param C: Output matrix of the discrete-time state-space model.
   :type C: ndarray
   :param A: State matrix of the discrete-time state-space model.
   :type A: ndarray

   :returns: Gamma matrix.
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: make_Upsilon(Np, C, A, B)

   
   Construct the Upsilon matrix mapping control inputs to future outputs.

   :param Np: Prediction horizon steps.
   :type Np: int
   :param C: Output matrix of the discrete-time state-space model.
   :type C: ndarray
   :param A: State matrix of the discrete-time state-space model.
   :type A: ndarray
   :param B: Input matrix of the discrete-time state-space model.
   :type B: ndarray

   :returns: Upsilon matrix.
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

