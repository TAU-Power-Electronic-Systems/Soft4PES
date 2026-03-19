soft4pes.control.lin.lcl_grid_curr_ctr_wacfb
============================================

.. py:module:: soft4pes.control.lin.lcl_grid_curr_ctr_wacfb

.. autoapi-nested-parse::

   Grid current controller for a converter with LCL filter based on weighted average control
    (WAC) feedback.

   [Ref.]. L. S. Perić, E. Levi and S. N. Vukosavić, "Compound Feedback for Current-Controlled
    Grid-Side Inverters With LCL Filters," in IEEE Transactions on Power Electronics, vol. 40,
      no. 2, pp. 3005-3019, Feb. 2025, doi: 10.1109/TPEL.2024.3487109.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.lcl_grid_curr_ctr_wacfb.LCLGridCurrCtrWACFB


Module Contents
---------------

.. py:class:: LCLGridCurrCtrWACFB(sys, gamma=None, xi=None, alpha_d=0.3)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Grid current controller for a converter with LCL filter based on weighted average based (WAC)
   feedback.

   :param sys: System model containing electrical parameters and base values.
   :type sys: object

   .. attribute:: sys

      System model containing electrical parameters and base values.

      :type: object

   .. attribute:: gamma

      Tuning parameter for the high-pass filter (HPF) in the damping compensation path.

      :type: float

   .. attribute:: xi

      Damping ratio for the damping compensation path.

      :type: float

   .. attribute:: alpha_d

      Tuning parameter for the integrator gain in the main control path.

      :type: float

   .. attribute:: ctr

      Controller parameters and filters.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: set_sampling_interval(Ts)

      
      Set the sampling interval and compute controller parameters.

      :param Ts: Sampling interval in seconds.
      :type Ts: float















      ..
          !! processed by numpydoc !!


   .. py:method:: execute(sys, kTs)

      
      Execute the controller.

      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **output** -- The output of the controller after execution.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


