"""
Simulation environment for power electronic systems. 

"""

import os
import numpy as np
from scipy.io import savemat
from types import SimpleNamespace


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


class SwitchingLogic:
    """
    A class to handle switching-related logic, such as quantizing switching time instants and 
    extracting the three-phase switch position or modulating signal.

    Parameters
    ----------
    Ts_sim : float
        Simulation sampling interval [s].
    Ts : float
        Control system sampling interval [s].

    Attributes
    ----------
    Ts_sim : float
        Simulation sampling interval [s].
    Ts : float
        Control system sampling interval [s].
    k_switch : ndarray
        Quantized switching times.
    u_abc : ndarray
        Three-phase switch position or modulating signal.
    """

    def __init__(self, Ts_sim, Ts):
        self.Ts_sim = Ts_sim
        self.Ts = Ts
        self.k_switch = 0
        self.u_abc = np.zeros(3)

    def quantize_switching_time_instants(self, t_switch):
        """
        Quantize the switching time instants.

        Parameters
        ----------
        t_switch : ndarray
            Switching time instants. 

        Returns
        -------
        ndarray
            Quantized switching time instants.
        """

        return np.round(t_switch * self.Ts / self.Ts_sim)

    def get_switch_positions(self, ctr_output, k_sim):
        """
        Get the three-phase switch position or modulating signal for the current discrete time 
        instant. The switching time instants are quantized to the simulation sampling interval in 
        the beginning of the control interval.

        Parameters
        ----------
        ctr_output : SimpleNamespace
            Output from the controller including the switching time instants and the corresponding 
            switch position or modulating signal.
        k_sim : int
            The current simulation step within the control interval.

        Returns
        -------
        ndarray
            Three-phase switch positions or modulating signal for current simulation step.
        """

        # Get the quantized switching time instants. The quantization is done only once at the
        # beginning of the control interval.
        if k_sim == 0:
            self.k_switch = self.quantize_switching_time_instants(
                ctr_output.t_switch)

        # Get the three-phase switch positions or modulating signal for the current simulation step.
        # The output is updated if a switching time instant equals the current simulation step.
        if np.any(k_sim == self.k_switch):
            # Get the three-phase switch position or modulating signal for the current simulation
            # step. Multiple switching time instants can be equal to the current simulation step. If
            # this is the case, the last entry is used, as it includes the preceding ones.
            self.u_abc = ctr_output.switch_pos[k_sim == self.k_switch]
            if self.u_abc.ndim == 2:
                self.u_abc = self.u_abc[-1]
        return self.u_abc


class Simulation:
    """
    Simulation environment.

    Parameters
    ----------
    sys : system object
        System model.
    ctr : controller object
        Control system.
    Ts_sim : float
        Simulation sampling interval [s].

    Attributes
    ----------
    sys : system object
        System model.
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
    switching_logic : SwitchingLogic
        Object for handling switching logic.
    """

    def __init__(self, sys, ctr, Ts_sim, disc_method='forward_euler'):
        self.sys = sys
        self.ctr = ctr
        self.Ts_sim = Ts_sim
        self.t_stop = 0
        self.matrices = self.sys.get_discrete_state_space(
            self.Ts_sim, disc_method)
        self.simulation_data = None
        self.switching_logic = SwitchingLogic(Ts_sim, ctr.Ts)

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
            kTs = k * self.ctr.Ts

            # Execute the controller
            ctr_output = self.ctr(self.sys, kTs)

            for k_sim in range(int(self.ctr.Ts / self.Ts_sim)):
                kTs_sim = kTs + k_sim * self.Ts_sim

                # Extract the three-phase switch position or modulating signal
                u_abc = self.switching_logic.get_switch_positions(
                    ctr_output, k_sim)

                # Update the system state
                self.sys.update(self.matrices, u_abc, kTs_sim)

            progress_printer(k)

        # Get the simulation data
        self.ctr.get_control_system_data()
        self.simulation_data = {'ctr': self.ctr.data, 'sys': self.sys.data}

        return self.process_simulation_data(
            SimpleNamespace(sys=self.sys.data, ctr=self.ctr.data))

    def save_data(self, filename='sim_data.mat', path=''):
        """
        Save the simulation data to a .mat file.

        Parameters
        ----------
        filename : str, optional
            Name of the file to save the data to. The default filename is 'sim_data.mat'.
        path : str, optional
            Directory path to save the file to. The path can be absolute or relative to the current 
            directory. The default saving directory is the current directory. 
        """

        # Ensure the filename ends with .mat
        if not filename.endswith('.mat'):
            filename += '.mat'

        # Ensure the directory exists
        if path and not os.path.exists(path):
            os.makedirs(path)

        full_path = os.path.join(path, filename)
        savemat(full_path, self.simulation_data)

    def process_simulation_data(self, data):
        """
        Recursively convert lists of arrays in a SimpleNamespace to NumPy arrays.

        Parameters
        ----------
        data : SimpleNamespace or list of ndarray
            The data to be converted. Can be a SimpleNamespace or a list of arrays.

        Returns
        -------
        SimpleNamespace or ndarray
            A SimpleNamespace with lists of arrays converted to NumPy arrays, or a NumPy array if 
            the input is a list of arrays.
        """
        if isinstance(data, list):
            # If data is a list of arrays, convert it to a single NumPy array
            stacked_array = np.array(data)
            return stacked_array

        elif isinstance(data, SimpleNamespace):
            # If data is a SimpleNamespace, recursively process its attributes
            for attr in data.__dict__:
                setattr(data, attr,
                        self.process_simulation_data(getattr(data, attr)))
            return data

        else:
            # If data is neither a list nor a SimpleNamespace, return it as is
            return data
