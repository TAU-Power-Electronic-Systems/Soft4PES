soft4pes.control.mpc.common.solver_base
=======================================

.. py:module:: soft4pes.control.mpc.common.solver_base

.. autoapi-nested-parse::

   Base class for MPC solvers.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.common.solver_base.MPCSolverBase


Functions
---------

.. autoapisummary::

   soft4pes.control.mpc.common.solver_base.make_soft_constraint_matrices


Module Contents
---------------

.. py:function:: make_soft_constraint_matrices(soft_constraints_max, soft_constr_weights)

   
   Create matrices for soft constraint formulation in MPC.

   :param soft_constraints_max: Maximum allowed values for constrained variables [p.u.].
   :type soft_constraints_max: float or ndarray
   :param soft_constr_weights: Weighting matrix in the objective function for the soft constraints.
   :type soft_constr_weights: float or ndarray

   :returns: Namespace containing soft constraint matrices.
   :rtype: SimpleNamespace















   ..
       !! processed by numpydoc !!

.. py:class:: MPCSolverBase

   Bases: :py:obj:`abc.ABC`


   
   Abstract base class for MPC solvers.

   This class provides common initialization and soft constraint handling
   for all MPC solver implementations.

   .. attribute:: soft_constraint_matrices

      Namespace containing soft constraint matrices (M, W_tilde, K_inv_tilde, N, Nc, R).

      :type: SimpleNamespace or None

   .. attribute:: initialized

      Flag indicating whether solver-specific initialization has been performed.

      :type: bool















   ..
       !! processed by numpydoc !!

   .. py:method:: init_soft_constraints(ctr)

      
      Initialize soft constraint matrices if needed.

      This method should be called during solver initialization to set up
      soft constraint matrices based on controller configuration.

      :param ctr: Controller object with soft constraint configuration.
      :type ctr: controller object















      ..
          !! processed by numpydoc !!


   .. py:method:: __call__(sys, ctr, y_ref, d_pred=None)
      :abstractmethod:


      
      Solve the MPC optimization problem.

      :param sys: System model.
      :type sys: system object
      :param ctr: Controller object.
      :type ctr: controller object
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats
      :param d_pred: Disturbance prediction vector [p.u.].
      :type d_pred: ndarray of floats, optional

      :returns: **u_abc** -- Optimal control input (three-phase switch position or modulating signal).
      :rtype: ndarray















      ..
          !! processed by numpydoc !!


