"""
Asynchronous carrier-based pulse width modulation (CB-PWM) for two and three-level converters.  
"""

import numpy as np
from soft4pes.control.common.controller import Controller
from types import SimpleNamespace


class CarrierPWM(Controller):

    def __init__(self):
        super().__init__()
        self.carrier_rising = False

    def execute(self, sys, kTs):
        """
        Generate switching times and switch positions using asynchronous carrier-based pulse width 
        modulation (CB-PWM). The modulating signal is sampled at the peaks of the carrier, 
        resulting in the device switching frequency of 1/(2Ts) for two-level converters and 1/(4Ts) 
        for three-level converters, when Ts is the sampling time of the control system.
        
        The produced output is presented below. Note that the switching times are in ascending 
        order.
        
                                |      Switch positions       |
        Switching time instants | Phase A | Phase B | Phase C | 
        ---------------         |---------|---------|---------|
                    0           | state   | state   | state
                    t_switch[1] | state   | state   | state
                    t_switch[2] | state   | state   | state
                    t_switch[3] | state   | state   | state 

        Parameters
        ----------
        sys : system object
            The system model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        t_switch : ndarray
            Switching time instants.
        switch_array : ndarray
            Switch positions.
        """

        u_ref_abc = self.input.u_abc

        # Normalize the reference signal for 2-level and 3-level converters, i.e. ensure that the
        # modulating signal is between 0 and 1. This effectively produces the duty ratios. Note
        # that the full duty cycle corresbonds the controller sampling interval.
        #
        # For two level converter, the duty ratio is for the upper switch. For the three level
        # converter, the duty ratio is for the switches 1 and 3 when the modulating signal is >= 0
        # and for the switches 2 and 4 when the modulating signal is < 0
        if sys.conv.nl == 2:
            d_abc = 0.5 * (u_ref_abc + 1)
        elif sys.conv.nl == 3:
            d_abc = np.where(u_ref_abc < 0, 1 + u_ref_abc, u_ref_abc)
        else:
            raise ValueError(
                'Only two- and three-level converters are supported.')

        # Compute switching time instants and corresponding switch positions. Add a zero at the
        # beginning of the array to include the switch position when the cycle starts
        if self.carrier_rising:
            # If the carrier is rising, the duty ratio corresponds to the percentage the switch is
            # on from the start of the cycle.
            t_switch = np.concatenate(([0], d_abc))
            switch_pos = (d_abc > t_switch[:, np.newaxis]).astype(int)
        else:
            # If the carrier is falling, calculate the time the switch is off from the start of the
            # cycle (d-1).
            t_switch = np.concatenate(([0], 1 - d_abc))
            switch_pos = (~(1 - d_abc > t_switch[:, np.newaxis])).astype(int)

        # Switch positions are 1 and 0. Adjust them to be -1 and 1 for a two-level converter and
        # -1, 0, and 1 for a three-level converter, depending on the sign of the modulating signal
        if sys.conv.nl == 2:
            switch_pos = 2 * switch_pos - 1
        elif sys.conv.nl == 3:
            for i in range(3):
                # If the modulating signal is negative, the possible switch positions are 0 and -1
                if u_ref_abc[i] < 0:
                    switch_pos[:, i] -= 1

        # Sort switching time instants and switch positions to ensure that the switching time
        # instants are in ascending order. This is important in case two switching instants appear
        # at (almost) the same time. By sorting, we can pick only the latter switch position, as it
        # also includes the former switch position
        sorted_t_indices = np.argsort(t_switch)
        t_switch = t_switch[sorted_t_indices]
        switch_pos = switch_pos[sorted_t_indices]

        # Toggle the carrier direction
        self.carrier_rising = not self.carrier_rising

        self.output = SimpleNamespace(
            t_switch=t_switch,
            switch_pos=switch_pos,
        )

        return self.output
