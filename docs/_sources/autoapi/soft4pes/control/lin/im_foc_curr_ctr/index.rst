soft4pes.control.lin.im_foc_curr_ctr
====================================

.. py:module:: soft4pes.control.lin.im_foc_curr_ctr

.. autoapi-nested-parse::

   Field-oriented control (FOC) for the current control of an induction machine (IM).

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.im_foc_curr_ctr.FOCCurrCtr


Module Contents
---------------

.. py:class:: FOCCurrCtr(sys)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Field-oriented control (FOC) for the current control of a induction machine (IM).

   :param sys: System model.
   :type sys: object

   .. attribute:: iS_ii_dq

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

      Magnitude optimum criterion based on:
      J. W. Umland and M. Safiuddin,
      "Magnitude and symmetric optimum criterion for the design
      of linear control systems: what is it and how does it compare with the others?,"
      in IEEE Transactions on Industry Applications, vol. 26, no. 3,
      pp. 489-497, May-June 1990, doi: 10.1109/28.55967

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


