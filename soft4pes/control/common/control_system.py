"""
Control system class to manage and execute a set of controllers.
"""

from types import SimpleNamespace


class ControlSystem:
    """
    ControlSystem class to manage and execute a set of controllers. The class accepts any number of 
    controllers and combines them to complete control system.

    Parameters
    ----------
    controllers : list
        List of controller instances. The controllers are executed in the order they appear in the
        list. 
    ref_seq : SimpleNamespace
        Reference sequences for the control system. The sequences must be of class Sequence. The 
        references are given to the first controller in the list.
    Ts : float
        Sampling interval [s].
    pwm : modulator, optional
        Modulator for generating three-phase switch positions.

    Attributes
    ----------
    ref_seq : SimpleNamespace
        Reference sequences for the controllers. The sequences must be of class Sequence.
    data : SimpleNamespace
        Data storage for the control system.
    Ts : float
        Sampling interval [s].
    pwm : modulator, optional
        Modulator for generating three-phase switch positions.
    controllers : list
        List of controller instances.
    """

    def __init__(self, controllers, ref_seq, Ts, pwm=None):
        self.ref_seq = ref_seq
        self.data = SimpleNamespace(t=[])
        self.Ts = Ts
        self.pwm = pwm
        self.controllers = controllers
        for controller in self.controllers:
            controller.set_sampling_interval(Ts)

    def __call__(self, sys, conv, kTs):
        """
        Execute the control system for a given discrete time step. The control system
        1. Gets the references for the current time step.
        2. Executes the controllers in the order they appear in the list.
        3. Generates the three-phase switch position if modulator is used.

        Parameters
        ----------
        sys : object
            System model.
        conv : object
            Converter model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        uk_abc : ndarray
            Three-phase switch position or modulating signals.
        """

        # Get the references on step k from the sequences
        ctr_input = self.get_references(kTs)

        # Execute the controllers
        for controller in self.controllers:
            controller.input = ctr_input
            ctr_input = controller.execute(sys, conv, kTs)
            controller.save_data()

        self.save_data(kTs=kTs)

        # Form the three-phase switch position if PWM is used, otherwise use feedforward the
        # output of the last controller
        if self.pwm is not None:
            uk_abc = self.pwm(ctr_input)
        else:
            uk_abc = ctr_input.uk_abc
        return uk_abc

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
            Reference sequences for the control system. The sequences must be of class Sequence. 
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
        Fetch and save the data of the individual controllers. The data is saved with the name of 
        the controller class.
        """

        for controller in self.controllers:
            controller_name = controller.__class__.__name__
            setattr(self.data, controller_name, controller.data)
