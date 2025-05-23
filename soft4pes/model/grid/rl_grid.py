""" Model of a grid with a voltage source and an RL impedance in alpha-beta frame. The magnitude of 
the grid voltage is configurable as a function of time. """

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import Sequence, abc_2_alpha_beta
from soft4pes.model.common.system_model import SystemModel
from soft4pes.utils.conversions import dq_2_alpha_beta


class RLGrid(SystemModel):
    """
    Model of a grid with a voltage source and an RL impedance in alpha-beta frame. The state of the 
    system is the grid current (same as the converter current). The system input is the converter 
    three-phase switch position or modulating signal. The grid voltage is considered to be a 
    disturbance and the magnitude of the grid voltage is configurable as a function of time using a 
    Sequence object.

    This class can be used as a base class for other grid models.

    Parameters
    ----------
    par : RLGridParameters
        Grid parameters in p.u.
    conv : converter object
        Converter object.
    base : base value object
        Base values.
    ig_ref_init : 1 x 2 ndarray of floats, optional
        Reference at discrete time instant kTs = 0 for starting simulation from steady state.

    Attributes
    ----------
    data : SimpleNamespace
        Namespace for storing simulation data.
    par : RLGridParameters
        Grid parameters in p.u.
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

    def __init__(self, par, conv, base, ig_ref_init=None):
        super().__init__(par=par,
                         base=base,
                         conv=conv,
                         x_size=2,
                         state_map={
                             'ig': slice(0, 2),
                             'i_conv': slice(0, 2)
                         })
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

    def get_continuous_state_space(self):
        """
        Calculate the continuous-time state-space model of the system.

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing matrices F, G1 and G2 of the continuous-time 
            state-space model. 
        """

        Rg = self.par.Rg
        Xg = self.par.Xg

        # Clarke transformation matrix
        K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                                [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

        F = -Rg / Xg * np.eye(2)
        G1 = self.conv.v_dc / 2 * 1 / Xg * K
        G2 = -1 / Xg * np.eye(2)

        return SimpleNamespace(F=F, G1=G1, G2=G2)

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

        # Get grid peak voltage
        if isinstance(self.par.Vg, Sequence):
            Vg = np.sqrt(2 / 3) * self.par.Vg(kTs)
        else:
            Vg = np.sqrt(2 / 3) * self.par.Vg

        vg_abc = Vg * np.sin(theta + 2 * np.pi / 3 * np.array([0, -1, 1]))

        vg = abc_2_alpha_beta(vg_abc)
        return vg

    def get_next_state(self, matrices, u_abc, kTs):
        """
        Calculate the next state of the system.

        Parameters
        ----------
        u_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        matrices : SimpleNamespace
            A SimpleNamespace object containing the state-space model matrices.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        ndarray of floats
            The next state of the system.
        """

        vg = self.get_grid_voltage(kTs)
        x_kp1 = np.dot(matrices.A, self.x) + np.dot(
            matrices.B1, u_abc) + np.dot(matrices.B2, vg)
        return x_kp1

    def get_measurements(self, kTs):
        """
        Update the measurement data of the system.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        SimpleNamespace
            A SimpleNamespace object containing the grid voltage in alpha-beta frame.
        """

        return SimpleNamespace(vg=self.get_grid_voltage(kTs))
