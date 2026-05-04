soft4pes.control.mpc.solvers.indirect_mpc_qp
============================================

.. py:module:: soft4pes.control.mpc.solvers.indirect_mpc_qp

.. autoapi-nested-parse::

   This module contains the class IndirectQP, which is used to solve the indirect model predictive
   control (MPC) problem using a quadratic program (QP) solver.

   The formulation of the control problem and the QP matrices are based on:
   M. Rossi, P. Karamanakos, and F. Castelli-Dezza, “An indirect model predictive control method for
   grid-connected three-level neutral point clamped converters with LCL filters,” IEEE Trans. Ind.
   Applicat., vol. 58, no. 3, pp. 3750-3768, May/Jun. 2022. The same states do not have to be both
   controlled (output variables) and constrained.

   The QP is solved using the `qpsolvers` package and the `DAQP` solver (MIT license).

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.solvers.indirect_mpc_qp.iMPCQP


Module Contents
---------------

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


