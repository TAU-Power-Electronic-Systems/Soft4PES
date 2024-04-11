""" Model of grid with stiff voltage source and RL-load in alpha-beta frame"""

import numpy as np
from soft4pes.util.conversions import abc_2_alpha_beta


class RLGrid:
    """
    Model of grid with stiff voltage source and RL-load in alpha-beta frame. 
    Grid voltage is treated as disturbance.

    Attributes
    ----------
    Vgr : float
        Grid rated voltage [pu].
    wg : float
        Grid angular frequency calculated [pu].
    Rg : float
        Resistance [pu].
    Lg : float
        Inductance [pu].
    x : 1 x 2 ndarray of floats
        Current state of the grid [pu]. The grid state is represented by the grid current.
    """

    def __init__(self, Vgr, fgr, Rg, Lg, base):
        """
        Initialize a RLGrid instance. Set inital states to zero.

        Parameters
        ----------
        Vgr : float
            Grid rated voltage [V].
        fgr : float
            Grid rated frequency [Hz].
        Rg : float
            Resistance [Ohm].
        Lg : float
            Inductance [H].
        base : base value object
            Base values.
        """
        self.Vgr = Vgr / base.V
        self.wg = 2 * np.pi * fgr / base.w
        self.Rg = Rg / base.Z
        self.Lg = Lg / base.L
        self.x = np.array([0, 0])
        self.base = base

    def get_next_state(self, x, u, v_dc, t, Ts):
        """
        Calculate the next state of the grid using discrete system model.

        Parameters
        ----------
        x : 1 x 2 ndarray of floats
            Current state of the grid [pu].
        u : 3 x 1 ndarray of ints
            Converter switch position.
        v_dc : float
            Converter output terminal voltage [V].
        t : float
            Current time [t].
        Ts : float
            Time step [s].

        Returns
        -------
        1 x 2 ndarray of floats
            Next state of the grid [pu].
        """

        matrices = self.get_state_space(v_dc, Ts)

        v = self.get_grid_voltage(t)

        return np.dot(matrices['A'], x) + np.dot(matrices['B1'], u) + np.dot(
            matrices['B2'], v)

    def get_state_space(self, v_dc, Ts):
        """
        Get the discrete state-space model of the grid in alpha-beta frame.
        Discretization is done using the forward Euler method.

        Parameters
        ----------
        v_dc : float
            Converter output terminal voltage [pu].
        Ts : float
            Time step [s].

        Returns
        -------
        dict
            A dictionary containing matrices A, B1, B2, and C of the state-space model.
        """
        Rg = self.Rg
        Lg = self.Lg
        Ts = Ts * self.base.w

        # Clarke transformation matrix
        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

        F = -Rg / Lg * np.eye(2)
        G1 = v_dc / 2 * 1 / Lg * K
        G2 = -1 / Lg * np.eye(2)

        A = np.eye(2) + F * Ts
        B1 = G1 * Ts
        B2 = G2 * Ts
        C = np.array([[1, 0], [0, 1]])

        return {'A': A, 'B1': B1, 'B2': B2, 'C': C}

    def get_grid_voltage(self, t):
        """
        Get the grid voltage at a specific time.

        Parameters
        ----------
        t : float
            Current time [s].

        Returns
        -------
        1 x 2 ndarray of floats
            Grid voltage in alpha-beta frame [pu].
        """

        phi = self.wg * (t * self.base.w)
        v_abc = np.sqrt(2 / 3) * self.Vgr * np.sin(phi + 2 * np.pi / 3 *
                                                   np.array([0, -1, 1]))

        v = abc_2_alpha_beta(v_abc)
        return v

    def update_state(self, x):
        """
        Update the current state of the grid.

        Parameters
        ----------
        x : 1 x 2 ndarray of floats
            New state of the grid.
        """
        self.x = x

    def get_current(self, x):
        """
        Get the grid current from the state.

        Parameters
        ----------
        x : 1 x 2 ndarray of floats
            Current state of the grid.

        Returns
        -------
        1 x 2 ndarray of floats
            Grid current [pu].
        """
        return x
