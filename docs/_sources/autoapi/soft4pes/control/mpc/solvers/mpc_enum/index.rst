soft4pes.control.mpc.solvers.mpc_enum
=====================================

.. py:module:: soft4pes.control.mpc.solvers.mpc_enum

.. autoapi-nested-parse::

   Enumeration based solver for Model Predictive Control (MPC).

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.solvers.mpc_enum.MpcEnum


Module Contents
---------------

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


