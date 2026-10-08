"""Main window for the Soft4PES GUI."""

from PySide6 import QtWidgets

try:
    from ..panels.grid_panel import GridPanel
    from ..panels.filter_panel import FilterPanel
    from ..panels.converter_panel import ConverterPanel
    from ..panels.controller_panel import ControllerPanel
    from ..panels.reference_panel import ReferencePanel
    from ..panels.simulation_panel import SimulationPanel
    from ..runners.runner_factory import RunnerFactory
    from ..results.results_panel import ResultsPanel
    from ..config.simulation_config import SimulationConfig
except ImportError:  # pragma: no cover - direct script execution fallback
    from panels.grid_panel import GridPanel
    from panels.filter_panel import FilterPanel
    from panels.converter_panel import ConverterPanel
    from panels.controller_panel import ControllerPanel
    from panels.reference_panel import ReferencePanel
    from panels.simulation_panel import SimulationPanel
    from runners.runner_factory import RunnerFactory
    from results.results_panel import ResultsPanel
    from config.simulation_config import SimulationConfig


class MainWindow(QtWidgets.QMainWindow):
    """Main window for the Soft4PES GUI."""

    def __init__(self):

        super().__init__()

        # Initialize widget attributes to avoid pylint warnings about
        # assigning instance attributes outside __init__.
        self.grid_panel = None
        self.filter_panel = None
        self.converter_panel = None
        self.controller_panel = None
        self.reference_panel = None
        self.simulation_panel = None
        self.results_panel = None
        self._loading_defaults = False

        self.setWindowTitle("Soft4PES Simulation Interface")

        self.resize(
            1200,
            800,
        )

        self.create_ui()

    # ======================================================
    # UI
    # ======================================================

    def create_ui(self):

        central_widget = (QtWidgets.QWidget())

        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        title = QtWidgets.QLabel("Soft4PES Simulation Interface")

        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
            }
            """)

        layout.addWidget(title)

        # --------------------------------------------------
        # Tabs
        # --------------------------------------------------

        self.tabs = QtWidgets.QTabWidget()

        layout.addWidget(self.tabs)

        # --------------------------------------------------
        # Panels
        # --------------------------------------------------

        self.grid_panel = GridPanel()

        self.filter_panel = FilterPanel()

        self.converter_panel = ConverterPanel()

        self.controller_panel = ControllerPanel()

        self.reference_panel = ReferencePanel()

        self.simulation_panel = SimulationPanel()

        self.results_panel = ResultsPanel()

        # --------------------------------------------------
        # Add tabs
        # --------------------------------------------------

        self.tabs.addTab(
            self.grid_panel,
            "Grid",
        )

        self.tabs.addTab(
            self.filter_panel,
            "Filter",
        )

        self.tabs.addTab(
            self.converter_panel,
            "Converter",
        )

        self.tabs.addTab(
            self.controller_panel,
            "Controller",
        )

        self.tabs.addTab(
            self.reference_panel,
            "References",
        )

        self.tabs.addTab(
            self.simulation_panel,
            "Simulation",
        )

        self.tabs.addTab(
            self.results_panel,
            "Results",
        )

        self.controller_panel.use_defaults.toggled.connect(
            self.update_default_parameters)
        self.controller_panel.controller_type.currentTextChanged.connect(
            self.update_default_parameters)
        self.filter_panel.filter_type.currentTextChanged.connect(
            self.update_default_parameters)
        self.controller_panel.use_defaults.setChecked(True)

        # --------------------------------------------------
        # Run button
        # --------------------------------------------------

        self.run_button = QtWidgets.QPushButton("Run Simulation")

        self.run_button.setMinimumHeight(45)

        layout.addWidget(self.run_button)

        self.run_button.clicked.connect(self.run_simulation)

    # ======================================================
    # Configuration
    # ======================================================

    def get_simulation_config(self):

        grid = self.grid_panel.get_parameters()

        filter_params = self.filter_panel.get_parameters()

        converter = self.converter_panel.get_parameters()

        controller = self.controller_panel.get_parameters()

        simulation = self.simulation_panel.get_parameters()

        return SimulationConfig(
            # Grid
            Vg=grid["Vg"],
            Ig=grid["Ig"],
            fg=grid["fg"],
            Rg=grid["Rg"],
            Lg=grid["Lg"],

            # Filter
            filter_type=filter_params["type"],
            Lfc=filter_params["Lfc"],
            Rfc=filter_params["Rfc"],
            Cf=filter_params["Cf"],
            Rc=filter_params["Rc"],
            Lfg=filter_params["Lfg"],
            Rfg=filter_params["Rfg"],

            # Converter
            Vdc=converter["Vdc"],
            converter_levels=converter["levels"],

            # Controller
            controller_type=controller["type"],
            fs_control=controller["fs"],
            Np=controller["Np"],
            lambda_u=controller["lambda_u"],
            I_conv_max=controller["I_conv_max"],

            # Simulation
            Ts_sim=simulation["Ts_sim"],
            t_stop=simulation["t_stop"],
        )

    # ======================================================
    # Run simulation
    # ======================================================

    def run_simulation(self):

        try:

            # ==================================================
            # Configuration
            # ==================================================

            config = self.get_simulation_config()

            references = self.reference_panel.get_references()

            # ==================================================
            # Select runner automatically
            # ==================================================

            runner = RunnerFactory.create(
                config=config,
                references=references,
            )

            # ==================================================
            # Run
            # ==================================================

            print("\nStarting Soft4PES simulation...")

            results = runner.run()

            print("Simulation completed successfully.")

            # ==================================================
            # Results
            # ==================================================

            self.results_panel.set_results(results)

            self.tabs.setCurrentWidget(self.results_panel)

            QtWidgets.QMessageBox.information(
                self,
                "Simulation",
                "Simulation completed successfully!",
            )

        except Exception as error:  # pylint: disable=broad-exception-caught

            print("Simulation error:")

            print(error)

            QtWidgets.QMessageBox.critical(
                self,
                "Simulation Error",
                str(error),
            )

    def update_default_parameters(self, *_):
        if self._loading_defaults:
            return
        checked = self.controller_panel.use_defaults.isChecked()
        controller = self.controller_panel.controller_type.currentText()
        self._loading_defaults = True
        try:
            if checked:
                if controller == "Grid Following - Linear":
                    index = 1 if self.filter_panel.filter_type.currentText(
                    ) == "LCL Filter" else 0
                else:
                    index = {
                        "Grid Forming - MPC": 2,
                        "Grid Forming - Cascade": 3,
                        "Direct MPC - Grid Current": 4
                    }[controller]
                self.load_example_preset(index)
            for panel in (self.grid_panel, self.converter_panel,
                          self.reference_panel, self.simulation_panel):
                panel.setEnabled(not checked)
            for box in self.filter_panel.findChildren(
                    QtWidgets.QDoubleSpinBox):
                box.setEnabled(not checked)
            self.filter_panel.filter_type.setEnabled(
                not checked or controller == "Grid Following - Linear")
            for box in (self.controller_panel.control_frequency,
                        self.controller_panel.Np,
                        self.controller_panel.lambda_u,
                        self.controller_panel.I_conv_max):
                box.setEnabled(not checked)
            if not checked:
                self.controller_panel.controller_changed(controller)
            self.reference_panel.V_table.setEnabled(
                not checked and controller.startswith("Grid Forming"))
            self.reference_panel.Q_table.setEnabled(
                not checked and not controller.startswith("Grid Forming"))
        finally:
            self._loading_defaults = False

    def load_example_preset(self, index):
        mv = index == 0
        lcl = index in (1, 2, 3)
        forming = index in (2, 3)
        grid = self.grid_panel
        for box, value in [(grid.voltage, 3300 if mv else 400),
                           (grid.current, 1575 if mv else 18),
                           (grid.frequency, 50),
                           (grid.resistance, .01815 if mv else .07),
                           (grid.inductance, .00057773 if mv else
                            (.03 if forming else .005))]:
            box.setValue(value)
        filt = self.filter_panel
        filt.filter_type.setCurrentText("LCL Filter" if lcl else "L Filter")
        if lcl:
            for name, value in [("Lfc", .003), ("Rfc", .1), ("Cf", 10e-6),
                                ("Rc", .001), ("Lfg", .003), ("Rfg", .1)]:
                getattr(filt, "LCL_" + name).setValue(value)
        else:
            filt.L_Lfc.setValue(.0005 if mv else .003)
            filt.L_Rfc.setValue(.1)
        self.converter_panel.dc_voltage.setValue(6200 if mv else 750)
        self.converter_panel.levels.setCurrentText(
            "2-Level" if lcl else "3-Level")
        ctr = self.controller_panel
        ctr.controller_type.setCurrentText([
            "Grid Following - Linear", "Grid Following - Linear",
            "Grid Forming - MPC", "Grid Forming - Cascade",
            "Direct MPC - Grid Current"
        ][index])
        ctr.control_frequency.setValue(10000)
        ctr.Np.setValue(4 if forming else 2)
        ctr.lambda_u.setValue(.01 if forming else .005)
        ctr.I_conv_max.setValue(1.3)
        stop = .3 if mv else (.2 if index == 4 else .4)
        self.simulation_panel.stop_time.setValue(stop)
        self.simulation_panel.simulation_step.setValue(5e-6 if index ==
                                                       4 else 1e-6)
        refs = self.reference_panel
        if forming:
            refs.P_table.set_data([0, .1, .1, .2, .2, .3, .3, .4],
                                  [0, 0, .5, .5, 1, 1, 0, 0])
        else:
            on, off = (.05, .15) if mv else ((.05, .1) if index == 4 else
                                             (.1, .2))
            refs.P_table.set_data([0, on, on, off, off, stop],
                                  [0, 0, 1, 1, 0, 0])
        qt = .25 if mv else (.15 if index == 4 else .3)
        refs.Q_table.set_data([0, qt, qt, stop], [
            0, 0, .5 if (mv or index == 4) else .3, .5 if
            (mv or index == 4) else .3
        ])
        refs.V_table.set_data([0, stop], [1, 1])
