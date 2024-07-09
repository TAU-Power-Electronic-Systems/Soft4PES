"""
Simulation environment for power electronic systems. 
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import savemat


class ProgressPrinter:
    """
    A class used to print the progress of the simulation process.

    Attributes
    ----------
    total_steps : int
        The total number of steps in the process.
    last_printed_percent : int
        The last printed percentage of progress.
    """

    def __init__(self, total_steps):
        """
        Parameters
        ----------
        total_steps : int
            The total number of steps in the process.
        """
        self.total_steps = total_steps
        self.last_printed_percent = -5

    def __call__(self, current_step):
        """
        Prints the current progress with steps of 5 percent.

        Parameters
        ----------
        current_step : int
            The current step in the process.
        """
        current_percent = int(np.round(current_step / self.total_steps * 100))
        if current_percent > self.last_printed_percent + 4:
            print(f"{current_percent}%")
            self.last_printed_percent = current_percent


class Simulation:
    """
    Simulation environment.

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
    """

    def __init__(self, sys, conv, ctr, Ts_sim):
        """
        Initialize a Simulation instance.

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
        """
        self.sys = sys
        self.conv = conv
        self.ctr = ctr
        self.Ts_sim = Ts_sim
        self.t_stop = 0
        self.matrices = self.sys.get_discrete_state_space(
            self.conv.v_dc, self.Ts_sim)

        # Check if self.ctr.Ts/Ts is an integer. Use tolerance to prevent
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
            Simulation stop time [s]. Simulation start time is always 0 s.
        """

        progress_printer = ProgressPrinter(int(t_stop / self.ctr.Ts))

        data = np.empty((0, 2))
        time = np.empty((0, 1))
        u_data = np.empty((0, 3))
        self.t_stop = t_stop

        t = 0
        for i in range(int(self.t_stop / self.ctr.Ts)):

            # Execute the controller
            u = self.ctr(self.sys, self.conv, t)

            for _ in range(int(self.ctr.Ts / self.Ts_sim)):

                # Save data
                data = np.vstack((data, self.sys.x))
                time = np.vstack((time, t))
                u_data = np.vstack((u_data, u))

                self.sys.update_state(u, self.matrices, t)

                t = t + self.Ts_sim

            progress_printer(i)

        # Plot data
        plt.plot(time, data)
        plt.show()

        # Create a dictionary to store data
        data_to_save = {'time': time, 'data': data, 'u': u_data}

        # Save to a .mat file
        savemat('examples/sim.mat', data_to_save)
