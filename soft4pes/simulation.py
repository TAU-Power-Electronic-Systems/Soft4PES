"""
Simulation environment for power electronic systems. 
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import savemat


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
    Ts : float
        Simulation sampling time [s].
    t_stop : float
        Simulation stop time [s].
    """

    def __init__(self, sys, conv, ctr, Ts):
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
        Ts : float
            Simulation sampling time [s].
        """
        self.sys = sys
        self.conv = conv
        self.ctr = ctr
        self.Ts = Ts
        self.t_stop = 0

    def simulate(self, t_stop):
        """
        Simulate the system.

        Parameters
        ----------
        t_stop : float
            Simulation stop time [s]. Simulation start time is always 0 s.
        """

        # For saving data, should be done in a better way
        data = np.empty((0, 2))
        time = np.empty((0, 1))
        self.t_stop = t_stop

        t = 0
        # This expects that t_stop/Ts is an integer
        for i in range(int(self.t_stop / self.ctr.Ts)):

            # Execute the controller
            u = self.ctr(self.sys, self.conv, t)

            # Simulate the model
            # This expects that Ts_control/Ts_sim is an integer
            # Thsi will be removed once continuous simulation is implemented
            for _ in range(int(self.ctr.Ts / self.Ts)):

                # Save data, for debugging and verification, will be removed later
                data = np.vstack((data, self.sys.x))
                time = np.vstack((time, t))

                x_kp1 = self.sys.get_next_state(self.sys.x, u, self.conv.v_dc,
                                                t, self.Ts)
                self.sys.update_state(x_kp1)

                t = t + self.Ts

            print("{}%".format(np.round(i / (t_stop / self.ctr.Ts) * 100, 1)))

        # Plot data, debugging
        plt.plot(time, data)
        plt.show()

        # Create a dictionary to store your data
        data_to_save = {'time': time, 'data': data}

        # Save to a .mat file, debugging
        savemat('examples/sim.mat', data_to_save)
