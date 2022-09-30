from typing import Optional, Callable
import numpy as np
import pyqtgraph as pg
import edifice as ed
from PySide2 import QtWidgets

class PyQtGraphFigure(ed.CustomWidget):
    @ed.register_props
    def __init__(self, plot_fun: Callable[[pg.PlotWidget], None]):
        super().__init__()
        self.figure_added = False
        self.plot_widget: Optional[pg.PlotWidget] = None

    def did_mount(self):
        plot_fun = self.props.plot_fun
        assert self.plot_widget is not None
        plot_fun(self.plot_widget)
    
    def create_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        self.figure_added = False
        return widget

    def paint(self, widget, newprops):
        if not self.figure_added:
            self.plot_widget = pg.PlotWidget()
            widget.layout().addWidget(self.plot_widget)
            self.figure_added = True

xs = np.linspace(-10, 10, 2000)
ys = np.sin((xs*2*np.pi*1+np.pi/2)/20)
#pg.plot(xs, ys)

ed.App(ed.View()(
    PyQtGraphFigure(lambda pw: pw.plot(xs, ys))
)).start()