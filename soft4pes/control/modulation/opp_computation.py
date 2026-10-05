"""
Offline optimized pulse pattern (OPP) computation.

Supported features
------------------
- Two-level and three-level converters
- QaHWS and HWS pulse patterns
- Machine- or grid-connected converters
"""

from datetime import datetime
import multiprocessing as mp
from types import SimpleNamespace

import control as ct
import numpy as np
import xarray as xr
from scipy.optimize import Bounds, LinearConstraint, minimize
from scipy.stats import qmc

from soft4pes.model.grid.rl_grid import RLGrid
from soft4pes.model.grid.rl_grid_lcl_filter import RLGridLCLFilter

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
        Data shared by all optimization tasks executed by each worker.
    """

    global _WORKER_DATA
    _WORKER_DATA = worker_data


def objective_function(x):
    """
    Evaluate the OPP objective function.

    Parameters
    ----------
    x : ndarray
        Vector of switching angles.

    Returns
    -------
    float
        Value of the OPP objective function.
    """

    data = _WORKER_DATA

    x = np.asarray(x)

    converter_level = data["level"]
    symmetry = data["symmetry"]
    delta_u = data["delta_u"]

    harmonic_orders = data["harmonic_orders"]
    harmonic_weights = data["harmonic_weights"]

    harmonic_angles = harmonic_orders[:, None] * x[None, :]

    if symmetry == "HWS":
        cosine_sum = np.cos(harmonic_angles) @ delta_u
        sine_sum = np.sin(harmonic_angles) @ delta_u

        cost = np.sum(
            (harmonic_weights / harmonic_orders)**2
            * (cosine_sum**2 + sine_sum**2)
        )

    else:
        cosine_sum = np.cos(harmonic_angles) @ delta_u

        if converter_level == 2:
            harmonic_sum = 1 + 2 * cosine_sum
        else:
            harmonic_sum = cosine_sum

        cost = np.sum(
            ((harmonic_weights * harmonic_sum) / harmonic_orders)**2
        )

    return cost

def objective_gradient(x):
    """
    Evaluate the gradient of the objective function.

    Parameters
    ----------
    x : ndarray
        Vector of switching angles.

    Returns
    -------
    ndarray
        Gradient of the objective function with respect to the switching angles.
    """
    data = _WORKER_DATA

    x = np.asarray(x)

    converter_level = data["level"]
    symmetry = data["symmetry"]
    delta_u = data["delta_u"]

    harmonic_orders = data["harmonic_orders"]
    harmonic_weights = data["harmonic_weights"]

    harmonic_angles = harmonic_orders[:, None] * x[None, :]

    if symmetry == "HWS":
        cosine_sum = np.cos(harmonic_angles) @ delta_u
        sine_sum = np.sin(harmonic_angles) @ delta_u

        factors = 2 * harmonic_weights**2 / harmonic_orders

        gradient = np.sum(
            factors[:, None]
            * (
                -cosine_sum[:, None] * np.sin(harmonic_angles)
                + sine_sum[:, None] * np.cos(harmonic_angles)
            ),
            axis=0,
        ) * delta_u

    else:
        cosine_sum = np.cos(harmonic_angles) @ delta_u

        if converter_level == 2:
            harmonic_sum = 1 + 2 * cosine_sum
            scale = 4
        else:
            harmonic_sum = cosine_sum
            scale = 2

        factors = (
            -scale
            * harmonic_weights**2
            * harmonic_sum
            / harmonic_orders
        )

        gradient = np.sum(
            factors[:, None] * np.sin(harmonic_angles),
            axis=0,
        ) * delta_u

    return gradient


def nonlinear_constraint_function(x, modulation_index, u0):
    """
    Evaluate the OPP equality constraints.

    Parameters
    ----------
    x : ndarray
        Vector of switching angles.

    modulation_index : float
        Desired modulation index.

    u0 : int
        Initial switch position.

    Returns
    -------
    ndarray
        Values of equality constraints.
    """

    data = _WORKER_DATA

    x = np.asarray(x)

    converter_level = data["level"]
    symmetry = data["symmetry"]
    delta_u = data["delta_u"]

    if symmetry == "HWS":
        cosine_sum = np.dot(delta_u, np.cos(x))
        sine_sum = np.dot(delta_u, np.sin(x))

        if converter_level == 2:
            ceq1 = (u0 * 4 / np.pi) * cosine_sum - modulation_index
            # The fundamental OPP component is chosen to have zero initial phase.
            ceq2 = -(u0 * 4 / np.pi) * sine_sum
        else:
            ceq1 = (2 / np.pi) * cosine_sum - modulation_index
            ceq2 = -(2 / np.pi) * sine_sum

        return np.array([ceq1, ceq2])

    if converter_level == 2:
        ceq = (u0 * 4 /
               np.pi) * (1 + 2 * np.dot(delta_u, np.cos(x))) - modulation_index
    else:
        ceq = (4 / np.pi) * np.dot(delta_u, np.cos(x)) - modulation_index

    return np.array([ceq])

def nonlinear_constraint_jacobian(x, u0):
    """
    Evaluate the Jacobian of the equality constraints.

    Parameters
    ----------
    x : ndarray
        Vector of switching angles.

    u0 : int
        Initial switch position.

    Returns
    -------
    ndarray
        Jacobian of the equality constraints with respect to the switching angles.
    """
    data = _WORKER_DATA

    converter_level = data["level"]
    symmetry = data["symmetry"]
    delta_u = data["delta_u"]

    if symmetry == "HWS":
        if converter_level == 2:
            factor = u0 * 4 / np.pi
        else:
            factor = 2 / np.pi

        jacobian = np.vstack((
            -factor * delta_u * np.sin(x),
            -factor * delta_u * np.cos(x),
        ))

    else:
        if converter_level == 2:
            factor = u0 * 8 / np.pi
        else:
            factor = 4 / np.pi

        jacobian = (
            -factor * delta_u * np.sin(x)
        )[None, :]

    return jacobian

def run_single_optimization(task):
    """
    Run a local SLSQP optimization from a single initial point.

    Parameters
    ----------
    task : tuple
        Tuple containing the initial vector of switching angles, modulation index,
        and initial switch position.

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
        ),
        "jac": lambda x: nonlinear_constraint_jacobian(
            x,
            u0,
        ),
    }

    result = minimize(
        objective_function,
        x0,
        method="SLSQP",
        jac=objective_gradient,
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


class OPPComputation:
    """
    Offline OPP computation.
    
    Parameters
    ----------
    sys : SystemModel
        System model.

    d : int, default=5
        Base number of switching transitions used to construct the OPP.
        For example, this corresponds to the pulse number for three-level
        QaHWS OPPs.

    symmetry : str, default="QaHWS"
        Waveform symmetry.

        Options
        -------
        - "HWS": half-wave symmetry
        - "QaHWS": quarter- and half-wave symmetry

    n_m : int, default=256
        Number of points used to discretize the modulation index range
        [0, 4/pi], resulting in n_m - 1 nonzero modulation indices for
        which OPPs are computed.

    n_ini_points : int, default=1000
        Number of multistart initial points.

    max_harmonics : int, default=500
        Maximum harmonic order included in the objective function.

    modulation_indices : array_like or None, default=None
        Modulation indices for which OPPs are computed. If None, the
        modulation index range [0, 4/pi] is discretized using n_m
        points.

    Attributes
    ----------
    setup : SimpleNamespace
        OPP configuration data.

    harmonics : SimpleNamespace
        Harmonic orders and weighting factors used in the objective function.

    switching : SimpleNamespace
        Switching-angle and switching-pattern data.

    constraints : SimpleNamespace
        Bounds and ordering constraints for the switching angles.

    initial_points : ndarray or None
        Initial vectors of switching angles used for multistart optimization.

    results : dict or None
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
        modulation_indices=None,
    ):

        self.sys = sys

        if symmetry not in ("HWS", "QaHWS"):
            raise ValueError("symmetry must be either 'QaHWS' or 'HWS'.")

        if n_m < 2:
            raise ValueError("n_m must be at least 2.")

        if modulation_indices is None:
            modulation_indices = (np.arange(1, n_m) / (n_m - 1)) * (4 / np.pi)
        else:
            modulation_indices = np.asarray(modulation_indices, dtype=float)

            if modulation_indices.size == 0:
                raise ValueError(
                    "modulation_indices must contain at least one value.")

            if (np.any(modulation_indices <= 0)
                    or np.any(modulation_indices > 4 / np.pi)):
                raise ValueError(
                    "modulation_indices must be in the interval (0, 4/pi].")

        self.setup = SimpleNamespace(
            d=d,
            level=sys.conv.nl,
            symmetry=symmetry,
            n_m=n_m,
            n_ini_points=n_ini_points,
            max_harmonics=max_harmonics,
            modulation_indices=modulation_indices,
            is_grid=isinstance(sys, RLGrid),
        )

        self.harmonics = SimpleNamespace(
            orders=None,
            weights=None,
        )

        self.switching = SimpleNamespace(
            n_angles=None,
            u0_candidates=None,
            delta_u=None,
        )

        self.constraints = SimpleNamespace(
            angle_max=None,
            bounds=None,
            linear_constraint=None,
        )

        self.initial_points = None
        self.results = None

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

        harmonics = np.arange(2, self.setup.max_harmonics + 1)

        self.harmonics.orders = harmonics[(harmonics % 2 == 1)
                                          & (harmonics % 3 != 0)]

    def build_switching_sequence(self):
        """
        Build switching-angle and switching-sequence information.
        """

        if self.setup.symmetry == "HWS":
            if self.setup.level == 2:
                # We assume a switching transition at pi for two-level HWS OPPs.
                self.switching.n_angles = 2 * self.setup.d + 1
            else:
                self.switching.n_angles = 2 * self.setup.d
        else:
            self.switching.n_angles = self.setup.d

        if self.setup.level == 2:
            self.switching.u0_candidates = np.array([1, -1])
            self.switching.delta_u = (-1)**np.arange(
                1, self.switching.n_angles + 1)
        else:
            self.switching.u0_candidates = np.array([1])
            self.switching.delta_u = (-1)**np.arange(
                2, self.switching.n_angles + 2)

        self.switching.delta_u = self.switching.delta_u.astype(float)

    def build_system_model(self):
        """
        Build harmonic weighting factors used in the objective function.

        For systems with an LCL filter, the weighting factors are based on the
        gain of the transfer function from the switch position to the output
        current. All other currently supported systems use 1/n weighting
        factors.
        """

        if isinstance(self.sys, RLGridLCLFilter):

            state_space = self.sys.cont_state_space

            # States are the alpha-beta components of the converter current,
            # grid current, and capacitor voltage.
            F_sys = state_space.F
            G_sys = state_space.G

            # Grid current as the output.
            C_sys = np.array([
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0],
            ])

            D_sys = np.zeros((2, 3))

            filter_model = ct.ss(F_sys, G_sys, C_sys, D_sys)

            self.harmonics.weights = np.zeros(len(self.harmonics.orders))

            for harmonic_index, harmonic_order in enumerate(
                    self.harmonics.orders):
                mag, _, _ = ct.frequency_response(filter_model,
                                                  [harmonic_order])
                self.harmonics.weights[harmonic_index] = np.linalg.norm(mag)

        else:
            # All other currently supported systems use 1/n harmonic weighting factors.
            self.harmonics.weights = 1 / self.harmonics.orders

    def build_constraints(self):
        """
        Build bound and ordering constraints for the switching angles.
        """

        self.constraints.angle_max = (np.pi if self.setup.symmetry == "HWS"
                                      else np.pi / 2)

        self.constraints.bounds = Bounds(
            np.zeros(self.switching.n_angles),
            np.ones(self.switching.n_angles) * self.constraints.angle_max,
        )

        A = np.zeros((self.switching.n_angles - 1, self.switching.n_angles))

        for i in range(self.switching.n_angles - 1):
            A[i, i] = 1.0
            A[i, i + 1] = -1.0

        b = np.zeros(self.switching.n_angles - 1)

        # Remove duplicate reflected solutions in the two-level HWS formulation.
        if self.setup.symmetry == "HWS" and self.setup.level == 2:
            A = np.vstack((
                A,
                np.zeros((1, self.switching.n_angles)),
            ))

            A[-1, 0] = 1.0
            A[-1, -1] = 1.0

            b = np.concatenate((
                b,
                [np.pi + 1e-12],
            ))

        self.constraints.linear_constraint = LinearConstraint(A, -np.inf, b)

    def build_initial_points(self):
        """
        Generate Halton initial points for multistart optimization.
        """

        sampler = qmc.Halton(
            d=self.switching.n_angles,
            scramble=True,
            seed=0,
        )

        # Skip the first Halton points to improve sample distribution.
        sampler.fast_forward(1000)

        initial_points = sampler.random(self.setup.n_ini_points)
        initial_points = np.sort(initial_points, axis=1)

        self.initial_points = initial_points * self.constraints.angle_max

    def get_worker_data(self):
        """
        Collect data required by multiprocessing workers.

        Returns
        -------
        dict
            Data shared with worker processes.
        """

        return {
            "level": self.setup.level,
            "symmetry": self.setup.symmetry,
            "delta_u": self.switching.delta_u,
            "harmonic_orders": self.harmonics.orders,
            "harmonic_weights": self.harmonics.weights,
            "bounds": self.constraints.bounds,
            "linear_constraint": self.constraints.linear_constraint,
        }

    def compute(self, use_parallel=True):
        """
        Compute OPPs.

        Parameters
        ----------
        use_parallel : bool, default=True
            If True, the multistart initial points are solved in parallel.

        Returns
        -------
        dict
            Computed OPP lookup-table data, including switching angles,
            modulation indices, and switch positions.
        """
        if use_parallel:
            mp.freeze_support()

        n_modulation_indices = len(self.setup.modulation_indices)

        results = {
            "angles":
            np.full((n_modulation_indices, self.switching.n_angles), np.nan),
            "modulation_index":
            self.setup.modulation_indices.copy(),
            "switch_positions":
            np.full(
                (n_modulation_indices, self.switching.n_angles + 1), np.nan
            ),
            "symmetry":
            self.setup.symmetry,
            "converter_type":
            f"{self.setup.level}Level",
            "d":
            self.setup.d,
            "system_type":
            "grid" if self.setup.is_grid else "machine",
        }

        worker_data = self.get_worker_data()

        if use_parallel:
            n_workers = max(1, mp.cpu_count() - 1)

            with mp.Pool(
                    processes=n_workers,
                    initializer=init_worker,
                    initargs=(worker_data, ),
            ) as pool:
                self.compute_loop(results, pool)

        else:
            init_worker(worker_data)
            self.compute_loop(results, pool=None)

        self.results = results

        return results

    def compute_loop(self, results, pool):
        """
        Main loop over modulation indices and switching sequences.

        Parameters
        ----------
        results : dict
            Dictionary used to store computed OPP data.

        pool : multiprocessing.Pool or None
            Worker pool used for parallel execution.
        """

        for m_index, modulation_index in enumerate(
                self.setup.modulation_indices):

            print(f"Modulation index = {modulation_index:.4f}")

            best_cost = np.inf
            best_result = None
            best_u0 = None

            for u0 in self.switching.u0_candidates:

                tasks = [(x0, modulation_index, u0)
                         for x0 in self.initial_points]

                if pool is None:
                    local_results = [
                        run_single_optimization(task) for task in tasks
                    ]
                else:
                    local_results = pool.map(run_single_optimization, tasks)

                converged_results = [
                    result for result in local_results if result.success
                ]

                if converged_results:
                    candidate = min(
                        converged_results,
                        key=lambda result: result.fun,
                    )

                    if candidate.fun < best_cost:
                        best_cost = candidate.fun
                        best_result = candidate
                        best_u0 = u0

            if best_result is not None:
                results["angles"][m_index, :] = best_result.x

                if self.setup.level == 2:
                    switch_positions = np.empty(self.switching.n_angles + 1)
                    switch_positions[0] = best_u0

                    for k in range(self.switching.n_angles):
                        switch_positions[k + 1] = -switch_positions[k]

                else:
                    switch_positions = np.zeros(self.switching.n_angles + 1)
                    switch_positions[1:] = np.cumsum(self.switching.delta_u)

                results["switch_positions"][m_index, :] = switch_positions

    def save_results(self, filename=None):
        """
        Save computed OPPs to a NetCDF file.

        Parameters
        ----------
        filename : str, optional
            Output file name.
            If None, a file name is generated from the OPP configuration.
        """

        if self.results is None:
            raise RuntimeError(
                "No results found. Run compute() before save_results().")

        if filename is None:
            system_name = "grid" if self.setup.is_grid else "machine"
            level_name = f"{self.setup.level}Level"
            symmetry_name = self.setup.symmetry

            filename = (f"d{self.setup.d}_"
                        f"{level_name}_"
                        f"{system_name}_"
                        f"{symmetry_name}_"
                        f"OPPs.nc")

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
                "angle_index": np.arange(1, self.switching.n_angles + 1),
                "position_index": np.arange(0, self.switching.n_angles + 1),
                "modulation_index": self.results["modulation_index"],
            },
            attrs={
                "description": "Optimized pulse pattern lookup table",
                "angle_units": "radians",
                "converter_type": f"{self.setup.level}Level",
                "system_type": "grid" if self.setup.is_grid else "machine",
                "symmetry": self.setup.symmetry,
                "base_number_of_switching_transitions": self.setup.d,
                "creation_date": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
            },
        )
        dataset.to_netcdf(filename)

        print(f"Saved: {filename}")
