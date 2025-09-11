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
        Generate switching time instants and switch positions using asynchronous carrier-based pulse 
        width modulation (CB-PWM). The modulating signal is sampled at the peaks of the carrier, 
        resulting in the device switching frequency of 1/(2Ts) for two-level converters. For three-
        level converters, the device switching frequency is roughly half the apparent switching, ie.
        the carrier frequency, when phase-disposition PWM is used.

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

        # Calculate the duty ratio, bound to [0 1]. Note that the full duty cycle corresponds to the
        # controller sampling interval.

        # For two-level converter, the duty ratio of a phase represents the fraction of the sampling
        # interval that the upper switch in the corresponding phase is on. When the upper switch is
        # on, the converter phase is in switch position 1, and when the upper switch is off, the
        # switch position of the phase is -1.

        # In the case of a three-level converter, the duty ratio represents the fraction of the
        # sampling interval that
        # - Switch S1 is on and S3 off, when the modulating signal is >= 0. Switch S2 is always on
        #   and S4 off in this case. The phase is then in switch position 1 when S1 is on and and 0
        #   while S1 is off.
        # - Switch S4 is on and S2 off, when the modulating signal is < 0. Switch S1 is always off
        #   and S3 on. The phase is then in switch position -1 when S4 is on and 0 when S4 is off

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

        # Switch positions are 1 and 0, corresponding the state of the individual switches (S1 for
        # two-level converter, S1/S4 for three-level converter depending on the sign of the
        # modulating signal). Deduce the phase switch positions.
        if sys.conv.nl == 2:
            # Map 0 → -1 and 1 → 1
            switch_pos_phase = 2 * switch_pos - 1
        elif sys.conv.nl == 3:
            # Map 0 → 0 and 1 → 1. The negative phase switch position -1 is selected when the
            # modulating signal is negative. Then, map 1 -> 0 and 0 -> -1.
            switch_pos_phase = np.where(u_ref_abc < 0, switch_pos - 1,
                                        switch_pos)
        else:
            raise ValueError(
                'Only two- and three-level converters are supported.')

        # Sort switching time instants and switch positions to ensure that the switching time
        # instants are in ascending order. This is important in case two switching instants appear
        # at (almost) the same time. By sorting, we can pick only the latter switch position, as it
        # also includes the former switch position
        sorted_t_indices = np.argsort(t_switch)
        t_switch = t_switch[sorted_t_indices]
        switch_pos_phase = switch_pos_phase[sorted_t_indices]

        # Toggle the carrier direction
        self.carrier_rising = not self.carrier_rising

        self.output = SimpleNamespace(
            t_switch=t_switch,
            switch_pos=switch_pos_phase,
        )

        return self.output
