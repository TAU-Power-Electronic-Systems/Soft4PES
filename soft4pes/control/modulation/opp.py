"""
Offline optimal pulse pattern (OPP) computation.

Supported features
------------------
- Two-level and three-level converters
- QaHWS and HWS pulse patterns
- Load-connected and grid-connected converters
"""

from datetime import datetime
import multiprocessing as mp
from types import SimpleNamespace

import control as ct
import numpy as np
import xarray as xr
from scipy.optimize import Bounds, LinearConstraint, minimize
from scipy.stats import qmc

# Data shared by worker processes.
_WORKER_DATA = None


def init_worker(worker_data):
    """
    Initialize worker-local data.

    Large arrays are stored once per worker process to reduce inter-process
    communication overhead.

    Parameters
    ----------
    worker_data : dict
        Data shared by all optimization tasks executed by the worker.
    """

    global _WORKER_DATA
    _WORKER_DATA = worker_data


def objective_function(x):
    """
    Evaluate the OPP objective function.

    Parameters
    ----------
    x : ndarray
        Switching-angle vector.

    Returns
    -------
    float
        Objective-function value.
    """

    data = _WORKER_DATA

    x = np.asarray(x)

    harmonic_orders = data["harmonic_orders"]
    delta_u = data["delta_u"]
    harmonic_weights = data["harmonic_weights"]

    converter_level = data["level"]
    is_grid = data["is_grid"]
    symmetry = data["symmetry"]

    cost = 0

    for harmonic_index, harmonic_order in enumerate(harmonic_orders):
        harmonic_weight = harmonic_weights[harmonic_index]

        if symmetry == "HWS":
            coeff_cos = np.dot(delta_u, np.cos(harmonic_order * x))
            coeff_sin = np.dot(delta_u, np.sin(harmonic_order * x))

            if is_grid:
                cost += (
                    (harmonic_weight / harmonic_order) ** 2
                ) * (coeff_cos ** 2 + coeff_sin ** 2)
            else:
                cost += (
                    (harmonic_weight / (harmonic_order ** 2)) ** 2
                ) * (coeff_cos ** 2 + coeff_sin ** 2)

        else:

            if converter_level == 2:
                harmonic_coeff = 1 + 2 * np.dot(delta_u, np.cos(harmonic_order * x))
            else:
                harmonic_coeff = np.dot(delta_u, np.cos(harmonic_order * x))

            if is_grid:
                cost += (
                    (harmonic_weight * harmonic_coeff)
                    / harmonic_order
                ) ** 2
            else:
                cost += (
                    (harmonic_weight * harmonic_coeff)
                    / (harmonic_order ** 2)
                ) ** 2

    return cost


def nonlinear_constraint_function(x, modulation_index, u0):
    """
    Evaluate the OPP equality constraints.

    Parameters
    ----------
    x : ndarray
        Switching-angle vector.

    modulation_index : float
        Desired modulation index.

    u0 : int
        Initial switching state.

    Returns
    -------
    ndarray
        Equality-constraint values.
    """

    data = _WORKER_DATA

    x = np.asarray(x)

    delta_u = data["delta_u"]
    converter_level = data["level"]
    symmetry = data["symmetry"]

    if symmetry == "HWS":
        coeff_cos = np.dot(delta_u, np.cos(x))
        coeff_sin = np.dot(delta_u, np.sin(x))

        if converter_level == 2:
            ceq1 = (u0 * 4 / np.pi) * coeff_cos - modulation_index
            ceq2 = -(u0 * 4 / np.pi) * coeff_sin
        else:
            ceq1 = (2 / np.pi) * coeff_cos - modulation_index
            ceq2 = -(2 / np.pi) * coeff_sin

        return np.array([ceq1, ceq2])

    if converter_level == 2:
        ceq = (u0 * 4 / np.pi) * (1 + 2 * np.dot(delta_u, np.cos(x))) - modulation_index
    else:
        ceq = (4 / np.pi) * np.dot(delta_u, np.cos(x)) - modulation_index

    return np.array([ceq])


def run_single_optimization(task):
    """
    Run a local SLSQP optimization from a single initial point.

    Parameters
    ----------
    task : tuple
        Tuple containing the initial switching-angle vector, modulation index,
        and switching-sequence-specific data.

    Returns
    -------
    OptimizeResult
        Optimization result returned by scipy.optimize.minimize.
    """

    x0, modulation_index, u0 = task

    data = _WORKER_DATA

    nonlinear_constraint = {
        "type": "eq",
        "fun": lambda x: nonlinear_constraint_function(
            x,
            modulation_index,
            u0,
        )
    }

    result = minimize(
        objective_function,
        x0,
        method="SLSQP",
        bounds=data["bounds"],
        constraints=[
            nonlinear_constraint,
            data["linear_constraint"],
        ],
        options={
            "maxiter": 1000,
            "ftol": 1e-12,
            "disp": False,
        },
    )

    return result


class OPP:
    """
    Offline OPP computation.
    
    Parameters
    ----------
    sys : SystemModel
        System model.

    d : int, default=5
        Pulse number.

    symmetry : str, default="QaHWS"
        Waveform symmetry.

        Options
        -------
        - "HWS": half-wave symmetry
        - "QaHWS": quarter- and half-wave symmetry

    n_m : int, default=256
        Number of modulation-index samples.

    n_ini_points : int, default=1000
        Number of multistart initial points.

    max_harmonics : int, default=500
        Maximum harmonic order included in the objective function.

    Attributes
    ----------
    results : dict
        Computed OPP lookup table.
    """

    def __init__(
        self,
        sys,
        d=5,
        symmetry="QaHWS",
        n_m=256,
        n_ini_points=1000,
        max_harmonics=500,
    ):

        self.sys = sys
        self.d = d
        self.level = sys.conv.nl

        if symmetry not in ("HWS", "QaHWS"):
            raise ValueError("symmetry must be either 'QaHWS' or 'HWS'.")
        self.symmetry = symmetry

        self.is_grid = hasattr(sys, "cont_state_space")
        self.n_m = n_m
        self.n_ini_points = n_ini_points
        self.max_harmonics = max_harmonics

        self.harmonic_orders = None
        self.n_angles = None
        self.n_sequences = None
        self.u0_candidates = None
        self.delta_u = None
        self.harmonic_weights = None
        self.x0_set = None
        self.results = None
        self.constraints = SimpleNamespace(
            angle_max=None,
            bounds=None,
            linear_constraint=None,
        )

        self.build_problem()

    # Problem setup

    def build_problem(self):
        """
        Build all quantities required for OPP computation.
        """

        self.build_harmonics()
        self.build_switching_sequence()
        self.build_system_model()
        self.build_constraints()
        self.build_initial_points()

    def build_harmonics(self):
        """
        Build the set of considered non-triplen odd harmonic orders.
        """

        harmonics = np.arange(2, self.max_harmonics + 1)

        self.harmonic_orders = harmonics[
            (harmonics % 2 == 1) &
            (harmonics % 3 != 0)
        ]

    def build_switching_sequence(self):
        """
        Build switching-angle and switching-sequence information.
        """

        if self.symmetry == "HWS":
            if self.level == 2:
                self.n_angles = 2 * self.d + 1
            else:
                self.n_angles = 2 * self.d
        else:
            self.n_angles = self.d

        if self.level == 2:
            self.n_sequences = 2
            self.u0_candidates = np.array([1, -1])
            self.delta_u = (-1) ** np.arange(1, self.n_angles + 1)
        else:
            self.n_sequences = 1
            self.u0_candidates = np.array([1])
            self.delta_u = (-1) ** np.arange(2, self.n_angles + 2)

        self.delta_u = self.delta_u.astype(float)

    def build_system_model(self):
        """
        Build harmonic weighting factors used in the objective function.

        For grid-connected systems, the weighting factors are obtained from the
        LCL-filter frequency-response magnitude.
        """

        if not self.is_grid:
            self.harmonic_weights = np.ones(len(self.harmonic_orders))
            return

        state_space = self.sys.cont_state_space

        F_sys = state_space.F
        G_sys = state_space.G

        # Grid current as the output.
        C_sys = np.array([
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
        ])

        D_sys = np.zeros((2, 3))

        filter_model = ct.ss(F_sys, G_sys, C_sys, D_sys)

        self.harmonic_weights = np.zeros(len(self.harmonic_orders))

        for harmonic_index, harmonic_order in enumerate(self.harmonic_orders):
            mag, _, _ = ct.frequency_response(filter_model, [harmonic_order])
            self.harmonic_weights[harmonic_index] = np.linalg.norm(mag)

    def build_constraints(self):
        """
        Build bound and ordering constraints for the switching angles.
        """

        self.constraints.angle_max = (
            np.pi if self.symmetry == "HWS" else np.pi / 2
        )

        self.constraints.bounds = Bounds(
            np.zeros(self.n_angles),
            np.ones(self.n_angles) * self.constraints.angle_max,
        )

        if self.symmetry == "HWS":
            A = np.eye(self.n_angles)

            A += np.block([
                [
                    np.zeros((self.n_angles - 1, 1)),
                    -np.eye(self.n_angles - 1),
                ],
                [
                    np.zeros((1, self.n_angles)),
                ],
            ])

            A[-1, 0] = 1

            b = np.concatenate((
                np.zeros(self.n_angles - 1),
                [np.pi + 1e-12],
            ))

        else:
            A = np.zeros((self.n_angles - 1, self.n_angles))

            for i in range(self.n_angles - 1):
                A[i, i] = 1.0
                A[i, i + 1] = -1.0

            b = np.zeros(self.n_angles - 1)

        self.constraints.linear_constraint = LinearConstraint(A, -np.inf, b)

    def build_initial_points(self):
        """
        Generate Halton initial points for multistart optimization.
        """

        sampler = qmc.Halton(
            d=self.n_angles,
            scramble=True,
            seed=0,
        )

        sampler.fast_forward(1000)

        initial_points = sampler.random(self.n_ini_points)
        initial_points = np.sort(initial_points, axis=1)

        self.x0_set = initial_points * self.constraints.angle_max

    def get_worker_data(self):
        """
        Collect data required by multiprocessing workers.

        Returns
        -------
        dict
            Data shared with worker processes.
        """

        return {
            "harmonic_orders": self.harmonic_orders,
            "delta_u": self.delta_u,
            "harmonic_weights": self.harmonic_weights,
            "level": self.level,
            "is_grid": self.is_grid,
            "symmetry": self.symmetry,
            "bounds": self.constraints.bounds,
            "linear_constraint": self.constraints.linear_constraint,
        }

    # Computation

    def compute(self, m_values=None, use_parallel=True):
        """
        Compute OPPs.

        Parameters
        ----------
        m_values : list[int] or None, default=None
            Modulation-index sample indices to compute. If None, all
            modulation-index samples are computed.

        use_parallel : bool, default=True
            If True, the multistart initial points are solved in parallel.

        Returns
        -------
        dict
            Computed OPP data, including switching angles, modulation indices,
            and switch positions.
        """

        results = {
            "angles": np.zeros((self.n_m, self.n_angles)),
            "modulation_index": np.zeros((self.n_m, 1)),
            "switch_positions": np.zeros((self.n_m, self.n_angles + 1)),
            "symmetry": self.symmetry,
            "converter_type": "2Level" if self.level == 2 else "3Level",
            "d": self.d,
            "system_type": "grid" if self.is_grid else "load",
        }

        if m_values is None:
            m_values = range(1, self.n_m)

        worker_data = self.get_worker_data()

        if use_parallel:
            n_workers = max(1, mp.cpu_count() - 1)

            with mp.Pool(
                processes=n_workers,
                initializer=init_worker,
                initargs=(worker_data,),
            ) as pool:
                self.compute_loop(results, m_values, pool)

        else:
            init_worker(worker_data)
            self.compute_loop(results, m_values, pool=None)

        self.results = results

        return results

    def compute_loop(self, results, m_values, pool):
        """
        Main loop over modulation indices and switching sequences.

        Parameters
        ----------
        results : dict
            Dictionary used to store computed OPP data.

        m_values : iterable
            Modulation-index samples to compute.

        pool : multiprocessing.Pool or None
            Worker pool used for parallel execution.
        """

        for m_index in m_values:

            print(f"m = {m_index + 1} / {self.n_m}")

            modulation_index = (m_index / (self.n_m - 1)) * (4 / np.pi)

            results["modulation_index"][m_index, 0] = modulation_index

            best_cost = np.inf
            best_result = None
            best_u0 = None

            for u0 in self.u0_candidates:

                tasks = [
                    (x0, modulation_index, u0)
                    for x0 in self.x0_set
                ]

                if pool is None:
                    local_results = [
                        run_single_optimization(task)
                        for task in tasks
                    ]
                else:
                    local_results = pool.map(
                        run_single_optimization,
                        tasks
                    )

                converged_results = [
                    result for result in local_results
                    if result.success
                ]

                if converged_results:
                    candidate = min(
                        converged_results,
                        key=lambda result: result.fun,
                    )
                else:
                    candidate = min(
                        local_results,
                        key=lambda result: result.fun,
                    )

                if candidate.fun < best_cost:
                    best_cost = candidate.fun
                    best_result = candidate
                    best_u0 = u0

            if best_result is not None:
                results["angles"][m_index, :] = best_result.x

                if self.level == 2:
                    switch_positions = np.empty(self.n_angles + 1)
                    switch_positions[0] = best_u0

                    for k in range(self.n_angles):
                        switch_positions[k + 1] = -switch_positions[k]

                else:

                    switch_positions = np.zeros(self.n_angles + 1)
                    switch_positions[1:] = np.cumsum(self.delta_u)

                results["switch_positions"][m_index, :] = switch_positions

    # Save

    def save_results(self, file_name=None):
        """
        Save computed OPPs to a NetCDF file.

        Parameters
        ----------
        file_name : str, optional
            Output file name.
            If None, a file name is generated from the OPP configuration.
        """

        if self.results is None:
            raise RuntimeError(
                "No results found. Run compute() before save_results()."
            )

        if file_name is None:
            system_name = "grid" if self.is_grid else "load"
            level_name = "2Level" if self.level == 2 else "3Level"
            symmetry_name = self.symmetry

            file_name = (
                f"d{self.d}_"
                f"{level_name}_"
                f"{system_name}_"
                f"{symmetry_name}_"
                f"OPPs.nc"
            )

        dataset = xr.Dataset(
            data_vars={
                "switching_angles": (
                    ["angle_index", "modulation_index"],
                    self.results["angles"].T,
                ),
                "switch_positions": (
                    ["position_index", "modulation_index"],
                    self.results["switch_positions"].T,
                ),
            },
            coords={
                "angle_index": np.arange(1, self.n_angles + 1),
                "position_index": np.arange(0, self.n_angles + 1),
                "modulation_index": self.results["modulation_index"].flatten(),
            },
            attrs={
                "description": "Optimized pulse pattern switching angles",
                "angle_units": "radians",
                "converter_type": f"{self.level}Level",
                "system_type": "grid" if self.is_grid else "load",
                "symmetry": self.symmetry,
                "pulse_number": self.d,
                "creation_date": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
            },
        )
        dataset.to_netcdf(file_name)

        print(f"Saved: {file_name}")