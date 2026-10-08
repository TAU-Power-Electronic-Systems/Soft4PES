"""Settings panel for the filter parameters."""

from PySide6 import QtWidgets


class FilterPanel(QtWidgets.QWidget):
    """Panel for configuring the filter parameters in the Soft4PES GUI."""

    def __init__(self):

        super().__init__()

        # Initialize widget attributes to avoid pylint warnings about
        # assigning instance attributes outside __init__.
        self.filter_type = None
        self.stack = None
        self.L_Lfc = None
        self.L_Rfc = None
        self.LCL_Lfc = None
        self.LCL_Rfc = None
        self.LCL_Cf = None
        self.LCL_Rc = None
        self.LCL_Lfg = None
        self.LCL_Rfg = None

        self.create_ui()

    # ==================================================
    # UI
    # ==================================================

    def create_ui(self):
        """Create the user interface for the filter panel."""

        main_layout = QtWidgets.QVBoxLayout(self)

        # --------------------------------------------------
        # Filter selector
        # --------------------------------------------------

        selector_layout = QtWidgets.QFormLayout()

        self.filter_type = QtWidgets.QComboBox()

        self.filter_type.addItems([
            "L Filter",
            "LCL Filter",
        ])

        selector_layout.addRow(
            "Filter type:",
            self.filter_type,
        )

        main_layout.addLayout(selector_layout)

        # --------------------------------------------------
        # Stack
        # --------------------------------------------------

        self.stack = QtWidgets.QStackedWidget()

        main_layout.addWidget(self.stack)

        # L filter page
        self.create_l_filter_page()

        # LCL filter page
        self.create_lcl_filter_page()

        # --------------------------------------------------
        # Connection
        # --------------------------------------------------

        self.filter_type.currentIndexChanged.connect(
            self.stack.setCurrentIndex)

    # ==================================================
    # L filter
    # ==================================================

    def create_l_filter_page(self):
        """Create the page for configuring L filter parameters."""

        page = QtWidgets.QWidget()

        layout = QtWidgets.QFormLayout(page)

        self.L_Lfc = self.create_spinbox(
            value=0.0005,
            decimals=8,
            suffix=" H",
        )

        self.L_Rfc = self.create_spinbox(
            value=0.1,
            decimals=6,
            suffix=" Ohm",
        )

        layout.addRow(
            "Converter-side inductance:",
            self.L_Lfc,
        )

        layout.addRow(
            "Converter-side resistance:",
            self.L_Rfc,
        )

        self.stack.addWidget(page)

    # ==================================================
    # LCL filter
    # ==================================================

    def create_lcl_filter_page(self):
        """Create the page for configuring LCL filter parameters."""

        page = QtWidgets.QWidget()

        layout = QtWidgets.QFormLayout(page)

        self.LCL_Lfc = self.create_spinbox(
            value=0.003,
            decimals=8,
            suffix=" H",
        )

        self.LCL_Rfc = self.create_spinbox(
            value=0.1,
            decimals=6,
            suffix=" Ohm",
        )

        self.LCL_Cf = self.create_spinbox(
            value=10e-6,
            decimals=9,
            suffix=" F",
        )

        self.LCL_Rc = self.create_spinbox(
            value=1e-3,
            decimals=8,
            suffix=" Ohm",
        )

        self.LCL_Lfg = self.create_spinbox(
            value=0.003,
            decimals=8,
            suffix=" H",
        )

        self.LCL_Rfg = self.create_spinbox(
            value=0.1,
            decimals=6,
            suffix=" Ohm",
        )

        layout.addRow(
            "Converter-side inductance:",
            self.LCL_Lfc,
        )

        layout.addRow(
            "Converter-side resistance:",
            self.LCL_Rfc,
        )

        layout.addRow(
            "Filter capacitance:",
            self.LCL_Cf,
        )

        layout.addRow(
            "Capacitor resistance:",
            self.LCL_Rc,
        )

        layout.addRow(
            "Grid-side inductance:",
            self.LCL_Lfg,
        )

        layout.addRow(
            "Grid-side resistance:",
            self.LCL_Rfg,
        )

        self.stack.addWidget(page)

    # ==================================================
    # Helper
    # ==================================================

    def create_spinbox(
        self,
        value,
        decimals,
        suffix,
    ):
        """Create a QDoubleSpinBox with specified properties."""

        box = QtWidgets.QDoubleSpinBox()

        box.setDecimals(decimals)

        box.setRange(
            0.0,
            100000.0,
        )

        box.setValue(value)

        box.setSuffix(suffix)

        return box

    # ==================================================
    # Parameters
    # ==================================================

    def get_parameters(self):
        """Get the filter parameters from the panel."""

        filter_type = self.filter_type.currentText()

        if filter_type == "L Filter":

            return {
                "type": filter_type,
                "Lfc": self.L_Lfc.value(),
                "Rfc": self.L_Rfc.value(),
                "Cf": 0.0,
                "Rc": 0.0,
                "Lfg": 0.0,
                "Rfg": 0.0,
            }

        return {
            "type": filter_type,
            "Lfc": self.LCL_Lfc.value(),
            "Rfc": self.LCL_Rfc.value(),
            "Cf": self.LCL_Cf.value(),
            "Rc": self.LCL_Rc.value(),
            "Lfg": self.LCL_Lfg.value(),
            "Rfg": self.LCL_Rfg.value(),
        }
