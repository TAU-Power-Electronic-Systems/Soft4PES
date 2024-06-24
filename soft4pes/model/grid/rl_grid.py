""" Model of a grid with stiff voltage source and RL-load in alpha-beta frame"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils.conversions import abc_2_alpha_beta


class RLGrid:
    """
    Model of a grid with stiff voltage source and RL-load in alpha-beta frame. 

    Attributes
    ----------
    Vgr : float
        Grid rated voltage [p.u.] (line-to-line rms voltage).
    wg : float
        Grid angular frequency [p.u.].
    Rg : float
        Resistance [p.u.].
    Xg : float
        Reactance [p.u.].
    x : 1 x 2 ndarray of floats
        Current state of the grid [p.u.]. The grid state is represented by the 
        grid current in alpha-beta frame.
    """

    def __init__(self, Vgr, fgr, Rg, Lg, base):
        """
        Initialize a RLGrid instance. Set inital state to zero.

        Parameters
        ----------
        Vgr : float
            Grid rated voltage [V] (line-to-line rms voltage).
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

    def get_discrete_state_space(self, v_dc, Ts):
        """
        Get the discrete state-space model of the grid in alpha-beta frame.
        Discretization is done using the forward Euler method.

        Parameters
        ----------
        v_dc : float
            Converter dc-link voltage [p.u.].
        Ts : float
            Sampling interval [s].

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing matrices A, B1, B2, and C of the 
            state-space model. 
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

        return SimpleNamespace(A=A, B1=B1, B2=B2, C=C)

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
            Grid voltage in alpha-beta frame [p.u.].
        """

        theta = self.wg * (t * self.base.w)

        # Grid peak voltage
        Vg = np.sqrt(2 / 3) * self.Vgr

        vg_abc = Vg * np.sin(theta + 2 * np.pi / 3 * np.array([0, -1, 1]))

        vg = abc_2_alpha_beta(vg_abc)
        return vg

    def update_state(self, x):
        """
        Update the current state of the grid.

        Parameters
        ----------
        x : 1 x 2 ndarray of floats
            New state of the grid [p.u.].
        """
        self.x = x

    def get_current(self, x):
        """
        Get the grid current from the state.

        Parameters
        ----------
        x : 1 x 2 ndarray of floats
            Current state of the grid [p.u.].

        Returns
        -------
        1 x 2 ndarray of floats
            Grid current [p.u.].
        """
        return x
