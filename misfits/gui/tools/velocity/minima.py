import numpy as np

from inspect import currentframe, getframeinfo

from .... import get_parameters_from_header

from ..base.intervals import BaseIntervals
from ..base.interval import BaseInterval
from ..base.points import BaseLabelTogglePoints
from ..base.point import BaseLabelTogglePoint
from ..base.label import BaseFloatLabel

from ....tools.velocity import Minima

class MinimumPoint (BaseLabelTogglePoint) :

    def def_label(self):

        return BaseFloatLabel(self)

class MinimaPoints (BaseLabelTogglePoints) :

    def new_point(self):

        return MinimumPoint(self)

class Interval (BaseInterval) :

    def __init__(self, intervals):

        BaseInterval.__init__(self, intervals)

        self.artists['points'] = self.objects = self.points = MinimaPoints(self)

    def set_data(self, x0=None, xx=None):

        BaseInterval.set_data(self, x0, xx)

        minima = self.spectrum.spline.minima

        i = np.where((self.x0 <= minima) & (minima <= self.xx))
        points = list(zip(minima[i], self.spectrum.spline[0](minima[i])))
        self.artists['points'].set_data(points)

class Intervals (BaseIntervals) :

    def new_interval(self):

        return Interval(self)

def draw(intervals):

    method = intervals.method

    e = type('event', (object,), dict(inaxes=intervals.ax[0], button=1))
    for i, wavelengths in enumerate(method.wavelengths):

        e.xdata = method.limits[i][0]
        intervals.add_interval(e)

        e.xdata = method.limits[i][1]
        intervals.set_interval(e)

        interval = intervals._active_interval

        x = np.array([point.x for point in interval.points])
        for j, wavelength in enumerate(wavelengths):

            k = np.argmin((wavelength - x)**2)

            interval.points.points[k].toggle()

            if not method.references[i][j] is None:
                interval.points.points[k].label.set_data(str(method.references[i][j]))

        interval.points._update_colors()

def fit(intervals):

    method = intervals.method

    limits, wavelengths, references = [], [], []
    for interval in intervals:
        limits.append(tuple(interval.data))
        wavelengths.append([point.x for point in interval.points if point.selected])
        references.append([point.label.data for point in interval.points if point.selected])
    res = method(limits, wavelengths, references)

def main(gui, spectrum, header, *args, **kwargs):
    ''' - Velocity / Minima

Measure velocities by identifying minima in the smoothed spectrum.

The upper panel shows the spectrum (black line), the 1-sigma, 2-sigma and 3-sigma errors (red, green and blue polygons, respectively) and the defined sections (colored semitransparent areas).
The lower panel shows the selected section of the spectrum (black line) and the minima of the smoothed spectrum (semitransparent markers) with reference boxes above.


Use the cursor to define one or more sections of the spectrum in the upper panel and to choose between them.
Click on the markers in the lower panel to toggle them for measurement. If known, fill out the reference boxes by positioning the cursor on top of them and type the rest wavelength.
Use right click to delete sections in the upper panel.
To zoom in the upper panel, position the cursor on top of it and use the scrolling to zoom in and out and the middle button to center.'''

    method = Minima(spectrum)

    try:
        params = get_parameters_from_header(method, header)
    except KeyError:
        pass
    else:
        method(**params)

    if gui is None:
        return method

    ax = (gui.add_subplot(211, cursor='vertical', zoomable='horizontal'),
          gui.add_subplot(212, cursor='both'))

    gui.set_title(ax[0], 'Spectrum')
    ax[0].set_xlabel('Wavelength')
    ax[0].set_ylabel('Flux')

    gui.set_title(ax[1], 'Minima')
    ax[1].set_xlabel('Wavelength')
    ax[1].set_ylabel('Flux')

    intervals = Intervals(gui, spectrum, method)

    if hasattr(method, 'limits'):
        draw(intervals)

    gui.set_limits(ax[0])

    gui.on_quit = lambda: fit(intervals)

    function = currentframe().f_globals[getframeinfo(currentframe()).function]
    gui.set_text('\n' + function.__doc__ + '\n')

    return method
