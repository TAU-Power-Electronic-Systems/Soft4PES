from types import SimpleNamespace


class ControlSystem():

    def __init__(self, control_loops, ref):
        self.control_loops = control_loops
        self.ref = ref
        self.data = SimpleNamespace(t=[], ref=[])

    def get_control_system_data(self):
        for controller in self.control_loops:
            controller_name = controller.__class__.__name__
            setattr(self.data, controller_name, controller.data)

    def __call__(self, sys, conv, kTs):
        ctr_input = self.ref
        for controller in self.control_loops:
            controller.get_input(ctr_input)
            controller.execute(sys, conv, kTs)
            ctr_input = controller.get_output()

    def save_data(self, kTs):
        self.data.t.append(kTs)
        self.data.ref.append(self.ref)
