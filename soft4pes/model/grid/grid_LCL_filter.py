""" Model of a grid with LCL filter in alpha-beta frame """

from types import SimpleNamespace
import numpy as np


class GridLCLFilter:
    """
    Model of a grid with LCL filter in alpha-beta frame. 
    The state of the system is the converter current, capacitor voltage, grid current and grid voltage in the alpha-beta frame.
    The system input is the converter 3-phase switch position.

    Attributes
    ----------
    wg : float
        Grid angular frequency [p.u.].
    Rg : float
        Grid Resistance [p.u.].
    Xg : float
        Grid Reactance [p.u.].
    Rt : float
        Leakage Resistance [p.u.].
    Xt : float
        Leakage Reactance [p.u.].
    Rfg : float
        Filter Resistance on Grid Side [p.u.].
    Xfg : float
        Filter Reactance on Grid Side [p.u.].
    Rfc : float
        Filter Resistance on Converter Side [p.u.].
    Xfc : float
        Filter Reactance on Converter Side [p.u.].
    Rc : float
        Filter Capacitor Resistance [p.u.].
    Xc : float
        Filter capacitor Reactance [p.u.].
    i_conv : 1 x 2 ndarray of floats
        Converter current state in alpha-beta frame [p.u.].
    vc : 1 x 2 ndarray of floats
        Capacitor voltage state in alpha-beta frame [p.u.].
    ig : 1 x 2 ndarray of floats
        Grid current state in alpha-beta frame [p.u.].
    vg : 1 x 2 ndarray of floats
        Grid voltage state in alpha-beta frame [p.u.].
    x : 8 x 1 ndarray of floats
        All states of the grid in alpha-beta frame [p.u.].
    base : base value object
        Base values.
    data_sim : dict
        System data.
    """

    def __init__(self, fgr, Rg, Lg, Rt, Lt, Rfg, Lfg, Rfc, Lfc, Rc, C, base):
        """
        Initialize a Grid with LCL Filter instance.

        Parameters
        ----------
        fgr : float
            Grid rated frequency [Hz].
        Rg : float
            Grid Resistance [Ohm].
        Lg : float
            Grid Inductance [H].
        Rt : float
            Leakage Resistance [Ohm].
        Lt : float
            Leakage Inductance [H].
        Rfg : float
            Filter Resistance on Grid Side [Ohm].
        Lfg : float
            Filter Inductance on Grid Side [H].
        Rfc : float
            Filter Resistance on Converter Side [Ohm].
        Lfc : float
            Filter Inductance on Converter Side [H].
        Rc : float
            Filter Capacitor Resistance [Ohm].
        C : float
            Filter capacitance [F].        
        base : base value object
            Base values.
        """

        self.wg = 2 * np.pi * fgr / base.w
        self.Rg = Rg / base.Z
        self.Xg = Lg / base.L
        self.Rt = Rt / base.Z
        self.Xt = Lt / base.L
        self.Rfg = Rfg / base.Z
        self.Xfg = Lfg / base.L
        self.Rfc = Rfc / base.Z
        self.Xfc = Lfc / base.L
        self.Rc = Rc / base.Z
        self.Xc = base.C / C
        self.i_conv = np.array([0, 0])
        self.vc = np.array([0, 0])
        self.ig = np.array([0, 0])
        self.vg = np.array([0, -1])
        self.x = np.concatenate((self.i_conv, self.vc, self.ig, self.vg)).reshape(-1, 1)
        self.base = base
        self.sim_data = {
            'x': [],
            't': [],
        }

    def get_discrete_state_space(self, v_dc, Ts):
        """
        Get the discrete state-space model of the grid in alpha-beta frame.
        Discretization is done using exact discretization with the sampling interval Ts.

        Parameters
        ----------
        v_dc : float
            Converter dc-link voltage [p.u.].
        Ts : float
            Sampling interval [s].

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing matrices A, B and C of the 
            state-space model. 
        """
        Rg = self.Rg
        Xg = self.Xg
        Rt = self.Rt 
        Xt = self.Xt 
        Rfg = self.Rfg
        Xfg = self.Xfg
        Rfc = self.Rfc
        Xfc = self.Xfc
        Rc = self.Rc
        Xc = self.Xc    
        Ts = Ts * self.base.w
        R = Rg + Rt + Rfg
        X = Xg + Xt + Xfg
        R1 = Rfc + Rc
        R2 = R + Rc

        # Clarke transformation matrix
        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])
        
        F11 = (-R1/Xfc) * np.eye (2)
        F12 = (-1/Xfc) * np.eye (2)
        F13 = (Rc/Xfc) * np.eye (2)
        F14 = np.zeros ((2,2))

        F21 = (1/Xc) * np.eye (2)
        F22 = np.zeros ((2,2))
        F23 = (-1/Xc) * np.eye (2)
        F24 = np.zeros ((2,2))

        F31 = (Rc/X) * np.eye (2)
        F32 = (1/X) * np.eye (2)
        F33 = (-R2/X) * np.eye (2)
        F34 = (-1/X) * np.eye (2)

        F41 = np.zeros ((2,2))
        F42 = np.zeros ((2,2))
        F43 = np.zeros ((2,2))
        F44 = self.wg * np.array([[0, -1], [1, 0]])
        
        row1 = np.hstack([F11, F12, F13, F14])
        row2 = np.hstack([F21, F22, F23, F24])
        row3 = np.hstack([F31, F32, F33, F34])
        row4 = np.hstack([F41, F42, F43, F44])

        F = np.vstack([row1, row2, row3, row4])
        G = (v_dc / (2 * Xfc)) * np.dot(np.concatenate([np.eye(2), np.zeros((2, 6))], axis=1).T, K)

        A = np.exp (F * Ts)
        B = -np.dot(np.dot(np.linalg.inv(F), np.eye(8) - A), G) 
        C = np.concatenate([np.eye(6), np.zeros((6, 2))], axis=1)

        return SimpleNamespace(A=A, B=B, C=C)

    def update_state(self, u, matrices):
        """
        Get the next state of the grid.

        Parameters
        ----------
        u : 1 x 3 ndarray of floats
            Converter 3-phase switch position.
        matrices : SimpleNamespace
            A SimpleNamespace object containing matrices A, B and C of the 
            state-space model.

        Returns
        -------
        8 x 1 ndarray of floats
            Next state of the grid [p.u.].
        """
        x_kp1 = np.dot(matrices.A, self.x) + np.dot(matrices.B, u.T)
        self.x = x_kp1

    def save_data(self, t):
        """
        Save system data.

        Parameters
        ----------
        t : float
            Current time [s].
        """

        self.sim_data['x'].append(self.x)
        self.sim_data['t'].append(t)
