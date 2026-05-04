soft4pes.control.mpc.algorithms.pmsm_curr_ctr
=============================================

.. py:module:: soft4pes.control.mpc.algorithms.pmsm_curr_ctr

.. autoapi-nested-parse::

   Model predictive control (MPC) for the stator current of a permanent magnet synchronous machine
   (PMSM).

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.algorithms.pmsm_curr_ctr.PMSMCurrCtr


Module Contents
---------------

.. py:class:: PMSMCurrCtr(solver, Np, lambda_u, disc_method='forward_euler')

   Bases: :py:obj:`soft4pes.control.mpc.common.mpc_base.MPCBase`, :py:obj:`soft4pes.control.common.controller.Controller`


   
   MPC for PMSM stator current control.

   The controller tracks the stator current reference in the alpha-beta frame. The PMSM model is
   time-varying due to rotor position dependency, requiring state-space model updates at each
   control step.

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

      Transforms the current reference from dq to alpha-beta frame using the electrical angle,
      predicts permanent magnet flux disturbance over the horizon, and solves the MPC
      optimization problem to obtain the optimal control action.

      :param sys: System model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Output namespace with field `u_abc` containing the three-phase switch position or
                modulating signal.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


