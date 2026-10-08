"""set up the converter panel in the GUI."""

from PySide6 import QtWidgets


class ConverterPanel(QtWidgets.QWidget):
    """Panel for configuring the converter parameters in the Soft4PES GUI."""

    def __init__(self):

        super().__init__()

        # Initialize widget attributes to avoid pylint warnings about
        # assigning instance attributes outside __init__.
        self.dc_voltage = None
        self.levels = None

        self.create_ui()

    def create_ui(self):
        """Create the user interface for the converter panel."""

        layout = QtWidgets.QFormLayout(self)

        self.dc_voltage = QtWidgets.QDoubleSpinBox()

        self.dc_voltage.setRange(0, 50000)

        self.dc_voltage.setValue(6200)

        self.dc_voltage.setSuffix(" V")

        self.levels = QtWidgets.QComboBox()

        self.levels.addItems([
            "2-Level",
            "3-Level",
        ])

        self.levels.setCurrentText("3-Level")

        layout.addRow(
            "DC-link voltage:",
            self.dc_voltage,
        )

        layout.addRow(
            "Converter topology:",
            self.levels,
        )

    def get_parameters(self):
        """Get the converter parameters from the panel."""

        levels_text = self.levels.currentText()

        if levels_text == "2-Level":
            levels = 2

        else:
            levels = 3

        return {
            "Vdc": self.dc_voltage.value(),
            "levels": levels,
        }
