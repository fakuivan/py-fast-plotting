from dataclasses import dataclass
from abc import ABC
import numpy as np
import pyqtgraph as pg
import edifice as ed
from PySide2 import QtWidgets
from typing import Any, Callable, Optional

class PyQtGraphData(ABC):
    def __eq__(self, other: "PyQtGraphData") -> bool:
        raise NotImplementedError()

    def render(self, current_widget) -> tuple[bool, Any]:
        raise NotImplementedError()

class PyQtGPlotFunc(PyQtGraphData):
    plot_func: Callable[[pg.PlotItem], None]

    def __eq__(self, other):
        if not isinstance(other, PyQtGPlotFunc):
            return False
        return self.plot_func == other.plot_func

    def render(self, current_widget) -> tuple[bool, pg.PlotWidget]:
        if not isinstance(current_widget, pg.PlotWidget):
            new_widget = pg.PlotWidget()
            self.plot_func(new_widget.getPlotItem())
            return True, new_widget

        plot_item = current_widget.getPlotItem()
        plot_item.clearPlots()
        self.plot_func(plot_item)
        return False, current_widget

@dataclass(frozen=True)
class PyQtGPlotData(PyQtGraphData):
    xys: list[tuple[np.ndarray, np.ndarray]]

    def __eq__(self, other):
        if not isinstance(other, PyQtGPlotData):
            return False
        return np.array_equal(self.xys, other.xys)

    def plot(self, widget: pg.PlotWidget):
        for x, y in self.xys:
            widget.plot(x, y)

    def set_data(self, data_items: list[pg.PlotDataItem]):
        for (x, y), item in zip(self.xys, data_items, strict=True):
            item.setData(x=x, y=y)

    def render(self, current_widget) -> tuple[bool, pg.PlotWidget]:
        if not isinstance(current_widget, pg.PlotWidget):
            new_widget = pg.PlotWidget()
            self.plot(new_widget)
            return True, new_widget
        
        plot_item = current_widget.getPlotItem()
        if not len(plot_item.listDataItems()) == len(self.xys):
            plot_item.clear()
            self.plot(plot_item)
            return False, current_widget
        
        self.set_data(plot_item.listDataItems())
        return False, current_widget

class PyQtGraphFigure(ed.CustomWidget):
    @ed.register_props
    def __init__(self, plot_data: PyQtGraphData):
        super().__init__()
        self.figure_added = False
        self.plot_widget: Optional[Any] = None
        self.current_plot_data: Optional[PyQtGraphData] = None

    def create_widget(self):
        widget = QtWidgets.QWidget()
        # No idea why the layout thing is needed
        layout = QtWidgets.QVBoxLayout(widget)
        self.figure_added = False
        return widget

    def paint(self, widget: QtWidgets.QWidget, newprops):
        new_plot_data = newprops.plot_data if 'plot_data' in newprops else self.props.plot_data

        if not self.figure_added:
            _, self.plot_widget = new_plot_data.render(None)
            widget.layout().addWidget(self.plot_widget)
            self.figure_added = True
            self.current_plot_data = new_plot_data
            return
        
        if self.current_plot_data == self.props.plot_data:
            return

        should_close, new_plot_widget = new_plot_data.render(self.plot_widget)
        if should_close:
            self.plot_widget.close()
            self.plot_widget = new_plot_widget
            widget.layout().addWidget(self.plot_widget)
        self.current_plot_data = new_plot_data
