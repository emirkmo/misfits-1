import numpy as np
from matplotlib import cm

from inspect import currentframe, getframeinfo

from .... import get_parameters_from_header

from ...plot import WidthPolygon

from ..base.intervals import BaseIntervals
from ..base.interval import BaseInterval
from ..base.points import BaseConnectingPoints
from ..base.connection import BaseConnection

from ....tools.width import pEW

class PseudoEquivalentWidthConnection (BaseConnection) :

    def define(self):

        self.ax[1].lines.remove(self.artist)

        x0, xx = list(zip(*self.data))[0]
        
        wave = self.spectrum(x0, xx).wave
        flux = self.spectrum.spline[0](wave)
        self.artist = WidthPolygon(self.ax[1], wave, flux, alpha=.5, picker=True)

    def delete(self):

        if self.artist in self.ax[1].lines:
            BaseConnection.delete(self)
        else:
            self.artist.delete()

class PseudoEquivalentWidthPoints (BaseConnectingPoints) :

    def new_connection(self):

        return PseudoEquivalentWidthConnection(self)

    def def_connection(self, e):

        connection = self._active_connection
        Nconnections = len(self.connections)

        BaseConnectingPoints.def_connection(self, e)

        if len(self.connections) > Nconnections:
            connection.define()
            self._update_colors()
            self.fig.canvas.draw()

    def _get_connection_from_artist(self, artist):

        for connection in self.connections:
            if connection.artist.polygon is artist or \
                    connection.artist.continuum is artist:
                return connection

class Interval (BaseInterval) :

    def __init__(self, intervals):

        BaseInterval.__init__(self, intervals)

        self.artists['points'] = self.objects = self.points = PseudoEquivalentWidthPoints(self)

    def set_data(self, x0=None, xx=None):

        BaseInterval.set_data(self, x0, xx)

        x0, xx = self.data
        maxima = self.spectrum.spline.maxima

        i = np.where((x0 <= maxima) & (maxima <= xx))
        points = list(zip(maxima[i], self.spectrum.spline[0](maxima[i])))
        self.artists['points'].set_data(points)

class Intervals (BaseIntervals) :

    def new_interval(self):

        return Interval(self)

def draw(intervals):

        method = intervals.method

        e = type('event', (object,), dict(inaxes=intervals.ax[0], button=1))
        em = e.mouseevent = type('mouse', (object,), dict(inaxes=intervals.ax[1], button=1))
        for i, maxima in enumerate(method.maxima):

            e.xdata = method.limits[i][0]
            intervals.add_interval(e)

            e.xdata = method.limits[i][1]
            intervals.set_interval(e)

            interval = intervals._active_interval
            points = interval.points.points

            x = np.array([point.x for point in points])
            if not len(x):
                continue

            for j, (x0, xx) in enumerate(maxima):

                i, j = np.argmin((x0 - x)**2), np.argmin((xx - x)**2)

                e.artist, em.name = points[i].artist, 'button_press_event'
                interval.points.add_connection(e)

                e.artist, em.name = points[j].artist, 'button_release_event'
                interval.points.def_connection(e)

                interval.points._active_connection = None

def fit(intervals):

    method = intervals.method

    limits, maxima = [], []
    for interval in intervals:
        limits.append(tuple(interval.data))
        maxima.append([list(zip(*connection.data))[0] for connection in interval.points])
    res = method(limits, maxima)

def main(gui, spectrum, header, *args, **kwargs):
    ''' - Width / pEW

Measure pEW by connecting maxima in the smoothed spectrum.

The upper panel shows the spectrum (black line), the 1-sigma, 2-sigma and 3-sigma errors (red, green and blue polygons, respectively) and the defined sections (colored semitransparent areas).
The lower panel shows the selected section of the spectrum (black line), the maxima of the smoothed spectrum (semitransparent markers) and the defined pEWs (colored semitransparent areas).

Use the cursor to define one or more sections of the spectrum in the upper panel and to choose between them.
To define a pEW, click on a marker and drag the cursor to another marker in the lower panel.
Use right click to delete sections in the upper panel and pEWs in the lower panel.
To zoom in the upper panel, position the cursor on top of it and use the scrolling to zoom in and out and the middle button to center.'''

    method = pEW(spectrum)

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

    gui.set_title(ax[1], 'Maxima')
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
