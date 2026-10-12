soft4pes.control.modulation.opp_computation
===========================================

.. py:module:: soft4pes.control.modulation.opp_computation

.. autoapi-nested-parse::

   Offline optimized pulse pattern (OPP) computation.

   Supported features
   ------------------
   - Two-level and three-level converters
   - QaHWS and HWS pulse patterns
   - Machine- or grid-connected converters

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   soft4pes.control.modulation.opp_computation.OPPComputation


Functions
---------

.. autoapisummary::

   soft4pes.control.modulation.opp_computation.init_worker
   soft4pes.control.modulation.opp_computation.objective_function
   soft4pes.control.modulation.opp_computation.objective_gradient
   soft4pes.control.modulation.opp_computation.nonlinear_constraint_function
   soft4pes.control.modulation.opp_computation.nonlinear_constraint_jacobian
   soft4pes.control.modulation.opp_computation.run_single_optimization


Module Contents
---------------

.. py:function:: init_worker(worker_data)

   
   Initialize worker-local data.

   Large arrays are stored once per worker process to reduce inter-process
   communication overhead.

   :param worker_data: Data shared by all optimization tasks executed by each worker.
   :type worker_data: dict















   ..
       !! processed by numpydoc !!

.. py:function:: objective_function(x)

   
   Evaluate the OPP objective function.

   :param x: Vector of switching angles.
   :type x: ndarray

   :returns: Value of the OPP objective function.
   :rtype: float















   ..
       !! processed by numpydoc !!

.. py:function:: objective_gradient(x)

   
   Evaluate the gradient of the objective function.

   :param x: Vector of switching angles.
   :type x: ndarray

   :returns: Gradient of the objective function with respect to the switching angles.
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: nonlinear_constraint_function(x, modulation_index, u0)

   
   Evaluate the OPP equality constraints.

   :param x: Vector of switching angles.
   :type x: ndarray
   :param modulation_index: Desired modulation index.
   :type modulation_index: float
   :param u0: Initial switch position.
   :type u0: int

   :returns: Values of equality constraints.
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: nonlinear_constraint_jacobian(x, u0)

   
   Evaluate the Jacobian of the equality constraints.

   :param x: Vector of switching angles.
   :type x: ndarray
   :param u0: Initial switch position.
   :type u0: int

   :returns: Jacobian of the equality constraints with respect to the switching angles.
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: run_single_optimization(task)

   
   Run a local SLSQP optimization from a single initial point.

   :param task: Tuple containing the initial vector of switching angles, modulation index,
                and initial switch position.
   :type task: tuple

   :returns: Optimization result returned by scipy.optimize.minimize.
   :rtype: OptimizeResult















   ..
       !! processed by numpydoc !!

.. py:class:: OPPComputation(sys, d=5, symmetry='QaHWS', n_m=256, n_ini_points=1000, max_harmonics=500, modulation_indices=None)

   
   Offline OPP computation.

   :param sys: System model.
   :type sys: SystemModel
   :param d: Base number of switching transitions used to construct the OPP.
             For example, this corresponds to the pulse number for three-level
             QaHWS OPPs.
   :type d: int, default=5
   :param symmetry: Waveform symmetry.















   ..
       !! processed by numpydoc !!

   .. py:method:: build_problem()

      
      Build all quantities required for OPP computation.
















      ..
          !! processed by numpydoc !!


   .. py:method:: build_harmonics()

      
      Build the set of considered non-triplen odd harmonic orders.
















      ..
          !! processed by numpydoc !!


   .. py:method:: build_switching_sequence()

      
      Build switching-angle and switching-sequence information.
















      ..
          !! processed by numpydoc !!


   .. py:method:: build_system_model()

      
      Build harmonic weighting factors used in the objective function.

      For systems with an LCL filter, the weighting factors are based on the
      gain of the transfer function from the switch position to the output
      current. All other currently supported systems use 1/n weighting
      factors.















      ..
          !! processed by numpydoc !!


   .. py:method:: build_constraints()

      
      Build bound and ordering constraints for the switching angles.
















      ..
          !! processed by numpydoc !!


   .. py:method:: build_initial_points()

      
      Generate Halton initial points for multistart optimization.
















      ..
          !! processed by numpydoc !!


   .. py:method:: get_worker_data()

      
      Collect data required by multiprocessing workers.

      :returns: Data shared with worker processes.
      :rtype: dict















      ..
          !! processed by numpydoc !!


   .. py:method:: compute(use_parallel=True)

      
      Compute OPPs.

      :param use_parallel: If True, the multistart initial points are solved in parallel.
      :type use_parallel: bool, default=True

      :returns: Computed OPP lookup-table data, including switching angles,
                modulation indices, and switch positions.
      :rtype: dict















      ..
          !! processed by numpydoc !!


   .. py:method:: compute_loop(results, pool)

      
      Main loop over modulation indices and switching sequences.

      :param results: Dictionary used to store computed OPP data.
      :type results: dict
      :param pool: Worker pool used for parallel execution.
      :type pool: multiprocessing.Pool or None















      ..
          !! processed by numpydoc !!


   .. py:method:: save_results(filename=None)

      
      Save computed OPPs to a NetCDF file.

      :param filename: Output file name.
                       If None, a file name is generated from the OPP configuration.
      :type filename: str, optional















      ..
          !! processed by numpydoc !!


