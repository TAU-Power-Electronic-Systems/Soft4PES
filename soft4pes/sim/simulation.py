"""
Simulation environment for power electronic systems. 

"""

import numpy as np
from scipy.io import savemat


class ProgressPrinter:
    """
    A class used to print the progress of the simulation process.

    Parameters
    ----------
    total_steps : int
        The total number of steps in the process.

    Attributes
    ----------
    total_steps : int
        The total number of steps in the process.
    last_printed_percent : int
        The last printed percentage of progress.
    """

    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.last_printed_percent = -5

    def __call__(self, current_step):
        """
        Prints the current progress with steps of 5 percent.

        Parameters
        ----------
        current_step : int
            The number of the current step in the process.
        """
        current_percent = int(np.round(current_step / self.total_steps * 100))
        if current_percent > self.last_printed_percent + 4:
            print(f"{current_percent}%")
            self.last_printed_percent = current_percent


class Simulation:
    """
    Simulation environment.

    Parameters
    ----------
    sys : system object
        System model.
    conv : converter object
        Converter model.
    ctr : controller object
        Control system.
    Ts_sim : float
        Simulation sampling interval [s].

    Attributes
    ----------
    sys : system object
        System model.
    conv : converter object
        Converter model.
    ctr : controller object.
        Control system.
    Ts_sim : float
        Simulation sampling interval [s].
    t_stop : float
        Simulation stop time [s].
    matrices : SimpleNamespace
        Discrete state-space matrices of the simulated system.
    simulation_data : dict
        Data from the simulation.
    """

    def __init__(self, sys, conv, ctr, Ts_sim):
        self.sys = sys
        self.conv = conv
        self.ctr = ctr
        self.Ts_sim = Ts_sim
        self.t_stop = 0
        self.matrices = self.sys.get_discrete_state_space(
            self.conv.v_dc, self.Ts_sim)
        self.simulation_data = None

        # Check if self.ctr.Ts/Ts_sim is an integer. Use tolerance to prevent
        # floating point errors
        Ts_rat = self.ctr.Ts / self.Ts_sim
        if abs(Ts_rat - round(Ts_rat)) > 1e-10:
            raise ValueError(
                "The ratio of control system sampling interval to "
                "simulation sampling interval must be an integer.")

    def simulate(self, t_stop):
        """
        Simulate the system.

        Parameters
        ----------
        t_stop : float
            Simulation length [s]. Simulation start time is always 0 s, i.e. kTs = 0.
        """

        progress_printer = ProgressPrinter(int(t_stop / self.ctr.Ts))
        self.t_stop = t_stop

        for k in range(int(self.t_stop / self.ctr.Ts)):

            # Execute the controller
            kTs = k * self.ctr.Ts
            uk_abc = self.ctr(self.sys, self.conv, kTs)

            for k_sim in range(int(self.ctr.Ts / self.Ts_sim)):

                kTs_sim = kTs + k_sim * self.Ts_sim
                self.sys.update_state(self.matrices, uk_abc, kTs_sim)

            progress_printer(k)

        self.simulation_data = {'ctr': self.ctr.sim_data, 'sys': self.sys.data}

        # Save the simulation data to a .mat file
        savemat('examples/sim.mat', self.simulation_data)
