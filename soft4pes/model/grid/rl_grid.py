""" Model of a grid with stiff voltage source and RL-load in alpha-beta frame"""

import numpy as np
from soft4pes.util.conversions import abc_2_alpha_beta


class RLGrid:
    """
    Model of a grid with stiff voltage source and RL-load in alpha-beta frame. 

    Attributes
    ----------
    Vgr : float
        Grid rated voltage [pu].
    wg : float
        Grid angular frequency [pu].
    Rg : float
        Resistance [pu].
    Xg : float
        Reactance [pu].
    x : 1 x 2 ndarray of floats
        Current state of the grid [pu]. The grid state is represented by the 
        grid current in alpha-beta frame.
    """

    def __init__(self, Vgr, fgr, Rg, Lg, base):
        """
        Initialize a RLGrid instance. Set inital state to zero.

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
        self.Xg = Lg / base.L
        self.x = np.array([0, 0])
        self.base = base

    def get_next_state(self, x, u, v_dc, t, Ts):
        """
        Calculate the next state of the grid using discrete state-space model.

        Parameters
        ----------
        x : 1 x 2 ndarray of floats
            Current state of the grid [pu].
        u : 1 x 3 ndarray of ints
            Converter three-phase switch position.
        v_dc : float
            Converter dc-link voltage [pu].
        t : float
            Current time [s].
        Ts : float
            Time step [s].

        Returns
        -------
        1 x 2 ndarray of floats
            Next state of the grid [pu].
        """

        matrices = self.get_state_space(v_dc, Ts)

        vg = self.get_grid_voltage(t)

        return np.dot(matrices['A'], x) + np.dot(matrices['B1'], u) + np.dot(
            matrices['B2'], vg)

    def get_state_space(self, v_dc, Ts):
        """
        Get the discrete state-space model of the grid in alpha-beta frame.
        Discretization is done using the forward Euler method.

        Parameters
        ----------
        v_dc : float
            Converter dc-link voltage [pu].
        Ts : float
            Time step [s].

        Returns
        -------
        dict
            A dictionary containing matrices A, B1, B2, and C of the state-space model.
        """
        Rg = self.Rg
        Xg = self.Xg
        Ts = Ts * self.base.w

        # Clarke transformation matrix
        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

        F = -Rg / Xg * np.eye(2)
        G1 = v_dc / 2 * 1 / Xg * K
        G2 = -1 / Xg * np.eye(2)

        A = np.eye(2) + F * Ts
        B1 = G1 * Ts
        B2 = G2 * Ts
        C = np.array([[1, 0], [0, 1]])

        return {'A': A, 'B1': B1, 'B2': B2, 'C': C}

    def get_grid_voltage(self, t):
        """
        Get the grid voltage at a specific time instant.

        Parameters
        ----------
        t : float
            Current time [s].

        Returns
        -------
        1 x 2 ndarray of floats
            Grid voltage in alpha-beta frame [pu].
        """

        theta = self.wg * (t * self.base.w)
        vg_abc = np.sqrt(2 / 3) * self.Vgr * np.sin(theta + 2 * np.pi / 3 *
                                                    np.array([0, -1, 1]))

        vg = abc_2_alpha_beta(vg_abc)
        return vg

    def update_state(self, x):
        """
        Update the current state of the grid.

        Parameters
        ----------
        x : 1 x 2 ndarray of floats
            New state of the grid [pu].
        """
        self.x = x

    def get_current(self, x):
        """
        Get the grid current from the state.

        Parameters
        ----------
        x : 1 x 2 ndarray of floats
            Current state of the grid [pu].

        Returns
        -------
        1 x 2 ndarray of floats
            Grid current [pu].
        """
        return x
