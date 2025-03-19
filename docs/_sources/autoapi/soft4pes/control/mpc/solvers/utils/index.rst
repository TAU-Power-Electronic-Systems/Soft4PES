soft4pes.control.mpc.solvers.utils
==================================

.. py:module:: soft4pes.control.mpc.solvers.utils

.. autoapi-nested-parse::

   Utility functions for MPC solvers.

   ..
       !! processed by numpydoc !!


Functions
---------

.. autoapisummary::

   soft4pes.control.mpc.solvers.utils.switching_constraint_violated
   soft4pes.control.mpc.solvers.utils.make_QP_matrices
   soft4pes.control.mpc.solvers.utils.make_Gamma
   soft4pes.control.mpc.solvers.utils.make_Upsilon


Module Contents
---------------

.. py:function:: switching_constraint_violated(nl, uk_abc, u_km1_abc)

   
   Check if a candidate three-phase switch position violates a switching constraint.
   A three-level converter is not allowed to directly switch from -1 and 1 (and vice versa)
   on one phase.

   :param nl: Number of converter voltage levels.
   :type nl: int
   :param uk_abc: three-phase switch position.
   :type uk_abc: 1 x 3 ndarray of ints
   :param u_km1_abc: Previously applied three-phase switch position.
   :type u_km1_abc: 1 x 3 ndarray of ints

   :returns: Constraint violated.
   :rtype: bool















   ..
       !! processed by numpydoc !!

.. py:function:: make_QP_matrices(sys, ctr)

   
   Create the QP matrices.

   :param sys: System model.
   :type sys: system object
   :param ctr: Controller object.
   :type ctr: controller object

   :returns: Namespace containing the QP matrices.
   :rtype: SimpleNamespace















   ..
       !! processed by numpydoc !!

.. py:function:: make_Gamma(Np, C, A)

   
   Make Gamma matrix for the QP.

   :param Np: Prediction horizon.
   :type Np: int
   :param C: Output matrix of the system.
   :type C: ndarray
   :param A: State matrix of the system.
   :type A: ndarray

   :returns: Gamma matrix.
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: make_Upsilon(Np, C, A, B)

   
   Make Upsilon matrix for the QP.

   :param Np: Prediction horizon.
   :type Np: int
   :param C: Output matrix of the system.
   :type C: ndarray
   :param A: State matrix of the system.
   :type A: ndarray
   :param B: Input matrix of the system.
   :type B: ndarray

   :returns: Upsilon matrix.
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

