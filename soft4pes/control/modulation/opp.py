"""
Offline optimal pulse pattern (OPP) computation.

This module provides functionality for computing OPPs using multistart nonlinear optimization.

Supported features
------------------
- Two-level and three-level converters
- QaHWS and HWS pulse patterns
- Load-connected and grid-connected converters

Notes
-----
The optimization is intended for offline lookup-table generation and is
not designed for real-time control applications.
"""

import multiprocessing as mp

import control as ct
import numpy as np
from scipy.io import savemat
from scipy.optimize import Bounds, LinearConstraint, minimize
from scipy.stats import qmc


# =========================================================================
# Multiprocessing helper functions
# =========================================================================

_WORKER_DATA = None

def _init_worker(worker_data):
    """
    Initialize worker-local data.

    Large arrays are stored once per worker process to reduce
    inter-process communication overhead.
    """

    global _WORKER_DATA
    _WORKER_DATA = worker_data


def _objective_function(x):
    """
    Evaluate the OPP objective function.

    """

    data = _WORKER_DATA

    x = np.asarray(x)

    harmonics_int = data["harmonics_int"]
    delta_u = data["delta_u"]
    g_n_ab = data["g_n_ab"]

    level = data["level"]
    sys_ind = data["sys_ind"]
    hws = data["hws"]

    cost = 0.0

    for k_i, k in enumerate(harmonics_int):

        if hws:
            coeff_cos = np.dot(delta_u, np.cos(k*x))
            coeff_sin = np.dot(delta_u, np.sin(k*x))

            coeff_energy = coeff_cos**2 + coeff_sin**2

            if sys_ind:
                cost += ((g_n_ab[k_i]/k)**2) * coeff_energy
            else:
                cost += ((g_n_ab[k_i]/(k**2))**2) * coeff_energy

        else:
            inner = np.dot(delta_u, np.cos(k*x))

            if level:
                coeff = 1.0 + 2.0*inner
            else:
                coeff = inner

            if sys_ind:
                cost += ((g_n_ab[k_i]*coeff)/k)**2
            else:
                cost += ((g_n_ab[k_i]*coeff)/(k**2))**2

    return cost


def _nonlinear_constraint_function(x, modulation_index, u0):
    """
    Equality constraints.

    QaHWS:
          One equality constraint to enforce a fundamental OPP component with the desired amplitude (modulation index).

    HWS:
          Two equality constraints corresponding to the amplitude and
          phase of the fundamental OPP component.
    """

    data = _WORKER_DATA

    x = np.asarray(x)

    delta_u = data["delta_u"]
    level = data["level"]
    hws = data["hws"]

    if hws:
        coeff_cos = np.dot(delta_u, np.cos(x))
        coeff_sin = np.dot(delta_u, np.sin(x))

        if level:
            ceq1 = +(u0*4.0/np.pi)*coeff_cos - modulation_index
            ceq2 = -(u0*4.0/np.pi)*coeff_sin
        else:
            ceq1 = +(2.0/np.pi)*coeff_cos - modulation_index
            ceq2 = -(2.0/np.pi)*coeff_sin

        return np.array([ceq1, ceq2])

    inner = np.dot(delta_u, np.cos(x))

    if level:
        ceq = (u0*4.0/np.pi)*(1.0 + 2.0*inner) - modulation_index
    else:
        ceq = (4.0/np.pi)*inner - modulation_index

    return np.array([ceq])


def _run_single_optimization(task):
    """
    Run one local SLSQP optimization from one initial point.
    """

    x0, modulation_index, u0 = task

    data = _WORKER_DATA

    nonlinear_constraint = {
        "type": "eq",
        "fun": lambda x: _nonlinear_constraint_function(
            x,
            modulation_index,
            u0
        )
    }

    result = minimize(
        _objective_function,
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


# ======================================================================
# MAIN OPP CLASS
# ======================================================================

class OPP:
    """
    Offline OPP computation.
    """

    def __init__(
        self,
        sys,
        d=5,
        level=1,
        sys_ind=1,
        hws=0,
        n_m=256,
        n_ini_points=100,
        max_harmonics=500,
        include_zero_modulation=False):
       
       """
       Initialize the OPP problem.

       Parameters
       ----------
       sys : SystemModel
        Soft4PES system model.

       d : int
        Pulse number.

       level : int
        Converter topology.

        - 1 : two-level converter
        - 0 : three-level converter

       sys_ind : int
        System type.

        - 1 : grid-connected system
        - 0 : load-connected system

       hws : int
        Waveform symmetry.

        - 1 : half-wave symmetry (HWS)
        - 0 : quarter-wave and half-wave symmetry (QaHWS)

       n_m : int
        Number of modulation-index samples.

       n_ini_points : int
        Number of multistart initial points.

       max_harmonics : int
        Maximum harmonic order included in the objective function.

       include_zero_modulation : bool
        Include the zero-modulation operating point.
       """

       self.sys = sys

       self.d = d
       self.level = level
       self.sys_ind = sys_ind
       self.hws = hws
       self.n_m = n_m
       self.n_ini_points = n_ini_points
       self.max_harmonics = max_harmonics
       self.include_zero_modulation = include_zero_modulation

       self._build_problem()

    # ==================================================================
    # PROBLEM SETUP
    # ==================================================================

    def _build_problem(self):
        """
        Build all quantities needed before optimization.
        """

        self._build_harmonics()
        self._build_switching_sequence()
        self._build_system_model()
        self._build_constraints()
        self._build_initial_points()

    def _build_harmonics(self):
        """
        Build the considered harmonic orders.

        Only non-triplen odd harmonics are included:
        """

        harmonics = np.arange(2, self.max_harmonics + 1)

        self.harmonics_int = harmonics[
            (harmonics % 2 == 1)
            &
            (harmonics % 3 != 0)
        ]

    def _build_switching_sequence(self):
        """
        Build switching-angle and switching-sequence information.
        """

        if self.hws:
            if self.level:
                self.n_angles = 2*self.d + 1
            else:
                self.n_angles = 2*self.d
        else:
            self.n_angles = self.d

        if self.level:
            self.n_sequences = 2
            self.u0_candidates = np.array([1.0, -1.0])
            self.delta_u = (-1.0)**np.arange(1, self.n_angles + 1)
        else:
            self.n_sequences = 1
            self.u0_candidates = np.array([1.0])
            self.delta_u = (-1.0)**np.arange(2, self.n_angles + 2)

        self.delta_u = self.delta_u.astype(float)

    def _build_system_model(self):
        """
        Build the harmonic weighting.

        For grid-connected systems, the LCL-filter transfer function is
        included through the frequency response magnitude.
        """

        if not self.sys_ind:
            self.g_n_ab = np.ones(len(self.harmonics_int))
            return

        ss = self.sys.cont_state_space

        A_sys = ss.F
        B_sys = ss.G

        # Select the grid current as the output.
        C_sys = np.array([
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
        ])

        D_sys = np.zeros((2, 3))

        sys_g = ct.ss(A_sys, B_sys, C_sys, D_sys)

        self.g_n_ab = np.zeros(len(self.harmonics_int))

        for i, n in enumerate(self.harmonics_int):
            mag, _, _ = ct.frequency_response(sys_g, [n])
            self.g_n_ab[i] = np.linalg.norm(mag)

    def _build_constraints(self):
        """
        Build bound and ascending-order constraints for the switching angles.

        For QaHWS:
            0 <= alpha_1 <= alpha_2 <= ... <= pi/2

        For HWS:
            ordering constraints are used over [0, pi].
        """

        self.angle_max = np.pi if self.hws else np.pi/2

        self.bounds = Bounds(
            np.zeros(self.n_angles),
            np.ones(self.n_angles)*self.angle_max,
        )

        if self.hws:
            A = np.eye(self.n_angles)

            A += np.block([
                [
                    np.zeros((self.n_angles-1, 1)),
                    -np.eye(self.n_angles-1),
                ],
                [
                    np.zeros((1, self.n_angles)),
                ],
            ])

            A[-1, 0] = 1

            b = np.concatenate((
                np.zeros(self.n_angles-1),
                [np.pi + 1e-12],
            ))

        else:
            A = np.zeros((self.n_angles-1, self.n_angles))

            for i in range(self.n_angles-1):
                A[i, i] = 1.0
                A[i, i+1] = -1.0

            b = np.zeros(self.n_angles-1)

        self.linear_constraint = LinearConstraint(A, -np.inf, b)

    def _build_initial_points(self):
        """
        Generate Halton initial points for multistart optimization.
        """

        sampler = qmc.Halton(
            d=self.n_angles,
            scramble=True,
            seed=0,
        )

        sampler.fast_forward(1000)

        raw = sampler.random(self.n_ini_points)
        raw = np.sort(raw, axis=1)

        self.x0_set = raw * self.angle_max

    def _get_worker_data(self):
        """
        Collect data required by multiprocessing workers.
        """

        return {
            "harmonics_int": self.harmonics_int,
            "delta_u": self.delta_u,
            "g_n_ab": self.g_n_ab,
            "level": self.level,
            "sys_ind": self.sys_ind,
            "hws": self.hws,
            "bounds": self.bounds,
            "linear_constraint": self.linear_constraint,
        }

    # ==================================================================
    # COMPUTATION
    # ==================================================================

    def compute(self, m_values=None, use_parallel=True):
        """
        Compute OPPs.

        Parameters
        ----------
        m_values : list[int] or None
            Specific modulation-index indices to compute.
            If None, all modulation indices are computed.

        use_parallel : bool
            If True, multistart points are solved in parallel.

        Returns
        -------
        results : dict
            Dictionary containing angles, cost, exitflag, modulation index,
            and sequence information.
        """

        results = {
            "angles": np.zeros((self.n_m, self.n_angles)),
            "cost": np.zeros((self.n_m, 1)),
            "exitflag": np.zeros((self.n_m, 1)),
            "mod_index": np.zeros((self.n_m, 1)),
            "hws": self.hws,
            "level": self.level,
            "d": self.d,
            "n_angles": self.n_angles,
        }

        if self.level:
            results["sequence"] = np.zeros((self.n_m, 1))

        if m_values is None:
            if self.include_zero_modulation:
                m_values = range(self.n_m)
            else:
                m_values = range(1, self.n_m)

        worker_data = self._get_worker_data()

        if use_parallel:
            n_workers = max(1, mp.cpu_count() - 1)

            with mp.Pool(
                processes=n_workers,
                initializer=_init_worker,
                initargs=(worker_data,),
            ) as pool:

                self._compute_loop(results, m_values, pool)

        else:
            _init_worker(worker_data)
            self._compute_loop(results, m_values, pool=None)

        self.results = results

        return results

    def _compute_loop(self, results, m_values, pool):
        """
        Main loop over modulation indices and switching sequences.
        """

        for m in m_values:

            print(f"m = {m+1} / {self.n_m}")

            modulation_index = (
                m / (self.n_m - 1)
            ) * (4.0/np.pi)

            results["mod_index"][m, 0] = modulation_index

            best_cost = np.inf
            best_result = None
            best_sequence = None

            for seq, u0 in enumerate(self.u0_candidates, start=1):

                tasks = [
                    (x0, modulation_index, u0)
                    for x0 in self.x0_set
                ]

                if pool is None:
                    local_results = [
                        _run_single_optimization(task)
                        for task in tasks
                    ]
                else:
                    local_results = pool.map(
                        _run_single_optimization,
                        tasks
                    )

                successful = [
                    res for res in local_results
                    if res.success
                ]

                if successful:
                    candidate = min(successful, key=lambda res: res.fun)
                else:
                    candidate = min(local_results, key=lambda res: res.fun)

                if candidate.fun < best_cost:
                    best_cost = candidate.fun
                    best_result = candidate
                    best_sequence = seq

            if best_result is not None:
                results["angles"][m, :] = best_result.x
                results["cost"][m, 0] = best_result.fun
                results["exitflag"][m, 0] = int(best_result.success)

                if self.level:
                    results["sequence"][m, 0] = best_sequence

    # ==================================================================
    # SAVE
    # ==================================================================

    def save_results(self, file_name=None):
        """
        Save computed OPPs to a .mat file.
        """

        if not hasattr(self, "results"):
            raise RuntimeError(
                "No results found. Run compute() before save_results()."
            )

        if file_name is None:
            system_name = "grid" if self.sys_ind else "load"
            level_name = "2Level" if self.level else "3Level"
            symmetry_name = "HWS" if self.hws else "QaHWS"

            file_name = (
                f"d{self.d}_"
                f"{level_name}_"
                f"{system_name}_"
                f"{symmetry_name}_"
                f"OPPs.mat"
            )

        savemat(file_name, {"results": self.results})

        print(f"Saved: {file_name}")