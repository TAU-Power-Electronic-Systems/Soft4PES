soft4pes.control.mpc.common.mpc_base
====================================

.. py:module:: soft4pes.control.mpc.common.mpc_base

.. autoapi-nested-parse::

   This module defines the MPCBase class, which serves as a base class for model predictive
   controllers (MPC). It stores common parameters and provides utility functions for creating reference
   and disturbance vectors over the prediction horizon.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.common.mpc_base.MPCBase


Functions
---------

.. autoapisummary::

   soft4pes.control.mpc.common.mpc_base.has_soft_constraints


Module Contents
---------------

.. py:function:: has_soft_constraints(C_soft_constr, soft_constr_weights, soft_constraints_max)

   
   Check if soft constraints are enabled by verifying that all soft constraint parameters are
   provided.

   :param C_soft_constr: Output matrix for the constrained variables (used for soft constraints).
   :type C_soft_constr: ndarray or None
   :param soft_constr_weights: Weighting matrix in the objective function for the soft constraints.
   :type soft_constr_weights: ndarray or None
   :param soft_constraints_max: Maximum values for constrained variables.
   :type soft_constraints_max: ndarray or None

   :returns: True if soft constraints are enabled, False otherwise.
   :rtype: bool

   :raises ValueError: If only a subset of soft constraint parameters is provided.















   ..
       !! processed by numpydoc !!

.. py:class:: MPCBase(C, Q, Np, lambda_u, solver, C_soft_constr=None, soft_constr_weights=None, soft_constraints_max=None, disc_method='exact_discretization')

   
   Base class for MPC controllers.

   :param C: Output matrix. Defines the tracked variables.
   :type C: ndarray
   :param Q: Weighting matrix in the objective function for the tracked variables.
   :type Q: ndarray
   :param Np: Prediction horizon steps.
   :type Np: int
   :param lambda_u: Weighting factor for the control effort.
   :type lambda_u: float
   :param solver: Solver for MPC.
   :type solver: solver object
   :param disc_method: Discretization method for the state-space model.
   :type disc_method: str
   :param C_soft_constr: Output matrix for the constrained variables (used for soft constraints).
   :type C_soft_constr: ndarray, optional
   :param soft_constr_weights: Weighting matrix in the objective function for the soft constraints.
   :type soft_constr_weights: ndarray, optional
   :param soft_constraints_max: Maximum values for constrained variables.
   :type soft_constraints_max: ndarray, optional

   .. attribute:: C

      Output matrix. Defines the tracked variables.

      :type: ndarray

   .. attribute:: Q

      Weighting matrix in the objective function for the tracked variables.

      :type: ndarray

   .. attribute:: Np

      Prediction horizon steps.

      :type: int

   .. attribute:: lambda_u

      Weighting factor for the control effort.

      :type: float

   .. attribute:: solver

      Solver for MPC.

      :type: solver object

   .. attribute:: disc_method

      Discretization method for the state-space model.

      :type: str

   .. attribute:: state_space

      The state-space model of the system.

      :type: SimpleNamespace

   .. attribute:: u_km1_abc

      Previous (step k-1) three-phase switch position or modulating signal.

      :type: 1 x 3 ndarray of floats

   .. attribute:: C_soft_constr

      Output matrix for the constrained variables (used for soft constraints).

      :type: ndarray

   .. attribute:: soft_constr_weights

      Weighting matrix in the objective function for the soft constraints.

      :type: ndarray

   .. attribute:: soft_constraints_max

      Maximum values for constrained variables.

      :type: ndarray

   .. attribute:: has_soft_constraints

      Flag indicating whether soft constraints are enabled.

      :type: bool















   ..
       !! processed by numpydoc !!

   .. py:method:: get_ctr_state_space(sys, Ts)

      
      Get the discrete-time state-space model. If the system has a time-varying model, the state-
      space model is updated at each time step.

      :param sys: System model.
      :type sys: system object
      :param Ts: Sampling interval [s].
      :type Ts: float















      ..
          !! processed by numpydoc !!


   .. py:method:: make_horizon_vector(w, Ts, vector_in, start_step=1)

      
      Predict the future values of a vector over the prediction horizon by rotating the input
      vector. The rotation is applied to each variable in alpha-beta frame in the input vector,
      and the result is a vector extended over the prediction horizon.

      The start step determines the prediction time steps. For start_step=1, predictions are for
      k+1 to k+Np, which is typically used for reference trajectories. For start_step=0,
      predictions are for k to k+Np-1, which is typically used for disturbances.

      Example: vector_in = [vc_ref^T(k), ig_ref^T(k)]^T, Np = 3, start_step = 1, then the output
      will be [vc_ref^T(k+1), ig_ref^T(k+1), vc_ref^T(k+2), ig_ref^T(k+2), vc_ref^T(k+3),
      ig_ref^T(k+3)]^T.

      :param w: Angular frequency [rad/s].
      :type w: float
      :param Ts: Sampling interval [s].
      :type Ts: float
      :param vector_in: Input vector with variables in alpha-beta frame at current time step.
      :type vector_in: n x 1 ndarray
      :param start_step: Starting rotation step (default=1 for references k+1...k+Np,
                         use 0 for disturbances k...k+Np-1).
      :type start_step: int, optional

      :returns: **horizon_vector** -- Vector extended over the prediction horizon with rotations applied.
      :rtype: Np*n x 1 ndarray















      ..
          !! processed by numpydoc !!


   .. py:method:: make_reference_vector(w, Ts, ref)

      
      Create the reference vector for the prediction horizon (k+1 to k+Np).

      :param w: Angular frequency [rad/s].
      :type w: float
      :param Ts: Sampling interval [s].
      :type Ts: float
      :param ref: Reference values for the controlled outputs at the current time step.
      :type ref: n x 1 ndarray

      :returns: **ref_vector** -- Reference vector for the prediction horizon.
      :rtype: Np*n x 1 ndarray















      ..
          !! processed by numpydoc !!


   .. py:method:: make_disturbance_vector(w, Ts, d)

      
      Create the disturbance vector for the prediction horizon (k to k+Np-1).

      :param w: Angular frequency [rad/s].
      :type w: float
      :param Ts: Sampling interval [s].
      :type Ts: float
      :param d: Disturbance values at the current time step.
      :type d: n x 1 ndarray

      :returns: **dist_vector** -- Disturbance vector for the prediction horizon.
      :rtype: Np*n x 1 ndarray















      ..
          !! processed by numpydoc !!


