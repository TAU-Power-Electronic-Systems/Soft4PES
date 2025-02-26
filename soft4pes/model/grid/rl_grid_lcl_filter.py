""" 
Model of a grid with stiff voltage source, RL-load and an LC(L) filter in alpha-beta frame.
"""

from types import SimpleNamespace
import numpy as np
from scipy.linalg import expm

from soft4pes.model.grid.rl_grid import RLGrid


class RLGridLCLFilter(RLGrid):
    """
    Model of a grid with stiff voltage source, RL-load and an LC(L) filter in alpha-beta frame. If 
    the grid side inductance is not provided, the filter is in LC configuration.
    
    The state of the system is the converter current, the capacitor voltage and the grid current in 
    the alpha-beta frame, i.e. x = [i_conv^T, vc^T, ig^T]^T. The system input is the converter 
    three-phase switch position or modulating signal. The grid voltage is considered to be a 
    disturbance. The positive current direction is from the converter to the filter and from the
    filter to the grid for i_conv and ig, respectively. Knowledge of the grid impedance is required,
    and given to the model in the parent class RLGrid.

    Attributes
    ----------
    par : System parameters
        Combined RLGridParameters and LCLFilterParameters.
    x : 1 x 6 ndarray of floats
        Current state of the grid [p.u.].
    base : base value object
        Base values.
    """

    def __init__(self, par_grid, par_lcl_filter, base):
        super().__init__(par=par_grid, base=base)
        self.par = SimpleNamespace(**vars(par_grid), **vars(par_lcl_filter))
        self.set_initial_state()

    def set_initial_state(self, **kwargs):
        """
        Set the initial state of the system to zero.
        """

        self.x = np.zeros(6)

    def get_discrete_state_space(self, v_dc, Ts):
        """
        Get the discrete state-space model of the system in alpha-beta frame. The system is 
        discretized using exact discretization. 

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

        X_fc = self.par.X_fc
        R_fc = self.par.R_fc
        Xc = self.par.Xc
        Rc = self.par.Rc
        X_fg = self.par.X_fg
        R_fg = self.par.R_fg
        Xg = self.par.Xg
        Rg = self.par.Rg
        Ts_pu = Ts * self.base.w

        R1 = R_fc + Rc
        R2 = Rc + R_fg + Rg
        X = X_fg + Xg

        # Clarke transformation matrix
        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

        F11 = (-R1 / X_fc) * np.eye(2)
        F13 = (-1 / X_fc) * np.eye(2)
        F12 = (Rc / X_fc) * np.eye(2)

        F31 = (1 / Xc) * np.eye(2)
        F33 = np.zeros((2, 2))
        F32 = (-1 / Xc) * np.eye(2)

        F21 = (Rc / X) * np.eye(2)
        F23 = (1 / X) * np.eye(2)
        F22 = (-R2 / X) * np.eye(2)

        F = np.block([
            [F11, F12, F13],
            [F21, F22, F23],
            [F31, F32, F33],
        ])

        G1 = (v_dc / (2 * X_fc)) * np.dot(
            np.block([[np.eye(2), np.zeros((2, 4))]]).T, K)

        G2 = np.block(
            [[np.zeros((2, 2)), -1 / X * np.eye(2),
              np.zeros((2, 2))]]).T

        # Discretize the system using exact discretization
        A = expm(F * Ts_pu)
        B1 = np.dot(-np.linalg.inv(F), (np.eye(6) - A)).dot(G1)
        B2 = np.dot(-np.linalg.inv(F), (np.eye(6) - A)).dot(G2)

        return SimpleNamespace(A=A, B1=B1, B2=B2)
