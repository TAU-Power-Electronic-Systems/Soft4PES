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

