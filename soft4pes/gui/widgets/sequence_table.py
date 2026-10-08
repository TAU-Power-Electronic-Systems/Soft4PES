"""A table widget for entering time-value sequences in the GUI."""

from PySide6 import QtWidgets

import math


class SequenceTable(QtWidgets.QWidget):
    """A table widget for entering time-value sequences in the Soft4PES GUI."""

    def __init__(
        self,
        title,
        default_times=None,
        default_values=None,
        parent=None,
    ):

        super().__init__(parent)
        # Initialize widget attributes to avoid pylint warnings about
        # assigning instance attributes outside __init__.
        self.table = None
        self.add_button = None
        self.remove_button = None

        self.title = title

        self.create_ui()

        if (default_times is not None and default_values is not None):
            self.set_data(
                default_times,
                default_values,
            )

    # ==================================================
    # UI
    # ==================================================

    def create_ui(self):
        """Create the user interface for the sequence table widget."""

        layout = QtWidgets.QVBoxLayout(self)

        # ----------------------------------------------
        # Title
        # ----------------------------------------------

        title_label = QtWidgets.QLabel(self.title)

        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            """)

        layout.addWidget(title_label)

        # ----------------------------------------------
        # Table
        # ----------------------------------------------

        self.table = QtWidgets.QTableWidget()

        self.table.setColumnCount(2)

        self.table.setHorizontalHeaderLabels([
            "Time [s]",
            "Value [p.u.]",
        ])

        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        # ----------------------------------------------
        # Buttons
        # ----------------------------------------------

        button_layout = QtWidgets.QHBoxLayout()

        self.add_button = QtWidgets.QPushButton("Add Row")

        self.remove_button = QtWidgets.QPushButton("Remove Row")

        button_layout.addWidget(self.add_button)

        button_layout.addWidget(self.remove_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Connections
        self.add_button.clicked.connect(self.add_row)

        self.remove_button.clicked.connect(self.remove_row)

    # ==================================================
    # Add row
    # ==================================================

    def add_row(self):

        row = self.table.rowCount()

        self.table.insertRow(row)

        self.table.setItem(
            row,
            0,
            QtWidgets.QTableWidgetItem("0.0"),
        )

        self.table.setItem(
            row,
            1,
            QtWidgets.QTableWidgetItem("0.0"),
        )

    # ==================================================
    # Remove row
    # ==================================================

    def remove_row(self):

        row = self.table.currentRow()

        if row >= 0:
            self.table.removeRow(row)

    # ==================================================
    # Set table values
    # ==================================================

    def set_data(
        self,
        times,
        values,
    ):

        self.table.setRowCount(0)

        for time, value in zip(
                times,
                values,
        ):

            row = self.table.rowCount()

            self.table.insertRow(row)

            self.table.setItem(
                row,
                0,
                QtWidgets.QTableWidgetItem(str(time)),
            )

            self.table.setItem(
                row,
                1,
                QtWidgets.QTableWidgetItem(str(value)),
            )

    # ==================================================
    # Read values
    # ==================================================

    def get_data(self):

        times = []
        values = []

        for row in range(self.table.rowCount()):

            time_item = self.table.item(
                row,
                0,
            )

            value_item = self.table.item(
                row,
                1,
            )

            if (time_item is None or value_item is None):
                raise ValueError(f"{self.title}: row {row + 1} is incomplete.")

            times.append(float(time_item.text()))

            values.append(float(value_item.text()))

        if not times:
            raise ValueError(f"{self.title}: add at least one reference row.")
        if not all(math.isfinite(v) for v in times + values):
            raise ValueError(f"{self.title}: times and values must be finite.")
        if times[0] != 0 or any(t < 0 for t in times):
            raise ValueError(
                f"{self.title}: start at zero and use nonnegative times.")
        if any(b < a for a, b in zip(times, times[1:])):
            raise ValueError(
                f"{self.title}: times must be nondecreasing (equal times create steps)."
            )
        return times, values
