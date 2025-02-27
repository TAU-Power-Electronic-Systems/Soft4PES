soft4pes.control.mpc.solvers.mpc_QP
===================================

.. py:module:: soft4pes.control.mpc.solvers.mpc_QP

.. autoapi-nested-parse::

   This module contains the class MpcQP, which is used to solve the MPC problem using a quadratic
   program (QP) solver.

   The formulation of the control problem and the QP matrices are based on "M. Rossi, P. Karamanakos,
   and F. Castelli-Dezza, “An indirect model predictive control method for grid-connected three-level
   neutral point clamped converters with LCL filters,” IEEE Trans. Ind. Applicat., vol. 58, no. 3, pp.
   3750-3768, May/Jun. 2022". Note, that contrary to the reference, the grid voltage is modelled as a
   disturbance. Moreover, the same states do not have to be both controlled (i.e., be output variables)
   and constrained.

   The QP is solved using the qpsolvers package and the solver 'DAQP', licensed under the MIT
   license.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.mpc.solvers.mpc_QP.IndirectMpcQP


Module Contents
---------------

.. py:class:: IndirectMpcQP

   
   Problem formulation and QP solver for indirect MPC.

   .. attribute:: QP_matrices

      Namespace containing the matrices used in the QP problem.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: __call__(sys, conv, ctr, y_ref)

      
      Formulate and solve the MPC QP.

      :param sys: System model.
      :type sys: system object
      :param conv: Converter model.
      :type conv: converter object
      :param ctr: Controller object.
      :type ctr: controller object
      :param y_ref: Reference vector [p.u.].
      :type y_ref: ndarray of floats

      :returns: **uk_abc** -- The three-phase modulating signal.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


