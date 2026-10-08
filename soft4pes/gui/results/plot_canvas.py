"""Settings for the plot canvas used in the GUI."""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvasQTAgg):
    """Canvas for plotting results in the Soft4PES GUI."""

    def __init__(self, parent=None):

        self.figure = Figure(figsize=(8, 5))

        self.axes = self.figure.add_subplot(111)

        super().__init__(self.figure)

        self.setParent(parent)

    def clear(self):

        self.axes.clear()

    def refresh(self):

        self.figure.tight_layout()

        self.draw()
