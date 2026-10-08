"""Set up the grid panel for the GUI."""

from PySide6 import QtWidgets


class GridPanel(QtWidgets.QWidget):
    """Panel for configuring the grid parameters in the Soft4PES GUI."""

    def __init__(self):

        super().__init__()

        # Initialize widget attributes to avoid pylint warnings about
        # assigning instance attributes outside __init__.
        self.voltage = None
        self.current = None
        self.frequency = None
        self.resistance = None
        self.inductance = None

        self.create_ui()

    def create_ui(self):
        """Create the user interface for the grid panel."""

        layout = QtWidgets.QFormLayout(self)

        # ------------------------------------------
        # Grid voltage
        # ------------------------------------------

        self.voltage = QtWidgets.QDoubleSpinBox()

        self.voltage.setRange(
            0,
            100000,
        )

        self.voltage.setValue(3300)

        self.voltage.setSuffix(" V")

        # ------------------------------------------
        # Rated grid current
        # ------------------------------------------

        self.current = QtWidgets.QDoubleSpinBox()

        self.current.setRange(0, 100000)

        self.current.setValue(1575)

        self.current.setSuffix(" A")

        # ------------------------------------------
        # Frequency
        # ------------------------------------------

        self.frequency = QtWidgets.QDoubleSpinBox()

        self.frequency.setRange(1, 400)

        self.frequency.setValue(50)

        self.frequency.setSuffix(" Hz")

        # ------------------------------------------
        # Grid resistance
        # ------------------------------------------

        self.resistance = QtWidgets.QDoubleSpinBox()

        self.resistance.setDecimals(6)

        self.resistance.setRange(0, 100)

        self.resistance.setValue(0.01815)

        self.resistance.setSuffix(" Ohm")

        # ------------------------------------------
        # Grid inductance
        # ------------------------------------------

        self.inductance = QtWidgets.QDoubleSpinBox()

        self.inductance.setDecimals(8)

        self.inductance.setRange(0, 10)

        self.inductance.setValue(0.00057773)

        self.inductance.setSuffix(" H")

        # ------------------------------------------
        # Layout
        # ------------------------------------------

        layout.addRow(
            "Rated grid voltage:",
            self.voltage,
        )

        layout.addRow(
            "Rated grid current:",
            self.current,
        )

        layout.addRow(
            "Grid frequency:",
            self.frequency,
        )

        layout.addRow(
            "Grid resistance:",
            self.resistance,
        )

        layout.addRow(
            "Grid inductance:",
            self.inductance,
        )

    def get_parameters(self):

        return {
            "Vg": self.voltage.value(),
            "Ig": self.current.value(),
            "fg": self.frequency.value(),
            "Rg": self.resistance.value(),
            "Lg": self.inductance.value(),
        }
