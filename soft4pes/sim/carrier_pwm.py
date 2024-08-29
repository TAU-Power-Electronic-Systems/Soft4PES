""" Carrier-based PWM. The implementation is asynchronous. The control system is 
sampled twice per carrier period (in the peaks of the carrier). """

import numpy as np


class Carrier:
    """
    Generating a triangular carrier signal.

    Attributes
    ----------
    value : float
        Value of the carrier.
    lower_limit : float
        Minimum value of the carrier.
    upper_limit : float
        Maximum value of the carrier.
    direction : int
        Direction of the carrier.
    step : float
        Carrier step.
    """

    def __init__(self, Ts_ctr, Ts_sim, lower_limit, upper_limit, initial_val):
        """
        Initialize a Carrier instance.

        Parameters
        ----------
        Ts_ctr : float
            Control system sampling interval [s].
        Ts_sim : float
            Simulation sampling interval [s].
        lower_limit : float
            Minimum value of the carrier.
        upper_limit : float
            Maximum value of the carrier.
        initial_val : float
            Initial value of the carrier.
        """

        self.value = initial_val
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.direction = -1
        self.step = 2 * (upper_limit - lower_limit) * (Ts_sim / Ts_ctr)

    def __call__(self):
        """
        Get and update the carrier value.

        Returns
        -------
        float
            Current carrier value.
        """

        # Get carrier value
        carrier_value = self.value

        # Update the carrier signal value
        self.value += self.direction * self.step

        # Keep the carrier signal within the limits
        if self.value <= self.lower_limit:
            overflow = abs(self.value - self.lower_limit)
            self.value = self.lower_limit + overflow
            self.direction = -self.direction

        elif self.value >= self.upper_limit:
            overflow = abs(self.value - self.upper_limit)
            self.value = self.upper_limit - overflow
            self.direction = -self.direction

        return carrier_value


class CarrierPWM:
    """
    Carrier based PWM. The class creates the carrier(s) and produces the three-phase switch 
    positions.

    Attributes
    ----------
    lower_carrier : Carrier
        Lower Carrier object.
    upper_carrier : Carrier
        Upper Carrier object (only for 3-level PWM).
    nl : int
        Number of converter voltage levels.
    get_switch_positions : method 
        Method to generate three-phase switch positions.
    """

    def __init__(self, Ts_ctr, Ts_sim, nl):
        """
        Initialize a CarrierPWM instance.

        Parameters
        ----------
        Ts_ctr : float
            Period time of carrier signal [s].
        Ts_sim : float
            Simulation step time [s].
        nl : int
            Number of converter voltage levels.
        """
        self.nl = nl
        if nl == 2:
            self.lower_carrier = Carrier(Ts_ctr, Ts_sim, -1, 1, 1)
            self.upper_carrier = None
            self.get_switch_positions = self.two_level_comparison

        elif nl == 3:
            self.lower_carrier = Carrier(Ts_ctr, Ts_sim, -1, 0, 0)
            self.upper_carrier = Carrier(Ts_ctr, Ts_sim, 0, 1, 1)
            self.get_switch_positions = self.three_level_comparison

    def two_level_comparison(self, u_abc_ref):
        """
        Generate three-phase switch positions for a two-level converter.

        Parameters
        ----------
        u_abc_ref : 1 x 3 ndarray of floats
            Three-phase modulation signal. 

        Returns
        -------
        1 x 3 ndarray of ints
            Three-phase switch positions.
        """
        carrier = self.lower_carrier()
        u_abc = np.zeros(3, dtype=int)
        for i in range(3):
            u_abc[i] = 1 if u_abc_ref[i] > carrier else -1
        return u_abc

    def three_level_comparison(self, u_abc_ref):
        """
        Generate three-phase switch positions for a three-level converter.

        Parameters
        ----------
        u_abc_ref : 1 x 3 ndarray of floats
            Three-phase modulation signal.

        Returns
        -------
        1 x 3 ndarray of ints
            Three-phase switch positions.
        """
        lower_value = self.lower_carrier()
        upper_value = self.upper_carrier()
        u_abc = np.zeros(3, dtype=int)
        for i in range(3):
            if u_abc_ref[i] > upper_value:
                u_abc[i] = 1
            elif u_abc_ref[i] < lower_value:
                u_abc[i] = -1
            else:
                u_abc[i] = 0
        return u_abc

    def __call__(self, u_abc_ref):
        """
        Generate the three-phase switch positions.

        Parameters
        ----------
        u_abc_ref : 1 x 3 ndarray of floats
            Three-phase modulation signal.

        Returns
        -------
        1 x 3 ndarray of ints
            Three-phase switch positions.
        """
        return self.get_switch_positions(u_abc_ref)
