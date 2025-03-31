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

   /autoapi/soft4pes/control/mpc/solvers/mpc_QP/index
   /autoapi/soft4pes/control/mpc/solvers/mpc_bnb/index
   /autoapi/soft4pes/control/mpc/solvers/mpc_enum/index
   /autoapi/soft4pes/control/mpc/solvers/utils/index


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.solvers.IndirectMpcQP
   soft4pes.control.mpc.solvers.MpcBnB
   soft4pes.control.mpc.solvers.MpcEnum


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

.. py:class:: IndirectMpcQP

   
   Problem formulation and QP solver for indirect MPC.

   .. attribute:: QP_matrices

      Namespace containing the matrices used in the QP problem.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, ctr, y_ref)

      
      Formulate and solve the MPC QP.

      :param sys: System model.
      :type sys: system object
      :param ctr: Controller object.
      :type ctr: controller object
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats

      :returns: **uk_abc** -- The three-phase modulating signal.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


.. py:class:: MpcBnB(conv)

   
   Branch-and-bound (BnB) solver for model predictive control (MPC).

   :param conv: Converter model.
   :type conv: converter object

   .. attribute:: J_min

      Minimum cost.

      :type: float

   .. attribute:: U_seq

      Sequence of three-phase switch positions (switching sequence) with the lowest cost.

      :type: 1 x 3*Np ndarray of ints

   .. attribute:: U_temp

      Temporary array for incumbent swithing sequence.

      :type: 1 x 3*Np ndarray of ints

   .. attribute:: SW_COMB

      All possible three-phase switch positions.

      :type: 1 x conv.nl^3 ndarray of ints















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, ctr, y_ref)

      
      Solve MPC problem by using a simple BnB method.

      :param sys: System model.
      :type sys: system object
      :param ctr: Controller object.
      :type ctr: controller object
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats

      :returns: **uk_abc** -- The three-phase switch position.
      :rtype: 1 x 3 ndarray of ints















      ..
          !! processed by numpydoc !!


   .. py:method:: solve(sys, ctr, x_ell, y_ref, u_ell_abc_prev, ell=0, J_prev=0)

      
      Recursively compute the cost for different switching sequences.

      :param sys: System model.
      :type sys: object
      :param ctr: Controller object.
      :type ctr: object
      :param x_ell: State vector [p.u.].
      :type x_ell: ndarray of floats
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats
      :param u_ell_abc_prev: Previous three-phase switch position.
      :type u_ell_abc_prev: 1 x 3 ndarray of ints
      :param ell: Prediction step. The default is 0.
      :type ell: int
      :param J_prev: Previous cost. The default is 0.
      :type J_prev: float















      ..
          !! processed by numpydoc !!


.. py:class:: MpcEnum(conv)

   
   Enumeration-based solver for model predictive control (MPC).

   :param conv: Converter model.
   :type conv: converter object

   .. attribute:: U_seq

      Array for sequences of three-phase switch positions (switching sequences).

      :type: 3*Np x conv.nl^(3*Np) ndarray of ints

   .. attribute:: sw_pos_3ph

      Possible one-phase switch positions.

      :type: 1 x conv.nl ndarray of ints















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, ctr, y_ref)

      
      Solve MPC problem with exhaustive enumeration.

      :param sys: System model.
      :type sys: system object
      :param ctr: Controller object.
      :type ctr: controller object
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats

      :returns: **uk_abc** -- The three-phase switch position with the lowest cost.
      :rtype: 1 x 3 ndarray of ints















      ..
          !! processed by numpydoc !!


   .. py:method:: solve(sys, ctr, xk, y_ref, u_km1_abc)

      
      Recursively compute the cost for different switching sequences

      :param sys: System model.
      :type sys: system object
      :param ctr: Controller object.
      :type ctr: controller object.
      :param xk: Current state vector [p.u.].
      :type xk: ndarray of floats
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats
      :param u_km1_abc: Three-phase switch position applied at step k-1.
      :type u_km1_abc: 1 x 3 ndarray of ints

      :returns: **J** -- Cost array.
      :rtype: 1 x nl^(3*Np) ndarray of floats















      ..
          !! processed by numpydoc !!


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

.. py:function:: squared_weighted_second_norm(vector, Q)

   
   Compute the squared weighted second norm of a vector. The elements of the norm are weighted by
   the weighting matrix Q, i.e. sqrt(x.T * Q * x)^2 = x.T * Q * x.

   :param vector: Vector.
   :type vector: ndarray
   :param Q: Weighting matrix.
   :type Q: ndarray

   :returns: Squared weighted second norm.
   :rtype: float















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

