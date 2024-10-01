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

   /autoapi/soft4pes/control/mpc/solvers/mpc_bnb/index
   /autoapi/soft4pes/control/mpc/solvers/mpc_enum/index
   /autoapi/soft4pes/control/mpc/solvers/utils/index


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.solvers.MpcBnB
   soft4pes.control.mpc.solvers.MpcEnum


Package Contents
----------------

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

   .. py:method:: __call__(sys, conv, ctr, y_ref)

      
      Solve MPC problem by using a simple BnB method.

      :param sys: System model.
      :type sys: system object
      :param conv: Converter model.
      :type conv: converter object
      :param ctr: Controller object.
      :type ctr: controller object
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats

      :returns: **uk** -- The three-phase switch position.
      :rtype: 1 x 3 ndarray of ints















      ..
          !! processed by numpydoc !!


   .. py:method:: solve(sys, conv, ctr, x_ell, y_ref, u_ell_prev, ell=0, J_prev=0)

      
      Recursively compute the cost for different switching sequences.

      :param sys: System model.
      :type sys: object
      :param conv: Converter model.
      :type conv: object
      :param ctr: Controller object.
      :type ctr: object
      :param x_ell: State vector [p.u.].
      :type x_ell: ndarray of floats
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats
      :param u_ell_prev: Previous three-phase switch position.
      :type u_ell_prev: 1 x 3 ndarray of ints
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

   .. py:method:: __call__(sys, conv, ctr, y_ref)

      
      Solve MPC problem with exhaustive enumeration.

      :param sys: System model.
      :type sys: system object
      :param conv: Converter model.
      :type conv: converter object
      :param ctr: Controller object.
      :type ctr: controller object
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats

      :returns: **uk** -- The three-phase switch position with the lowest cost.
      :rtype: 1 x 3 ndarray of ints















      ..
          !! processed by numpydoc !!


   .. py:method:: solve(sys, conv, ctr, xk, y_ref, u_km1)

      
      Recursively compute the cost for different switching sequences

      :param sys: System model.
      :type sys: system object
      :param conv: Converter model.
      :type conv: converter object.
      :param ctr: Controller object.
      :type ctr: controller object.
      :param xk: Current state vector [p.u.].
      :type xk: ndarray of floats
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats
      :param u_km1: Three-phase switch position applied at step k-1.
      :type u_km1: 1 x 3 ndarray of ints

      :returns: **J** -- Cost array.
      :rtype: 1 x nl^(3*Np) ndarray of floats















      ..
          !! processed by numpydoc !!


