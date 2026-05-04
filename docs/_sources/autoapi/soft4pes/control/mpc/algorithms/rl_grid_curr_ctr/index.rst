soft4pes.control.mpc.algorithms.rl_grid_curr_ctr
================================================

.. py:module:: soft4pes.control.mpc.algorithms.rl_grid_curr_ctr

.. autoapi-nested-parse::

   Model predictive control (MPC) for the grid current.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.algorithms.rl_grid_curr_ctr.RLGridCurrCtr


Module Contents
---------------

.. py:class:: RLGridCurrCtr(solver, Np, lambda_u, disc_method='forward_euler')

   Bases: :py:obj:`soft4pes.control.mpc.common.mpc_base.MPCBase`, :py:obj:`soft4pes.control.common.controller.Controller`


   
   Model predictive control (MPC) for grid current. The converter is connected directly to the
   grid.

   :param solver: Solver for an MPC algorithm.
   :type solver: solver object
   :param Np: Prediction horizon steps.
   :type Np: int
   :param lambda_u: Weighting factor for the control effort.
   :type lambda_u: float
   :param disc_method: Discretization method for the state-space model ('forward_euler' or
                       'exact_discretization'). Default is 'forward_euler'.
   :type disc_method: str, optional















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Execute one control step of the MPC algorithm.

      Transforms the current reference from dq to alpha-beta frame using the grid voltage angle,
      predicts grid voltage disturbance over the horizon, and solves the MPC optimization problem
      to obtain the optimal control action.

      :param sys: System model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Output namespace with field `u_abc` containing the three-phase
                switch position or modulating signal.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


