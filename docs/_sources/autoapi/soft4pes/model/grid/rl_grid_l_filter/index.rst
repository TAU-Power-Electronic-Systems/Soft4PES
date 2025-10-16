soft4pes.model.grid.rl_grid_l_filter
====================================

.. py:module:: soft4pes.model.grid.rl_grid_l_filter

.. autoapi-nested-parse::

   Model of a grid with stiff voltage source, RL impedance and an L filter in alpha-beta frame.

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.rl_grid_l_filter.RLGridLFilter


Module Contents
---------------

.. py:class:: RLGridLFilter(par_grid, par_l_filter, conv, base, ig_ref_init=None)

   Bases: :py:obj:`soft4pes.model.grid.rl_grid.RLGrid`


   
   Model of a grid with stiff voltage source, RL impedance and an L filter in alpha-beta frame.

   The state of the system is the converter current (or the grid current) in
   the alpha-beta frame, i.e. x = [i_conv^T]^T or x = [ig^T]^T. The system input is the converter
   three-phase switch position or modulating signal. The grid voltage is considered to be a
   disturbance. The positive current direction is from the converter to the grid for i_conv
   and ig, respectively. Knowledge of the grid impedance is required,
   and given to the model in the parent class RLGrid.

   :param par_grid: Parameters of the grid.
   :type par_grid: RLGridParameters
   :param par_l_filter: Parameters of the L-filter.
   :type par_l_filter: LFilterParameters
   :param conv: Converter object.
   :type conv: converter object
   :param base: Base values.
   :type base: base value object

   .. attribute:: data

      Namespace for storing simulation data.

      :type: SimpleNamespace

   .. attribute:: par

      Combined RLGridParameters and L-FilterParameters.

      :type: System parameters

   .. attribute:: conv

      Converter object.

      :type: converter object

   .. attribute:: x

      Current state of the grid [p.u.].

      :type: 1 x 2 ndarray of floats

   .. attribute:: base

      Base values.

      :type: base value object

   .. attribute:: cont_state_space

      The continuous-time state-space model of the system.

      :type: SimpleNamespace

   .. attribute:: state_map

      A dictionary mapping states to elements of the state vector.

      :type: dict















   ..
       !! processed by numpydoc !!

   .. py:method:: get_continuous_state_space()

      
      Get the continuous-time state-space model of the system in alpha-beta frame.

      :returns: A SimpleNamespace object containing matrices F, G1 and G2 of the continuous-time
                state-space model.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


