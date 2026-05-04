soft4pes.control.lin.pll
========================

.. py:module:: soft4pes.control.lin.pll

.. autoapi-nested-parse::

   Phase-locked loop (PLL)

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.lin.pll.PLL


Module Contents
---------------

.. py:class:: PLL(sys, zeta=np.sqrt(2) / 2, wn=2 * np.pi * 20)

   Bases: :py:obj:`soft4pes.control.common.controller.Controller`


   
   Phase-locked loop (PLL) implementation.
















   ..
       !! processed by numpydoc !!

   .. py:method:: set_sampling_interval(Ts)

      
      Set the sampling interval and compute controller parameters.

      :param Ts: Sampling interval [s].
      :type Ts: float















      ..
          !! processed by numpydoc !!


   .. py:method:: execute(sys, kTs)

      
      Execute the PLL control algorithm to estimate the grid voltage angle.
      :param sys: System model.
      :type sys: object
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: **output** -- The output of the PLL, containing the estimated grid voltage angle (theta) and
                the active and reactive power references.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


