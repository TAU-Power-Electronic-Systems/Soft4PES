soft4pes.control.mpc.algorithms.lcl_grid_vc_ctr
===============================================

.. py:module:: soft4pes.control.mpc.algorithms.lcl_grid_vc_ctr

.. autoapi-nested-parse::

   Model predictive control (MPC) for grid-connected converters with LCL filter. The controller
   tracks only the filter capacitor voltage.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.algorithms.lcl_grid_vc_ctr.LCLGridVcCtr


Module Contents
---------------

.. py:class:: LCLGridVcCtr(solver, Np, lambda_u, I_conv_max, disc_method='exact_discretization')

   Bases: :py:obj:`soft4pes.control.mpc.common.mpc_base.MPCBase`, :py:obj:`soft4pes.control.common.controller.Controller`


   
   MPC for filter capacitor voltage tracking in LCL-filtered grid-connected systems.

   The controller tracks only the filter capacitor voltage reference in the alpha-beta frame.
   Moreover, converter current limits have been included as soft constraints in the MPC problem.

   The soft constraints are penalized in the cost function with a weight of 10e6, which ensures
   that the converter current limits are respected.

   :param solver: Solver for an MPC algorithm.
   :type solver: solver object
   :param Np: Prediction horizon steps.
   :type Np: int
   :param lambda_u: Weighting factor for the control effort.
   :type lambda_u: float
   :param I_conv_max: Maximum converter current [p.u.].
   :type I_conv_max: float
   :param disc_method: Discretization method for the state-space model ('forward_euler' or
                       'exact_discretization'). Default is 'exact_discretization'.
   :type disc_method: str, optional















   ..
       !! processed by numpydoc !!

   .. py:method:: execute(sys, kTs)

      
      Execute one control step of the MPC algorithm.

      Transforms the capacitor voltage reference from dq to alpha-beta frame, predicts grid
      voltage disturbance over the horizon, and solves the MPC optimization problem with soft
      constraints to obtain the optimal control action.

      :param sys: System model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Output namespace with field `u_abc` containing the converter three-phase switch
                position or modulating signal.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


