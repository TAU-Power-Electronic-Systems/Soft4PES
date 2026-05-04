soft4pes.control.mpc.algorithms.im_curr_ctr
===========================================

.. py:module:: soft4pes.control.mpc.algorithms.im_curr_ctr

.. autoapi-nested-parse::

   Model predictive control (MPC) for induction machine (IM) stator current control.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.algorithms.im_curr_ctr.IMCurrCtr


Module Contents
---------------

.. py:class:: IMCurrCtr(solver, Np, lambda_u, disc_method='forward_euler')

   Bases: :py:obj:`soft4pes.control.mpc.common.mpc_base.MPCBase`, :py:obj:`soft4pes.control.common.controller.Controller`


   
   MPC for induction machine stator current control.

   The controller tracks the stator current in the alpha-beta frame. The current reference
   is calculated based on the torque reference and rotor flux magnitude.

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

      Calculates the stator current reference from the torque reference, predicts it over
      the horizon, and solves the MPC optimization problem to obtain the optimal control action.

      :param sys: System model.
      :type sys: system object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Output namespace with field `u_abc` containing the three-phase switch position or
                modulating signal.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


