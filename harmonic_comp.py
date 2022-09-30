import edifice as ed
from ed_utils import function_component, Funs, ed_figure, PyQtGraphFigure, PyQtGPlotData
import numpy as np
from typing import Callable, Optional

def irdft_from_polar(dc, magnitudes, angles, n: Optional[int]=None):
    magnitudes = np.asanyarray(magnitudes)
    angles = np.asanyarray(angles)
    cs = np.concatenate(([dc], magnitudes/2*np.exp(1j*angles)))
    xs = np.fft.irfft(cs, n=n)
    return xs * len(xs)

@function_component
def HarmonicComposition(fs: Funs, use_pyqtgraph=True):
    harmonics, set_harmonics, map_harmonics = fs.use_state([(1, 0)]).as_tuple
    n = 1000
    def get_composition():
        mags, angles = zip(*harmonics
            ) if len(harmonics) > 0 else ([], [])
        comp = irdft_from_polar(0, mags, angles, n=n)
        ts = np.linspace(-.5, .5, len(comp))
        return ts, np.roll(comp, int(n/2))

    def get_components():
        w = 2*np.pi
        ts = np.linspace(-.5, .5, n)
        for i, (mag, angle) in enumerate(harmonics, 1):
            yield ts, mag*np.cos(i*w*ts+angle)

    def set_ith_harmonic(i):
        def set(mag, phase):
            result = list(harmonics)
            result[i] = (mag, phase)
            set_harmonics(result)
        return set

    def add_harmonic(_):
        map_harmonics(lambda old: old+[(0, 0)])

    def remove_harmonic(_):
        map_harmonics(lambda old: old[:-1])

    return ed.View(layout="column")(
        ed.View(layout="row")(
            ed_figure(lambda ax: ax.plot(*get_composition()), "grid"),
            ed_figure(lambda ax: [ax.plot(x, y) for x, y in get_components()], "grid"),
        ) if not use_pyqtgraph else ed.View(layout="row")(
            PyQtGraphFigure(plot_data=PyQtGPlotData([get_composition()])),
            PyQtGraphFigure(plot_data=PyQtGPlotData(list(get_components()))),
        ),
        ed.View("row")(
            *(ed.View(layout="column")(
                ed.Label(f"{i+1}th harmonic", style=dict(align="center")),
                MagnitudeAndPhaseControl(
                    set_ith_harmonic(i), mag, phase, orientation="vertical"))
                for i, (mag, phase) in enumerate(harmonics))
        ),
        ed.View(layout="column")(
            ed.Button("+", on_click=add_harmonic),
            *((ed.Button("-", on_click=remove_harmonic),
                ) if len(harmonics) > 0 else ())
        )
    )

@function_component
def MagnitudeAndPhaseControl(fs: Funs,
    on_change: Callable[[float, float], None],
    mag: float=0., phase: float=0., orientation: str = "vertical"
) -> ed.Component:
    mag_ = fs.use_state(mag)
    phase_ = fs.use_state(phase/2*np.pi)

    return ed.View(layout="row" if orientation == "vertical" else "column")(
        ed.Slider(mag_.value, min_value=0, max_value=1,
            on_change=lambda mag: on_change(mag_.set(mag), phase_.value),
            orientation=orientation),
        ed.Slider(phase_.value, min_value=0, max_value=1,
            on_change=lambda phase: on_change(mag_.value, phase_.set(phase)*2*np.pi),
            orientation=orientation)
    )


ed.App(HarmonicComposition(use_pyqtgraph=True)).start()