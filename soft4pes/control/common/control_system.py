"""
Control system class to manage and execute a set of control loops.
"""

from types import SimpleNamespace


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
        self.data = SimpleNamespace(t=[])
        self.Ts = Ts
        self.pwm = pwm
        self.control_loops = control_loops
        for control_loop in self.control_loops:
            control_loop.set_sampling_interval(Ts)

    def __call__(self, sys, kTs):
        """
        Execute the control system for a given discrete time step. The control system
        1. Gets the references for the current time step.
        2. Executes the control loops in the order they appear in the list.
        3. Generates the three-phase switch position if modulator is used.

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
            ctr_input = control_loop.execute(sys, kTs)
            control_loop.save_data()

        self.save_data(kTs=kTs)

        # Form the three-phase switch position if PWM is used, otherwise use the output of the inner
        # (i.e., last) loop as a feedforward signal
        if self.pwm is not None:
            u_abc = self.pwm(ctr_input)
        else:
            u_abc = ctr_input.u_abc
        return u_abc

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

    def save_data(self, kTs):
        """
        Save the current time step to the control system data.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].
        """

        self.data.t.append(kTs)

    def get_control_system_data(self):
        """
        Fetch and save the data of the individual control loops. The data is saved with the name of 
        the control loop class.
        """

        for control_loop in self.control_loops:
            control_loop_name = control_loop.__class__.__name__
            setattr(self.data, control_loop_name, control_loop.data)
