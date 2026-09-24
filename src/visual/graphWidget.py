from enum import IntEnum, auto

from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np
import pyqtgraph.opengl as gl
from math import sqrt, pi

from ..compui.grap_widget import Ui_graphWidget
from ..data import Data


class GraphType(IntEnum):
    SCATTER = auto()
    PARALLEL = auto()
    HEATMAP = auto()
    BUBBLE = auto()
    CORRFIELD = auto()
    DIAGNOSTIC = auto()


class GraphWidget(QWidget):
    def __init__(self, gtype: GraphType, data: Data):
        super().__init__()
        self.ui = Ui_graphWidget()
        self.ui.setupUi(self)

        layout = QVBoxLayout(self.ui.graph)
        widget = None
        layout.setContentsMargins(0, 0, 0, 0)

        if gtype == GraphType.SCATTER:
            self.setWindowTitle("Scatter Matrix")
            widget = self._build_scatter_matrix(data)

        elif gtype == GraphType.PARALLEL:
            self.setWindowTitle("Parallel Coordinates")
            widget = self._build_parallel_coords(data)

        elif gtype == GraphType.HEATMAP:
            self.setWindowTitle("Heatmap")
            widget = self._build_heatmap(data)

        elif gtype == GraphType.BUBBLE:
            self.setWindowTitle("Bubble Diagram")
            widget = self._build_bubble(data)

        elif gtype == GraphType.CORRFIELD:
            self.setWindowTitle("Correlation Field")
            widget = self._build_correlation_field(data)

        elif gtype == GraphType.DIAGNOSTIC:
            self.setWindowTitle("Diagnostic Diagram")
            widget = self._build_diagnostic_diagram(data)

        if widget is not None:
            layout.addWidget(widget)

    def _build_bubble(self, data: Data) -> QWidget:
        cols = data.cols
        if len(cols) < 3:
            raise ValueError("Not enough experiments (dimensions)")

        x = cols[0]
        y = cols[1]
        z = cols[2]

        mn, mx = min(z), max(z)
        max_px = 40.0

        def radius(val):
            s = (val - mn) / (mx - mn) if mx != mn else 0.0
            return max_px * sqrt(s / pi)

        glw = pg.GraphicsLayoutWidget()
        plot = glw.addPlot()

        sizes = [radius(v) for v in z]

        scatter = pg.ScatterPlotItem(
            x=x,
            y=y,
            size=sizes,
            brush=pg.mkBrush(100, 160, 220, 160),
            pen=pg.mkPen(None),
        )
        plot.addItem(scatter)

        return glw

    def _build_heatmap(self, data: Data) -> QWidget:
        cols = data.cols
        p = data.dimensions
        n = data.vector_length

        normalized = []
        for col in cols:
            mn, mx = min(col), max(col)
            if mx != mn:
                normalized.append([(v - mn) / (mx - mn) for v in col])
            else:
                normalized.append([0.0] * n)

        grid = np.array([[normalized[j][i] for j in range(p)] for i in range(n)])

        glw = pg.GraphicsLayoutWidget()
        plot = glw.addPlot()
        plot.hideAxis("left")
        plot.hideAxis("bottom")
        plot.setDefaultPadding(0)

        img = pg.ImageItem()
        colormap = pg.ColorMap(
            pos=[0.0, 1.0], color=[(240, 248, 255, 255), (30, 80, 160, 255)]
        )
        img.setColorMap(colormap)
        img.setImage(grid.T)
        img.setRect(0, 0, p, n)
        plot.addItem(img)
        plot.setXRange(0, p, padding=0)
        plot.setYRange(0, n, padding=0)

        for j in range(p):
            label = pg.TextItem(text=f"X{j + 1}", anchor=(0.5, 1.0), color="#aaaaaa")
            label.setPos(j + 0.5, 0)
            plot.addItem(label)

        return glw

    def _build_scatter_matrix(self, data: Data) -> QWidget:
        cols = data.cols
        corr = data.correlation_matrix
        p = data.dimensions

        glw = pg.GraphicsLayoutWidget()

        for row in range(p):
            for col in range(p):
                plot = glw.addPlot(row=row, col=col)
                plot.hideAxis("left")
                plot.hideAxis("bottom")

                if row == col:
                    self._draw_histogram(plot, cols[row])
                elif row > col:
                    self._draw_scatter(plot, cols[col], cols[row])
                else:
                    self._draw_corr_text(plot, corr[row][col])

        return glw

    def _build_parallel_coords(self, data: Data) -> QWidget:
        cols = data.cols
        p = data.dimensions
        n = data.vector_length

        mins = [min(c) for c in cols]
        maxs = [max(c) for c in cols]

        def normalize(val, mn, mx):
            return (val - mn) / (mx - mn) if mx != mn else 0.0

        glw = pg.GraphicsLayoutWidget()
        plot = glw.addPlot()
        plot.hideAxis("left")
        plot.setXRange(-0.1, p - 0.9, padding=0)
        plot.setYRange(-0.05, 1.05, padding=0)

        palette = [
            (220, 80, 80, 120),
            (80, 180, 80, 120),
            (100, 100, 220, 120),
            (220, 180, 80, 120),
            (180, 80, 220, 120),
        ]

        for i in range(n):
            color = palette[i % len(palette)]
            xs = list(range(p))
            ys = [normalize(cols[j][i], mins[j], maxs[j]) for j in range(p)]
            plot.plot(xs, ys, pen=pg.mkPen(color=color, width=1))

        for j in range(p):
            line = pg.InfiniteLine(pos=j, angle=90, pen=pg.mkPen("#666666", width=1))
            plot.addItem(line)
            label = pg.TextItem(text=f"X{j + 1}", anchor=(0.5, 1.0), color="#aaaaaa")
            label.setPos(j, -0.02)
            plot.addItem(label)

        return glw

    def _draw_histogram(self, plot: pg.PlotItem, data: list[float]):
        counts, edges = np.histogram(data, bins=10)
        width = float(edges[1] - edges[0])
        item = pg.BarGraphItem(
            x=edges[:-1],
            height=counts,
            width=width * 0.9,
            brush="#555555",
            pen=pg.mkPen("#888888"),
        )
        plot.addItem(item)

    def _draw_scatter(self, plot: pg.PlotItem, x: list[float], y: list[float]):
        plot.plot(
            x,
            y,
            pen=None,
            symbol="o",
            symbolSize=4,
            symbolBrush="#555555",
            symbolPen=pg.mkPen(None),
        )

    def _draw_corr_text(self, plot: pg.PlotItem, corr_value: float):
        text = pg.TextItem(
            text=f"Corr:\n{corr_value:.3f}",
            anchor=(0.5, 0.5),
            color="#cccccc",
        )
        plot.addItem(text)
        plot.setXRange(0, 1, padding=0)
        plot.setYRange(0, 1, padding=0)
        text.setPos(0.5, 0.5)

    def _build_correlation_field(self, data: Data) -> QWidget:
        cols = data.cols
        model = data.regression_model
        dep = data.dependent

        pred_indices = [i for i in range(len(cols)) if i != dep]

        x = np.array(cols[pred_indices[0]])
        y = np.array(cols[pred_indices[1]])
        z = np.array(cols[dep])

        x_mn, x_mx = x.min(), x.max()
        y_mn, y_mx = y.min(), y.max()
        z_mn, z_mx = z.min(), z.max()

        def norm(arr, mn, mx):
            return (arr - mn) / (mx - mn) if mx != mn else np.zeros_like(arr)

        x_n = norm(x, x_mn, x_mx)
        y_n = norm(y, y_mn, y_mx)
        z_n = norm(z, z_mn, z_mx)

        view = gl.GLViewWidget()
        view.setCameraPosition(distance=3)

        for start, end, color in [
            ([0, 0, 0], [1.2, 0, 0], (1, 0.3, 0.3, 1)),
            ([0, 0, 0], [0, 1.2, 0], (0.3, 1, 0.3, 1)),
            ([0, 0, 0], [0, 0, 1.2], (0.5, 0.7, 1.0, 1)),
        ]:
            view.addItem(
                gl.GLLinePlotItem(
                    pos=np.array([start, end]), color=color, width=2, antialias=True
                )
            )

        x_label = f"X{pred_indices[0] + 1}"
        y_label = f"X{pred_indices[1] + 1}"
        z_label = f"X{dep + 1}"

        for label_pos, text in [
            ([1.25, 0, 0], x_label),
            ([0, 1.25, 0], y_label),
            ([0, 0, 1.25], z_label),
        ]:
            view.addItem(
                gl.GLTextItem(
                    pos=np.array(label_pos), text=text, color=pg.mkColor("#cccccc")
                )
            )

        view.addItem(
            gl.GLScatterPlotItem(
                pos=np.column_stack([x_n, y_n, z_n]),
                size=6,
                color=(0.4, 0.6, 0.9, 0.8),
                pxMode=True,
            )
        )

        a0 = model.A_hat[0]
        a1 = model.A_hat[1]
        a2 = model.A_hat[2]

        grid_n = 20
        x_grid = np.linspace(x_mn, x_mx, grid_n)
        y_grid = np.linspace(y_mn, y_mx, grid_n)
        xx, yy = np.meshgrid(x_grid, y_grid)

        zz = a0 + a1 * xx + a2 * yy

        x_grid_n = norm(x_grid, x_mn, x_mx)
        y_grid_n = norm(y_grid, y_mn, y_mx)
        zz_n = norm(zz, z_mn, z_mx)

        plane = gl.GLSurfacePlotItem(
            x=x_grid_n,
            y=y_grid_n,
            z=zz_n.T,
            shader="balloon",
            color=(0.2, 0.8, 0.4, 0.15),
            smooth=True,
            drawEdges=False,
            drawFaces=True,
        )
        plane.setGLOptions("translucent")
        view.addItem(plane)

        return view

    def _build_diagnostic_diagram(self, data: Data) -> QWidget:
        glw = pg.GraphicsLayoutWidget()
        plot = glw.addPlot()

        x = data.regression_model.Y
        y = data.regression_model.model_error

        plot.plot(
            x=x,
            y=y,
            pen=None,
            symbol="o",
            symbolSize=4,
            symbolBrush="#555555",
            symbolPen=pg.mkPen(None),
        )

        return glw
