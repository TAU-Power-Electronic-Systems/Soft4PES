soft4pes.model.grid.rl_grid_lcl_filter
======================================

.. py:module:: soft4pes.model.grid.rl_grid_lcl_filter

.. autoapi-nested-parse::

   Model of a grid with stiff voltage source, RL-load and an LC(L) filter in alpha-beta frame.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.rl_grid_lcl_filter.RLGridLCLFilter


Module Contents
---------------

.. py:class:: RLGridLCLFilter(par_grid, par_lcl_filter, conv, base)

   Bases: :py:obj:`soft4pes.model.grid.rl_grid.RLGrid`


   
   Model of a grid with stiff voltage source, RL-load and an LC(L) filter in alpha-beta frame. If
   the grid side inductance is not provided, the filter is in LC configuration.

   The state of the system is the converter current, the capacitor voltage and the grid current in
   the alpha-beta frame, i.e. x = [i_conv^T, ig^T, vc^T]^T. The system input is the converter
   three-phase switch position or modulating signal. The grid voltage is considered to be a
   disturbance. The positive current direction is from the converter to the filter and from the
   filter to the grid for i_conv and ig, respectively. Knowledge of the grid impedance is required,
   and given to the model in the parent class RLGrid.

   :param par_grid: Parameters of the grid.
   :type par_grid: RLGridParameters
   :param par_lcl_filter: Parameters of the LCL filter.
   :type par_lcl_filter: LCLFilterParameters
   :param conv: Converter object.
   :type conv: converter object
   :param base: Base values.
   :type base: base value object

   .. attribute:: data

      Namespace for storing simulation data.

      :type: SimpleNamespace

   .. attribute:: par

      Combined RLGridParameters and LCLFilterParameters.

      :type: System parameters

   .. attribute:: conv

      Converter object.

      :type: converter object

   .. attribute:: x

      Current state of the grid [p.u.].

      :type: 1 x 6 ndarray of floats

   .. attribute:: base

      Base values.

      :type: base value object

   .. attribute:: cont_state_space

      The continuous-time state-space model of the system.

      :type: SimpleNamespace















   ..
       !! processed by numpydoc !!

   .. py:method:: set_initial_state(**kwargs)

      
      Set the initial state of the system to zero.
















      ..
          !! processed by numpydoc !!


   .. py:method:: get_continuous_state_space()

      
      Get the continuous-time state-space model of the system in alpha-beta frame.

      :returns: A SimpleNamespace object containing matrices F, G1 and G2 of the continuous-time
                state-space model.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


