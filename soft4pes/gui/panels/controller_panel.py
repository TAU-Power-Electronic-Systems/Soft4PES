"""Controller panel for Soft4PES GUI."""

from PySide6 import QtWidgets


class ControllerPanel(QtWidgets.QWidget):
    """Panel for configuring the controller parameters in the Soft4PES GUI."""

    def __init__(self):

        super().__init__()

        # Initialize widget attributes to avoid pylint warnings about
        # assigning instance attributes outside __init__.
        self.controller_type = None
        self.use_defaults = None
        self.control_frequency = None
        self.Np = None
        self.lambda_u = None
        self.I_conv_max = None

        self.create_ui()

    def create_ui(self):
        """Create the user interface for the controller panel."""

        layout = QtWidgets.QFormLayout(self)

        # ==================================================
        # Controller type
        # ==================================================

        self.controller_type = QtWidgets.QComboBox()

        self.controller_type.addItems([
            "Grid Following - Linear",
            "Grid Forming - MPC",
            "Grid Forming - Cascade",
            "Direct MPC - Grid Current",
        ])

        self.use_defaults = QtWidgets.QCheckBox(
            "Use default example parameters")
        self.use_defaults.setToolTip(
            "Load and lock the complete compatible example. Untick to edit parameters."
        )
        layout.addRow(self.use_defaults)

        # ==================================================
        # Sampling frequency
        # ==================================================

        self.control_frequency = QtWidgets.QDoubleSpinBox()

        self.control_frequency.setRange(
            1,
            1000000,
        )

        self.control_frequency.setValue(10000)

        self.control_frequency.setSuffix(" Hz")

        # ==================================================
        # Prediction horizon
        # ==================================================

        self.Np = QtWidgets.QSpinBox()

        self.Np.setRange(
            1,
            100,
        )

        self.Np.setValue(2)

        # ==================================================
        # lambda_u
        # ==================================================

        self.lambda_u = QtWidgets.QDoubleSpinBox()

        self.lambda_u.setDecimals(6)

        self.lambda_u.setRange(
            0,
            1000,
        )

        self.lambda_u.setValue(0.005)

        # ==================================================
        # Current limit
        # ==================================================

        self.I_conv_max = QtWidgets.QDoubleSpinBox()

        self.I_conv_max.setDecimals(3)

        self.I_conv_max.setRange(
            0,
            100,
        )

        self.I_conv_max.setValue(1.3)

        self.I_conv_max.setSuffix(" p.u.")

        # ==================================================
        # Layout
        # ==================================================

        layout.addRow(
            "Controller:",
            self.controller_type,
        )

        layout.addRow(
            "Control frequency:",
            self.control_frequency,
        )

        layout.addRow(
            "Prediction horizon:",
            self.Np,
        )

        layout.addRow(
            "Control penalty:",
            self.lambda_u,
        )

        layout.addRow(
            "Converter current limit:",
            self.I_conv_max,
        )

        self.controller_type.currentTextChanged.connect(
            self.controller_changed)

        self.controller_changed(self.controller_type.currentText())

    # ==================================================
    # Controller changed
    # ==================================================

    def controller_changed(
        self,
        controller,
    ):
        """Enable or disable parameters based on the selected controller type."""

        uses_mpc = "MPC" in controller

        self.Np.setEnabled(uses_mpc)

        self.lambda_u.setEnabled(uses_mpc)

        self.I_conv_max.setEnabled(controller in ("Grid Forming - MPC",
                                                  "Grid Forming - Cascade"))

    # ==================================================
    # Parameters
    # ==================================================

    def get_parameters(self):
        """Get the controller parameters from the panel."""

        return {
            "type": self.controller_type.currentText(),
            "fs": self.control_frequency.value(),
            "Np": self.Np.value(),
            "lambda_u": self.lambda_u.value(),
            "I_conv_max": self.I_conv_max.value(),
        }
