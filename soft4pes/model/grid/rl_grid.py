""" Model of a grid with stiff voltage source and RL-load in alpha-beta frame"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import abc_2_alpha_beta


class RLGrid:
    """
    Model of a grid with stiff voltage source and RL-load in alpha-beta frame. 
    The state of the system is the grid current in the alpha-beta frame.
    The system input is the converter three-phase switch position.
    The grid voltage is considered to be a disturbance.

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
        Current state of the grid [p.u.].
    base : base value object
        Base values.
    data_sim : dict
        System data.
    """

    def __init__(self, Vgr, fgr, Rg, Lg, base):
        self.Vgr = Vgr / base.V
        self.wg = 2 * np.pi * fgr / base.w
        self.Rg = Rg / base.Z
        self.Xg = Lg / base.L
        self.x = np.array([0, 0])
        self.base = base
        self.sim_data = {
            'x': [],
            'vg': [],
            't': [],
        }

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
            A SimpleNamespace object containing matrices A, B1 and B2 of the 
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

        return SimpleNamespace(A=A, B1=B1, B2=B2)

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

    def update_state(self, u, matrices, t):
        """
        Get the next state of the grid.

        Parameters
        ----------
        u : 1 x 3 ndarray of floats
            Converter three-phase switch position.
        matrices : SimpleNamespace
            A SimpleNamespace object containing matrices A, B1 and B2 of the 
            state-space model.

        Returns
        -------
        1 x 2 ndarray of floats
            Next state of the grid [p.u.].
        """

        vg = self.get_grid_voltage(t)
        self.save_data(vg, t)
        x_kp1 = np.dot(matrices.A, self.x) + np.dot(matrices.B1, u) + np.dot(
            matrices.B2, vg)
        self.x = x_kp1

    def save_data(self, vg, t):
        """
        Save system data.

        Parameters
        ----------
        vg : 1 x 2 ndarray of floats
            Grid voltage in alpha-beta frame [p.u.].
        t : float
            Current time [s].
        """

        self.sim_data['x'].append(self.x)
        self.sim_data['vg'].append(vg)
        self.sim_data['t'].append(t)
