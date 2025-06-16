"""
Control system class to manage and execute a set of control loops.
"""

from types import SimpleNamespace
import numpy as np


class ControlSystem:
    """
    ControlSystem class to manage and execute a set of control loops. The class accepts any number 
    of control loops and combines them to a complete control system.

    Parameters
    ----------
    control_loops : list
        List of controller instances. The control loops are executed in the order they appear in the
        list. 
    ref_seq : SimpleNamespace
        Reference sequences for the control system. The sequences must be of class Sequence. The 
        references are given to the first control loop in the list.
    Ts : float
        Sampling interval [s].
    pwm : modulator, optional
        Modulator for generating three-phase switch positions.

    Attributes
    ----------
    ref_seq : SimpleNamespace
        Reference sequences for the control system. The sequences must be of class Sequence.
    data : SimpleNamespace
        Data storage for the control system.
    Ts : float
        Sampling interval [s].
    pwm : modulator, optional
        Modulator for generating three-phase switch positions.
    control_loops : list
        List of controller instances.
    """

    def __init__(self, control_loops, ref_seq, Ts, pwm=None):
        self.ref_seq = ref_seq
        self.data = SimpleNamespace(t=[], u_abc_ref=[])
        self.Ts = Ts

        # If PWM is provided, it is added to the control loops list to be the last loop of the
        # control system.
        if pwm is not None:
            control_loops = control_loops + [pwm]

        self.control_loops = control_loops
        self.pwm = pwm

        # Initialize the control loops with the given sampling interval
        for control_loop in self.control_loops:
            control_loop.set_sampling_interval(Ts)

    def __call__(self, sys, kTs):
        """
        Execute the control system for a given discrete time step. The control system
        1. Gets the references for the current time step.
        2. Executes the control loops in the order they appear in the list.
        3. Outputs a three-phase switch position and the corresponding switching times.  

        Parameters
        ----------
        sys : object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        u_abc : ndarray
            Three-phase switch position or modulating signal.
        """

        # Extract reference at step k from the sequence of references for the outmost control loop
        ctr_input = self.get_references(kTs)

        # Execute the control loops
        for control_loop in self.control_loops:
            control_loop.input = ctr_input
            ctr_output = control_loop.execute(sys, kTs)
            ctr_input = ctr_output
            control_loop.save_data()

        # Use the output of the innermost (i.e., last) loop of the control system as a feedforward
        # signal if PWM is not used. This can be the modulating signal or the three-phase switch
        # position (in the case of direct MPC). These are kept constant over the (control) sampling
        # interval.
        if self.pwm is None:
            self.save_data(kTs=kTs, u_abc_ref=np.copy(ctr_output.u_abc))
            ctr_output = SimpleNamespace(t_switch=0,
                                         switch_pos=ctr_output.u_abc)
        else:
            self.save_data(kTs=kTs, u_abc_ref=np.copy(self.pwm.input.u_abc))

        return ctr_output

    def get_references(self, kTs):
        """
        Get the references for the current time step. A new SimpleNamespace object is created and 
        the '_seq' subscript is removed from the attribute names.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        ref : SimpleNamespace
            References for the first control loop of the control system.  
        """

        ref = SimpleNamespace()
        for key, value in self.ref_seq.__dict__.items():
            if '_seq' in key:
                key = key.replace('_seq', '')
            setattr(ref, key, value(kTs))
        return ref

    def save_data(self, kTs, u_abc_ref):
        """
        Save the current time step to the control system data.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].
        u_abc_ref : 1 x 3 ndarray
            Three-phase switch position or modulating signal.
        """

        self.data.t.append(kTs)
        self.data.u_abc_ref.append(u_abc_ref)

    def get_control_system_data(self):
        """
        Fetch and save the data of the individual control loops. The data is saved with the name of 
        the control loop class.
        """

        for control_loop in self.control_loops:
            control_loop_name = control_loop.__class__.__name__
            setattr(self.data, control_loop_name, control_loop.data)
