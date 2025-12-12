soft4pes.control.lin.l_conv_curr_ctr
====================================

.. py:module:: soft4pes.control.lin.l_conv_curr_ctr

.. autoapi-nested-parse::

   Current Controller (CC) for the control of the converter (or grid) current with L filter.
   Based on the following reference:
   E. Pouresmaeil, C. Miguel-Espinar, M. Massot-Campos, D. Montesinos-Miracle and O. Gomis-Bellmunt,
   "A Control Technique for Integration of DG Units to the Electrical Networks," in IEEE Transactions
   on Industrial Electronics, vol. 60, no. 7, pp. 2881-2893, July 2013, doi: 10.1109/TIE.2012.2209616.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.l_conv_curr_ctr.LConvCurrCtr


Module Contents
---------------

.. py:class:: LConvCurrCtr(sys)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Current Controller for converter (or grid) current with an L filter.

   :param sys: System model.
   :type sys: object

   .. attribute:: i_conv_ii_dq

      Integrator state of the PI-controller.

      :type: ndarray (2,)

   .. attribute:: sys

      System model.

      :type: object

   .. attribute:: ctr_pars

      Controller parameters.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: set_sampling_interval(Ts)

      
      Set the sampling interval and compute controller parameters.

      :param Ts: Sampling interval [s].
      :type Ts: float















      ..
          !! processed by numpydoc !!


   .. py:method:: execute(sys, kTs)

      
      Execute the Current Controller (CC) and save the controller data.

      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Three-phase modulating signal.
      :rtype: 1 x 3 ndarray of floats















      ..
          !! processed by numpydoc !!


