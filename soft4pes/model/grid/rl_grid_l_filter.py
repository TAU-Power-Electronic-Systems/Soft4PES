""" 
Model of a grid with stiff voltage source, RL impedance and an L filter in alpha-beta frame.
"""

from types import SimpleNamespace
import numpy as np

from soft4pes.model.grid.rl_grid import RLGrid


class RLGridLFilter(RLGrid):
    """
    Model of a grid with stiff voltage source, RL impedance and an L filter in alpha-beta frame.
    
    The state of the system is the converter current (or the grid current) in 
    the alpha-beta frame, i.e. x = [i_conv^T]^T or x = [ig^T]^T. The system input is the converter 
    three-phase switch position or modulating signal. The grid voltage is considered to be a 
    disturbance. The positive current direction is from the converter to the filter and from the
    filter to the grid for i_conv and ig, respectively. Knowledge of the grid impedance is required,
    and given to the model in the parent class RLGrid.

    Parameters
    ----------
    par_grid : RLGridParameters
        Parameters of the grid.
    par_l_filter : LFilterParameters
        Parameters of the L filter.
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
    x : 1 x 2 ndarray of floats
        Current state of the grid [p.u.].
    base : base value object
        Base values.
    cont_state_space : SimpleNamespace
        The continuous-time state-space model of the system.
    state_map : dict
        A dictionary mapping states to elements of the state vector.
    """

    def __init__(self, par_grid, par_l_filter, conv, base):
        par = SimpleNamespace(**vars(par_grid), **vars(par_l_filter))
        super().__init__(par=par, conv=conv, base=base)
        state_map = {
            'i_conv': slice(0, 2),  # Converter current (x[0:2])
        }
        # Overwrite the state map of RLGrid with the one of RLGridLCLFilter
        self.x_size = 2
        self.state_map = state_map
        self.set_initial_state()

    def set_initial_state(self, **kwargs):
        """
        Set the initial state of the system to zero.
        """

        self.x = np.zeros(2)

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
        Xg = self.par.Xg
        Rg = self.par.Rg

        # Clarke transformation matrix
        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

        F = -(Rg+R_fc) / (Xg+X_fc) * np.eye(2)
        G1 = self.conv.v_dc / 2 * 1 / (Xg+X_fc) * K
        G2 = -1 / (Xg+X_fc) * np.eye(2)

        return SimpleNamespace(F=F, G1=G1, G2=G2)
