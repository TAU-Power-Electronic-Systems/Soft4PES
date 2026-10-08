"""Set up the simulation panel for the GUI."""

from PySide6 import QtWidgets


class SimulationPanel(QtWidgets.QWidget):
    """Panel for configuring the simulation parameters in the Soft4PES GUI."""

    def __init__(self):

        super().__init__()

        # Initialize widget attributes to avoid pylint warnings about
        # assigning instance attributes outside __init__.
        self.stop_time = None
        self.simulation_step = None

        self.create_ui()

    def create_ui(self):
        """Create the user interface for the simulation panel."""

        layout = QtWidgets.QFormLayout(self)

        self.stop_time = QtWidgets.QDoubleSpinBox()

        self.stop_time.setDecimals(4)

        self.stop_time.setRange(0.001, 1000)

        self.stop_time.setValue(0.3)

        self.stop_time.setSuffix(" s")

        self.simulation_step = QtWidgets.QDoubleSpinBox()

        self.simulation_step.setDecimals(8)

        self.simulation_step.setRange(1e-8, 1)

        self.simulation_step.setValue(1e-6)

        self.simulation_step.setSuffix(" s")

        layout.addRow(
            "Stop time:",
            self.stop_time,
        )

        layout.addRow(
            "Simulation step:",
            self.simulation_step,
        )

    def get_parameters(self):
        """Get the simulation parameters from the panel."""

        return {
            "t_stop": self.stop_time.value(),
            "Ts_sim": self.simulation_step.value(),
        }
