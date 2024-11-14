""" Model of a grid with stiff voltage source and RL-load in alpha-beta frame"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import abc_2_alpha_beta
from soft4pes.model.common.system_model import SystemModel
from soft4pes.utils.conversions import dq_2_alpha_beta


class RLGrid(SystemModel):
    """
    Model of a grid with stiff voltage source and RL-load in alpha-beta frame. The state of the 
    system is the grid current in the alpha-beta frame. The system input is the converter 
    three-phase switch position or modulating signal. The grid voltage is considered to be a 
    disturbance.

    Parameters
    ----------
    par : RLGridParameters
        Grid parameters in p.u..
    base : base value object
        Base values.
    ig_ref_init : 1 x 2 ndarray of floats, optional
        Reference at discrete time instant kTs = 0 for starting simulation from steady state.

    Attributes
    ----------
    par : RLGridParameters
        Grid parameters in p.u..
    x : 1 x 2 ndarray of floats
        Current state of the grid [p.u.].
    base : base value object
        Base values.
    """

    def __init__(self, par, base, ig_ref_init=None):
        super().__init__()
        self.par = par
        self.base = base
        self.set_initial_state(ig_ref_init=ig_ref_init)

    def set_initial_state(self, **kwargs):
        """
        Set the initial state of the system based on the grid current reference, if provided.

        Parameters
        ----------
        ig_ref_init : 1 x 2 ndarray of floats, optional
            Reference at discrete time instant kTs = 0 for starting simulation from steady state.
        """

        ig_ref_init = kwargs.get('ig_ref_init')
        if ig_ref_init is not None:
            vg = self.get_grid_voltage(0)
            theta = np.arctan2(vg[1], vg[0])
            self.x = dq_2_alpha_beta(ig_ref_init, theta)
        else:
            self.x = np.zeros(2)

    def get_discrete_state_space(self, v_dc, Ts):
        Rg = self.par.Rg
        Xg = self.par.Xg
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

    def get_grid_voltage(self, kTs):
        """
        Get the grid voltage at a specific discrete time instant.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        1 x 2 ndarray of floats
            Grid voltage in alpha-beta frame [p.u.].
        """

        theta = self.par.wg * (kTs * self.base.w)

        # Grid peak voltage
        Vg = np.sqrt(2 / 3) * self.par.Vgr

        vg_abc = Vg * np.sin(theta + 2 * np.pi / 3 * np.array([0, -1, 1]))

        vg = abc_2_alpha_beta(vg_abc)
        return vg

    def update_state(self, matrices, uk_abc, kTs):
        vg = self.get_grid_voltage(kTs)
        x_kp1 = np.dot(matrices.A, self.x) + np.dot(
            matrices.B1, uk_abc) + np.dot(matrices.B2, vg)
        meas = SimpleNamespace(vg=vg)
        super().update(x_kp1, uk_abc, kTs, meas)
