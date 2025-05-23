""" 
Model of a grid with stiff voltage source, RL-load and an LC(L) filter in alpha-beta frame.
"""

from types import SimpleNamespace
import numpy as np

from soft4pes.model.grid.rl_grid import RLGrid


class RLGridLCLFilter(RLGrid):
    """
    Model of a grid with stiff voltage source, RL-load and an LC(L) filter in alpha-beta frame. If 
    the grid side inductance is not provided, the filter is in LC configuration.
    
    The state of the system is the converter current, the capacitor voltage and the grid current in 
    the alpha-beta frame, i.e. x = [i_conv^T, ig^T, vc^T]^T. The system input is the converter 
    three-phase switch position or modulating signal. The grid voltage is considered to be a 
    disturbance. The positive current direction is from the converter to the filter and from the
    filter to the grid for i_conv and ig, respectively. Knowledge of the grid impedance is required,
    and given to the model in the parent class RLGrid.

    Parameters
    ----------
    par_grid : RLGridParameters
        Parameters of the grid.
    par_lcl_filter : LCLFilterParameters
        Parameters of the LCL filter.
    conv : converter object
        Converter object.
    base : base value object
        Base values.

    Attributes
    ----------
    data : SimpleNamespace
        Namespace for storing simulation data.
    par : System parameters
        Combined RLGridParameters and LCLFilterParameters.
    conv : converter object
        Converter object.
    x : 1 x 6 ndarray of floats
        Current state of the grid [p.u.].
    base : base value object
        Base values.
    cont_state_space : SimpleNamespace
        The continuous-time state-space model of the system.
    state_map : dict
        A dictionary mapping states to elements of the state vector.
    """

    def __init__(self, par_grid, par_lcl_filter, conv, base):
        par = SimpleNamespace(**vars(par_grid), **vars(par_lcl_filter))
        super().__init__(par=par, conv=conv, base=base)
        state_map = {
            'i_conv': slice(0, 2),  # Converter current (x[0:2])
            'ig': slice(2, 4),  # Grid current (x[2:4])
            'vc': slice(4, 6),  # Capacitor voltage (x[4:6])
        }
        # Overwrite the state map of RLGrid with the one of RLGridLCLFilter
        self.x_size = 6
        self.state_map = state_map
        self.set_initial_state()

    def set_initial_state(self, **kwargs):
        """
        Set the initial state of the system to zero.
        """

        self.x = np.zeros(6)

    def get_continuous_state_space(self):
        """
        Get the continuous-time state-space model of the system in alpha-beta frame. 

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing matrices F, G1 and G2 of the continuous-time 
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

        G1 = (self.conv.v_dc / (2 * X_fc)) * np.dot(
            np.block([[np.eye(2), np.zeros((2, 4))]]).T, K)

        G2 = np.block(
            [[np.zeros((2, 2)), -1 / X * np.eye(2),
              np.zeros((2, 2))]]).T

        return SimpleNamespace(F=F, G1=G1, G2=G2)
