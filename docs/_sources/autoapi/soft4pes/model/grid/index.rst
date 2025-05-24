soft4pes.model.grid
===================

.. py:module:: soft4pes.model.grid

.. autoapi-nested-parse::

   
   Grid models.
















   ..
       !! processed by numpydoc !!


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/soft4pes/model/grid/base_grid/index
   /autoapi/soft4pes/model/grid/lcl_filter_param/index
   /autoapi/soft4pes/model/grid/rl_grid/index
   /autoapi/soft4pes/model/grid/rl_grid_lcl_filter/index
   /autoapi/soft4pes/model/grid/rl_grid_param/index


Classes
-------

.. autoapisummary::

   soft4pes.model.grid.BaseGrid
   soft4pes.model.grid.LCLFilterParameters
   soft4pes.model.grid.RLGridLCLFilter
   soft4pes.model.grid.RLGrid
   soft4pes.model.grid.RLGridParameters


Package Contents
----------------

.. py:class:: BaseGrid(Vg_R_SI, Ig_R_SI, fg_R_SI)

   
   Base values for a grid.

   The class computes the base values for a grid based on the rated values.

   :param Vg_R_SI: Rated voltage [V] (line-to-line rms voltage).
   :type Vg_R_SI: float
   :param Ig_R_SI: Rated current [A] (line rms current).
   :type Ig_R_SI: float
   :param fg_R_SI: Rated frequency [Hz].
   :type fg_R_SI: float

   .. attribute:: V

      Base voltage [V].

      :type: float

   .. attribute:: I

      Base current [A].

      :type: float

   .. attribute:: w

      Base angular frequency [rad/s].

      :type: float

   .. attribute:: S

      Base apparent power [VA].

      :type: float

   .. attribute:: Z

      Base impedance [Ohm].

      :type: float

   .. attribute:: L

      Base inductance [H].

      :type: float

   .. attribute:: C

      Base capacitance [F].

      :type: float















   ..
       !! processed by numpydoc !!

.. py:class:: LCLFilterParameters(L_fc_SI, C_SI, base, L_fg_SI=0, R_fc_SI=0, R_c_SI=0, R_fg_SI=0)

   
   Parameters for an LCL-filter.

   :param L_fc_SI: Inductance of the converter side filter inductor [H].
   :type L_fc_SI: float
   :param C_SI: Capacitance of the filter capacitor [F].
   :type C_SI: float
   :param base: Base values.
   :type base: base value object
   :param L_fg_SI: Inductance of the grid side filter inductor [H].
   :type L_fg_SI: float, optional
   :param R_fc_SI: Resistance of the converter side filter inductor [Ohm].
   :type R_fc_SI: float, optional
   :param R_c_SI: Resistance of the filter capacitor [Ohm].
   :type R_c_SI: float, optional
   :param R_fg_SI: Resistance of the grid side filter inductor [Ohm].
   :type R_fg_SI: float, optional

   .. attribute:: X_fc

      Reactance of the converter side filter inductor [p.u.].

      :type: float

   .. attribute:: R_fc

      Resistance of the converter side filter inductor [p.u.].

      :type: float

   .. attribute:: Xc

      Reactance of the filter capacitor [p.u.].

      :type: float

   .. attribute:: Rc

      Resistance of the filter capacitor [p.u.].

      :type: float

   .. attribute:: X_fg

      Reactance of the grid side filter inductor [p.u.].

      :type: float

   .. attribute:: R_fg

      Resistance of the grid side filter inductor [p.u.].

      :type: float

   .. attribute:: base

      :type: base value object















   ..
       !! processed by numpydoc !!

.. py:class:: RLGridLCLFilter(par_grid, par_lcl_filter, conv, base)

   Bases: :py:obj:`soft4pes.model.grid.rl_grid.RLGrid`


   
   Model of a grid with stiff voltage source, RL impedance and an LC(L) filter in alpha-beta frame.
   If the grid side inductance is not provided, the filter is in LC configuration.

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

   .. attribute:: state_map

      A dictionary mapping states to elements of the state vector.

      :type: dict















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


.. py:class:: RLGrid(par, conv, base, ig_ref_init=None)

   Bases: :py:obj:`soft4pes.model.common.system_model.SystemModel`


   
   Model of a grid with a voltage source and an RL impedance in alpha-beta frame. The state of the
   system is the grid current (same as the converter current). The system input is the converter
   three-phase switch position or modulating signal. The grid voltage is considered to be a
   disturbance and the magnitude of the grid voltage is configurable as a function of time using a
   Sequence object.

   This class can be used as a base class for other grid models.

   :param par: Grid parameters in p.u.
   :type par: RLGridParameters
   :param conv: Converter object.
   :type conv: converter object
   :param base: Base values.
   :type base: base value object
   :param ig_ref_init: Reference at discrete time instant kTs = 0 for starting simulation from steady state.
   :type ig_ref_init: 1 x 2 ndarray of floats, optional

   .. attribute:: data

      Namespace for storing simulation data.

      :type: SimpleNamespace

   .. attribute:: par

      Grid parameters in p.u.

      :type: RLGridParameters

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

   .. py:method:: set_initial_state(**kwargs)

      
      Set the initial state of the system based on the grid current reference, if provided.

      :param ig_ref_init: Reference at discrete time instant kTs = 0 for starting simulation from steady state.
      :type ig_ref_init: 1 x 2 ndarray of floats, optional















      ..
          !! processed by numpydoc !!


   .. py:method:: get_continuous_state_space()

      
      Calculate the continuous-time state-space model of the system.

      :returns: A SimpleNamespace object containing matrices F, G1 and G2 of the continuous-time
                state-space model.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


   .. py:method:: get_grid_voltage(kTs)

      
      Get the grid voltage at a specific discrete time instant.

      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: Grid voltage in alpha-beta frame [p.u.].
      :rtype: 1 x 2 ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_next_state(matrices, u_abc, kTs)

      
      Calculate the next state of the system.

      :param u_abc: Converter three-phase switch position or modulating signal.
      :type u_abc: 1 x 3 ndarray of floats
      :param matrices: A SimpleNamespace object containing the state-space model matrices.
      :type matrices: SimpleNamespace
      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: The next state of the system.
      :rtype: ndarray of floats















      ..
          !! processed by numpydoc !!


   .. py:method:: get_measurements(kTs)

      
      Update the measurement data of the system.

      :param kTs: Current discrete time instant [s].
      :type kTs: float

      :returns: A SimpleNamespace object containing the grid voltage in alpha-beta frame.
      :rtype: SimpleNamespace















      ..
          !! processed by numpydoc !!


.. py:class:: RLGridParameters(Vg_SI, fg_SI, Rg_SI, Lg_SI, base)

   
   Parameters for a grid with a voltage source and an RL impedance. The grid voltage can be given
   as a constant or as a function of time using a Sequence object.

   :param Vg_SI: Grid voltage [V] (line-to-line rms voltage).
   :type Vg_SI: float or Sequence
   :param fg_SI: Grid frequency [Hz].
   :type fg_SI: float
   :param Rg_SI: Resistance [Ohm].
   :type Rg_SI: float
   :param Lg_SI: Inductance [H].
   :type Lg_SI: float
   :param base: Base values.
   :type base: base value object

   .. attribute:: Vg

      Grid voltage [p.u.] (line-to-line rms voltage).

      :type: float or Sequence

   .. attribute:: wg

      Angular frequency [p.u.].

      :type: float

   .. attribute:: Rg

      Resistance [p.u.].

      :type: float

   .. attribute:: Xg

      Reactance [p.u.].

      :type: float















   ..
       !! processed by numpydoc !!

