soft4pes.control.mpc.solvers.utils
==================================

.. py:module:: soft4pes.control.mpc.solvers.utils

.. autoapi-nested-parse::

   Utility functions for solvers used for model predictive control (MPC).

   ..
       !! processed by numpydoc !!


Functions
---------

.. autoapisummary::

   soft4pes.control.mpc.solvers.utils.switching_constraint_violated
   soft4pes.control.mpc.solvers.utils.squared_weighted_second_norm
   soft4pes.control.mpc.solvers.utils.compute_next_state
   soft4pes.control.mpc.solvers.utils.compute_step_ell_cost
   soft4pes.control.mpc.solvers.utils.make_QP_matrices
   soft4pes.control.mpc.solvers.utils.make_Gamma
   soft4pes.control.mpc.solvers.utils.make_Upsilon


Module Contents
---------------

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

.. py:function:: compute_next_state(state_space, x_ell, u_ell_abc, d_pred, ell)

   
   Compute the next state using discrete-time state-space.

   :param state_space: Discrete-time state-space model.
   :type state_space: SimpleNamespace
   :param x_ell: State vector at prediction step ell [p.u.].
   :type x_ell: ndarray
   :param u_ell_abc: Three-phase switch position or modulating signal at step ell.
   :type u_ell_abc: ndarray
   :param d_pred: Disturbance trajectory over the prediction horizon [p.u.].
   :type d_pred: ndarray or None
   :param ell: Current prediction step index.
   :type ell: int

   :returns: State vector at prediction step ell+1 [p.u.].
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: compute_step_ell_cost(ctr, y_ref_pred, u_ell_abc, u_ell_abc_prev, x_ell_next, ell, soft_constraint_matrices)

   
   Compute the total cost for a single prediction step.

   :param ctr: Controller object.
   :type ctr: object
   :param y_ref_pred: Reference trajectory over the prediction horizon [p.u.].
   :type y_ref_pred: ndarray
   :param u_ell_abc: Three-phase switch position or modulating signal at step ell.
   :type u_ell_abc: 1 x 3 ndarray of ints or floats
   :param u_ell_abc_prev: Three-phase switch position or modulating signal from the previous step.
   :type u_ell_abc_prev: 1 x 3 ndarray of ints or floats
   :param x_ell_next: State vector at step ell+1 [p.u.].
   :type x_ell_next: ndarray
   :param ell: Current prediction step index.
   :type ell: int
   :param soft_constraint_matrices: Namespace containing soft constraint matrices.
   :type soft_constraint_matrices: SimpleNamespace or None

   :returns: Total cost for prediction step ell.
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

