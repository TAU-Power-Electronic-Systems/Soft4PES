"""Set up the reference panel for the GUI."""

from PySide6 import QtWidgets

try:
    from ..widgets.sequence_table import SequenceTable
    from ..config.reference_config import ReferenceConfig, SequenceConfig
except ImportError:  # pragma: no cover - direct script execution fallback
    from widgets.sequence_table import SequenceTable
    from config.reference_config import ReferenceConfig, SequenceConfig


class ReferencePanel(QtWidgets.QWidget):
    """Panel for configuring the reference signals in the Soft4PES GUI."""

    def __init__(self):

        super().__init__()

        # Initialize widget attributes to avoid pylint warnings about
        # assigning instance attributes outside __init__.
        self.P_table = None
        self.Q_table = None
        self.V_table = None

        self.create_ui()

    # ==================================================
    # UI
    # ==================================================

    def create_ui(self):
        """Create the user interface for the reference panel."""

        main_layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("Reference Signals")

        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            """)

        main_layout.addWidget(title)

        # --------------------------------------------------
        # Reference tables
        # --------------------------------------------------

        tables_layout = QtWidgets.QHBoxLayout()

        # --------------------------------------------------
        # P reference
        # --------------------------------------------------

        self.P_table = SequenceTable(
            title="Active Power Reference",
            default_times=[
                0.0,
                0.05,
                0.05,
                0.15,
                0.15,
                0.30,
            ],
            default_values=[
                0.0,
                0.0,
                1.0,
                1.0,
                0.0,
                0.0,
            ],
        )

        # --------------------------------------------------
        # Q reference
        # --------------------------------------------------

        self.Q_table = SequenceTable(
            title="Reactive Power Reference",
            default_times=[
                0.0,
                0.25,
                0.25,
                0.30,
            ],
            default_values=[
                0.0,
                0.0,
                0.5,
                0.5,
            ],
        )

        # --------------------------------------------------
        # Voltage reference
        # --------------------------------------------------

        self.V_table = SequenceTable(
            title="Voltage Magnitude Reference",
            default_times=[
                0.0,
                0.4,
            ],
            default_values=[
                1.0,
                1.0,
            ],
        )

        tables_layout.addWidget(self.P_table)

        tables_layout.addWidget(self.Q_table)

        tables_layout.addWidget(self.V_table)

        main_layout.addLayout(tables_layout)

    # ==================================================
    # Get references
    # ==================================================

    def get_references(self):
        """Get the reference signals from the panel."""

        P_times, P_values = self.P_table.get_data()

        Q_times, Q_values = self.Q_table.get_data()

        V_times, V_values = self.V_table.get_data()

        return ReferenceConfig(
            P=SequenceConfig(
                times=P_times,
                values=P_values,
            ),
            Q=SequenceConfig(
                times=Q_times,
                values=Q_values,
            ),
            V=SequenceConfig(
                times=V_times,
                values=V_values,
            ),
        )
