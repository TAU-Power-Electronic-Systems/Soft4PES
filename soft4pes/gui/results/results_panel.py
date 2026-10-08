"""Results panel for the GUI."""

import numpy as np

from PySide6 import QtWidgets

from soft4pes.utils import (
    alpha_beta_2_abc,
    alpha_beta_2_dq,
    dq_2_alpha_beta,
)

try:
    from ..results.plot_canvas import PlotCanvas
except ImportError:  # pragma: no cover - direct script execution fallback
    from results.plot_canvas import PlotCanvas


class ResultsPanel(QtWidgets.QWidget):
    """Panel for displaying simulation results in the Soft4PES GUI."""

    def __init__(self):

        super().__init__()

        # Initialize widget attributes to avoid pylint warnings about
        # assigning instance attributes outside __init__.
        self.plot_canvas = None
        self.result_selector = None
        self.results = None

        self.create_ui()

    # ======================================================
    # UI
    # ======================================================

    def create_ui(self):
        """Create the user interface for the results panel."""

        layout = QtWidgets.QVBoxLayout(self)

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        title = QtWidgets.QLabel("Simulation Results")

        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            """)

        layout.addWidget(title)

        # --------------------------------------------------
        # Plot selection
        # --------------------------------------------------

        top_layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("Plot:")

        self.result_selector = QtWidgets.QComboBox()

        self.result_selector.addItems([
            "Grid current abc",
            "Grid current dq",
            "Active & Reactive Power",
        ])

        self.result_selector.currentTextChanged.connect(self.update_plot)

        top_layout.addWidget(label)

        top_layout.addWidget(self.result_selector)

        top_layout.addStretch()

        layout.addLayout(top_layout)

        # --------------------------------------------------
        # Plot canvas
        # --------------------------------------------------

        self.plot_canvas = PlotCanvas(self)

        layout.addWidget(self.plot_canvas)

    # ======================================================
    # Receive simulation results
    # ======================================================

    def set_results(
        self,
        results,
    ):
        """Set the simulation results to be displayed in the panel."""

        self.results = results

        previous = self.result_selector.currentText()
        choices = [
            "Grid current abc", "Grid current dq", "Active & Reactive Power",
            "Converter command uc abc", "Converter voltage abc"
        ]
        if "vc" in results["sys"].state_map:
            choices += [
                "Capacitor voltage abc", "Capacitor voltage dq",
                "Capacitor voltage magnitude"
            ]
        self.result_selector.blockSignals(True)
        self.result_selector.clear()
        self.result_selector.addItems(choices)
        if previous in choices:
            self.result_selector.setCurrentText(previous)
        self.result_selector.blockSignals(False)
        self.update_plot()

    # ======================================================
    # Select plot
    # ======================================================

    def update_plot(self):
        """Update the plot based on the selected result type."""

        if self.results is None:
            return

        selection = self.result_selector.currentText()

        if selection == "Grid current abc":

            self.plot_grid_current_abc()

        elif selection == "Grid current dq":

            self.plot_grid_current_dq()

        elif selection == "Active & Reactive Power":

            self.plot_power()
        elif selection == "Converter command uc abc":
            self.plot_converter_command()
        elif selection == "Converter voltage abc":
            self.plot_converter_voltage()
        elif selection.startswith("Capacitor voltage"):
            self.plot_capacitor_voltage(selection)

    # ======================================================
    # Grid current abc
    # ======================================================

    def plot_grid_current_abc(self):

        sim_data = self.results["sim_data"]
        sys = self.results["sys"]

        # --------------------------------------------------
        # Get time and states
        # --------------------------------------------------

        t = sim_data.sys.t

        x = sim_data.sys.x

        # --------------------------------------------------
        # Extract ig alpha-beta
        # --------------------------------------------------

        ig_alpha_beta = x[:, sys.state_map["ig"]]

        # --------------------------------------------------
        # Convert alpha-beta to abc
        # --------------------------------------------------

        ig_abc = np.array(
            [alpha_beta_2_abc(current) for current in ig_alpha_beta])

        # --------------------------------------------------
        # Plot
        # --------------------------------------------------

        ax = self.plot_canvas.axes

        ax.clear()

        ax.plot(
            t,
            ig_abc[:, 0],
            label=r"$i_{g,a}$",
        )

        ax.plot(
            t,
            ig_abc[:, 1],
            label=r"$i_{g,b}$",
        )

        ax.plot(
            t,
            ig_abc[:, 2],
            label=r"$i_{g,c}$",
        )

        ax.set_xlabel("Time [s]")

        ax.set_ylabel(r"$i_g$ [p.u.]")

        ax.set_title("Grid Current - abc Frame")

        ax.grid(True)

        ax.legend()

        self.plot_canvas.refresh()

    # ======================================================
    # Grid current dq
    # ======================================================

    def plot_grid_current_dq(self):

        sim_data = self.results["sim_data"]
        sys = self.results["sys"]

        # --------------------------------------------------
        # System data
        # --------------------------------------------------

        t_sys = sim_data.sys.t

        x = sim_data.sys.x

        ig_alpha_beta = x[:, sys.state_map["ig"]]

        # --------------------------------------------------
        # Controller data
        # --------------------------------------------------

        t_control = sim_data.ctr.t

        theta = (sim_data.ctr.PLL.output.theta
                 if hasattr(sim_data.ctr, "PLL") else np.arctan2(
                     np.interp(t_control, t_sys, sim_data.sys.vg[:, 1]),
                     np.interp(t_control, t_sys, sim_data.sys.vg[:, 0]),
                 ))

        # --------------------------------------------------
        # Interpolate alpha-beta current
        # to controller time
        # --------------------------------------------------

        ig_alpha = np.interp(
            t_control,
            t_sys,
            ig_alpha_beta[:, 0],
        )

        ig_beta = np.interp(
            t_control,
            t_sys,
            ig_alpha_beta[:, 1],
        )

        ig_control = np.column_stack((
            ig_alpha,
            ig_beta,
        ))

        # --------------------------------------------------
        # alpha-beta -> dq
        # --------------------------------------------------

        ig_dq = np.array([
            alpha_beta_2_dq(
                current,
                angle,
            ) for current, angle in zip(
                ig_control,
                theta,
            )
        ])

        # --------------------------------------------------
        # Plot
        # --------------------------------------------------

        ax = self.plot_canvas.axes

        ax.clear()

        ax.plot(
            t_control,
            ig_dq[:, 0],
            label=r"$i_{g,d}$",
        )

        ax.plot(
            t_control,
            ig_dq[:, 1],
            label=r"$i_{g,q}$",
        )

        ax.set_xlabel("Time [s]")

        ax.set_ylabel(r"$i_g$ [p.u.]")

        ax.set_title("Grid Current - dq Frame")

        ax.grid(True)

        ax.legend()

        self.plot_canvas.refresh()

    # ======================================================
    # Active and reactive power
    # ======================================================

    def plot_power(self):

        sim_data = self.results["sim_data"]
        sys = self.results["sys"]

        P_ref_seq = (self.results["P_ref_seq"])

        Q_ref_seq = (self.results.get("Q_ref_seq"))

        # --------------------------------------------------
        # System data
        # --------------------------------------------------

        t = sim_data.sys.t

        x = sim_data.sys.x

        vg = sim_data.sys.vg

        # --------------------------------------------------
        # Grid current
        # --------------------------------------------------

        ig = x[:, sys.state_map["ig"]]

        # --------------------------------------------------
        # Power calculation
        # --------------------------------------------------

        P = (vg[:, 0] * ig[:, 0] + vg[:, 1] * ig[:, 1])

        Q = (vg[:, 1] * ig[:, 0] - vg[:, 0] * ig[:, 1])

        # --------------------------------------------------
        # Plot
        # --------------------------------------------------

        ax = self.plot_canvas.axes

        ax.clear()

        ax.plot(
            t,
            P,
            label=r"$P$",
        )

        ax.plot(
            t,
            Q,
            label=r"$Q$",
        )

        # --------------------------------------------------
        # Reference signals
        # --------------------------------------------------

        ax.plot(
            P_ref_seq.times,
            P_ref_seq.values,
            "--",
            label=r"$P_{\mathrm{ref}}$",
        )

        if Q_ref_seq is not None:
            ax.plot(
                Q_ref_seq.times,
                Q_ref_seq.values,
                "--",
                label=r"$Q_{\mathrm{ref}}$",
            )

        # --------------------------------------------------
        # Formatting
        # --------------------------------------------------

        ax.set_xlabel("Time [s]")

        ax.set_ylabel("Power [p.u.]")

        ax.set_title("Active and Reactive Power")

        ax.grid(True)

        ax.legend()

        self.plot_canvas.refresh()

    def finish_voltage_plot(self, title, ylabel):
        ax = self.plot_canvas.axes
        ax.set_xlabel("Time [s]")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True)
        ax.legend()
        self.plot_canvas.refresh()

    def plot_converter_command(self):
        data = self.results["sim_data"]
        ax = self.plot_canvas.axes
        ax.clear()
        for j, phase in enumerate("abc"):
            ax.plot(data.ctr.t, data.ctr.u_abc_ref[:, j], label=f"uc_{phase}")
        self.finish_voltage_plot(
            "Converter command (modulation / direct MPC switch command)",
            "Normalized command [-]")

    def plot_converter_voltage(self):
        data = self.results["sim_data"]
        vdc = self.results["sys"].conv.v_dc
        ax = self.plot_canvas.axes
        ax.clear()
        # Remove common-mode voltage to obtain converter phase-to-neutral voltage.
        actual = .5 * vdc * (data.sys.u_abc -
                             data.sys.u_abc.mean(axis=1, keepdims=True))
        command = .5 * vdc * (data.ctr.u_abc_ref -
                              data.ctr.u_abc_ref.mean(axis=1, keepdims=True))
        for j, phase in enumerate("abc"):
            line, = ax.plot(data.sys.t, actual[:, j], label=f"v_conv,{phase}")
            ax.plot(data.ctr.t,
                    command[:, j],
                    "--",
                    color=line.get_color(),
                    label=f"v_conv,{phase} command")
        self.finish_voltage_plot("Converter phase voltage and command",
                                 "Voltage [p.u.]")

    def plot_capacitor_voltage(self, selection):
        data = self.results["sim_data"]
        sys = self.results["sys"]
        vc = data.sys.x[:, sys.state_map["vc"]]
        ax = self.plot_canvas.axes
        ax.clear()
        t = data.ctr.t
        vg = np.array([sys.get_grid_voltage(time) for time in t])
        theta = np.arctan2(vg[:, 1], vg[:, 0])
        measured = np.column_stack(
            [np.interp(t, data.sys.t, vc[:, j]) for j in range(2)])
        dq = np.array(
            [alpha_beta_2_dq(v, th) for v, th in zip(measured, theta)])
        ref = (data.ctr.RFPSC.output.vc_ref_dq
               if hasattr(data.ctr, "RFPSC") else None)
        if selection.endswith("dq"):
            for j, axis in enumerate("dq"):
                line, = ax.plot(t, dq[:, j], label=f"vc_{axis}")
                if ref is not None:
                    ax.plot(t,
                            ref[:, j],
                            "--",
                            color=line.get_color(),
                            label=f"vc_{axis} ref")
            title = "Capacitor voltage tracking (grid-oriented dq)"
        elif selection.endswith("abc"):
            abc = np.array([alpha_beta_2_abc(v) for v in vc])
            if ref is not None:
                ref_abc = np.array([
                    alpha_beta_2_abc(dq_2_alpha_beta(v, th))
                    for v, th in zip(ref, theta)
                ])
            for j, phase in enumerate("abc"):
                line, = ax.plot(data.sys.t, abc[:, j], label=f"vc_{phase}")
                if ref is not None:
                    ax.plot(t,
                            ref_abc[:, j],
                            "--",
                            color=line.get_color(),
                            label=f"vc_{phase} ref")
            title = "Capacitor phase voltage tracking"
        else:
            ax.plot(data.sys.t, np.linalg.norm(vc, axis=1), label="|vc|")
            if ref is not None:
                ax.plot(t,
                        np.linalg.norm(ref, axis=1),
                        "--",
                        label="|vc inner reference|")
            outer = self.results.get("V_ref_seq")
            if outer is not None:
                ax.plot(t, [outer(time) for time in t],
                        ":",
                        label="V outer reference")
            title = "Capacitor voltage magnitude"
        self.finish_voltage_plot(title, "Voltage [p.u.]")
