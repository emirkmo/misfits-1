import numpy as np
from matplotlib import cm

from inspect import currentframe, getframeinfo

from .... import get_parameters_from_header

from ...plot import WidthPolygon

from ..base.intervals import BaseIntervals
from ..base.interval import BaseInterval
from ..base.base import Base

from ....tools.width import ShallowpEW

class BasePolynomialFit (Base) :

    def __init__(self, parent):

        Base.__init__(self, parent)
        self.intervals, self.interval = parent.intervals, parent

        self.x0, self.xx = None, None
        self.artist = self.ax[1].axvspan(None, None, fc='black', alpha=.5)

        self.polynomial, self.degree = [], 1

    def set_degree(self, degree):

        self.degree = degree

    def set_data(self, x0=None, xx=None, cosmetic=False):

        x0 = self.x0 if x0 is None else x0
        xx = self.xx if xx is None else xx

        if not cosmetic:
            self.x0, self.xx = x0, xx
        x0, xx = sorted([x0, xx], key=lambda x: x if not x is None else np.inf)

        self.artist.set_xy([(x0, 0), (x0, 1), (xx, 1), (xx, 0)])

    @property
    def data(self):

        return [self.x0, self.xx]

    def define(self):

        self.x0, self.xx = x0, xx = sorted(self.data)

        s = self.spectrum(x0, xx)
        self.polynomial = np.polyfit(s.wave, s.flux, self.degree)
        y0, yy = np.polyval(self.polynomial, [x0, xx])

        self.delete()

        self.artist, = self.ax[1].plot(
            [x0, xx], [y0, yy], ms=10, marker='o', mew=1.5, mec='black', lw=2.5,
            mfc='white', alpha=.6, zorder=float('inf'), color='black', picker=5
        )

    def refine(self):

        self.delete()

        self.x0, self.xx = None, None
        self.artist = self.ax[1].axvspan(None, None, fc='black', alpha=.5)
        
        self.polynomial = []

    @property
    def is_defined(self):

        return bool(len(self.polynomial))

    def set_color(self, color):

        self.artist.set_color(color)
        self.artist.set_markerfacecolor(color)

    def set_visible(self, visible):

        self.artist.set_visible(visible)

    def delete(self):

        if self.artist in self.ax[1].lines:
            self.ax[1].lines.remove(self.artist)
        elif self.artist in self.ax[1].patches:
            self.ax[1].patches.remove(self.artist)

    def __call__(self, x):

        return np.polyval(self.polynomial, x)

class ShallowPseudoEquivalentWidth (Base) :

    def __init__(self, parent):

        Base.__init__(self, parent)
        self.intervals, self.interval = parent.intervals, parent

        self.continua = [
            BasePolynomialFit(self),
            BasePolynomialFit(self)
        ]

        self.artist, = self.ax[1].plot([], [], color='black', ls='dashed')

    @property
    def data(self):

        return self.continua[0].data + self.continua[1].data

    def set_data(self, x, y):

        x0 = sum(self.data[:2]) / 2
        y0 = self.continua[0](x0)
        self.artist.set_data([x0, x], [y0, y])

    def define(self):

        self.continua = sorted(self.continua,
            key=lambda c: c.data[0] if c.data[0] is not None else '')

        self.ax[1].lines.remove(self.artist)

        x0, xx = sum(self.data[:2]) / 2, sum(self.data[2:]) / 2
        y0, yy = self.continua[0](x0), self.continua[1](xx)

        s = self.spectrum(x0, xx)
        wave, flux = [x0] + list(s.wave) + [xx], [y0] + list(s.flux) + [yy]
        self.artist = WidthPolygon(self.ax[1], wave, flux, alpha=.5, picker=True)
        self.artist.zoom_ignore = True

    def refine(self):

        self.artist.delete()

        self.artist, = self.ax[1].plot([], [], color='black', ls='dashed')

    def set_color(self, color):

        self.artist.set_color(color)

        for continuum in self.continua:
            continuum.set_color(color)

    def set_visible(self, visible):

        self.artist.set_visible(visible)

        for continuum in self.continua:
            continuum.set_visible(visible)

    def delete(self):

        if self.artist in self.ax[1].lines:
            self.ax[1].lines.remove(self.artist)
        else:
            self.artist.delete()

        for continuum in self.continua:
            continuum.delete()

class ShallowPseudoEquivalentWidths (Base) :

    def __init__(self, interval):

        Base.__init__(self, interval)                                               
        self.intervals, self.interval = interval.intervals, interval

        self.widths = list()
        self._active_width = None

        interval.mpl_connect('button_press_event', self.add_continuum)
        interval.mpl_connect('motion_notify_event', self.set_continuum)
        interval.mpl_connect('button_release_event', self.def_continuum)
        interval.mpl_connect('pick_event', self.adj_continuum)
        interval.mpl_connect('button_press_event', self.del_width)
        interval.mpl_connect('pick_event', self.del_width)

    def new_width(self):

        return ShallowPseudoEquivalentWidth(self)

    def add_continuum(self, e):

        if not e.button == 1:
            return

        if not self._active_width and e.inaxes is self.ax[1]:

            width = self.new_width()
            width.continua[0].set_data(x0=e.xdata)
            width.continua[0].set_data(xx=e.xdata, cosmetic=True)
            self._active_width = width

        elif self._active_width and e.inaxes is self.ax[1]:

            width = self._active_width
            x0 = width.continua[1].x0 if not width.continua[1].x0 is None else e.xdata
            width.continua[1].set_data(x0=x0)
            width.continua[1].set_data(xx=e.xdata, cosmetic=True)

        elif self._active_width:

            self._active_width.delete()
            self._active_width = None

        self.fig.canvas.draw()

    def set_continuum(self, e):

        if not e.inaxes is self.ax[1] or \
                not self._active_width:
            return

        width = self._active_width
        i = len(list(filter(None, width.data)))

        if i == 1:

            width.continua[0].set_data(xx=e.xdata, cosmetic=True)

        elif i == 2:

            width.set_data(e.xdata, e.ydata)

        elif i == 3:

            width.set_data(e.xdata, e.ydata)
            width.continua[1].set_data(xx=e.xdata, cosmetic=True)

        self.fig.canvas.draw()

    def def_continuum(self, e):

        if not e.button == 1 or \
                not self._active_width:
            return
        if not e.inaxes is self.ax[1]:
            self._active_width.delete()
            self._active_width = None
            self.fig.canvas.draw()
            return

        width = self._active_width
        i = (len(list(filter(None, width.data))) - 1) // 2

        width.continua[i].set_data(xx=e.xdata)

        try:
            width.continua[i].define()
        except TypeError:
            self._active_width.delete()
            self._active_width = None
            self.fig.canvas.draw()
            return

        if not i:
            return self.set_continuum(e)

        width.define()
        self._active_width = None

        self.widths.append(width)
        self.widths.sort(key=lambda w: w.continua[0].x0)

        self._update_colors()

        self.fig.canvas.draw()

    def adj_continuum(self, e):

        if self._active_width:
            if len(list(filter(None, self._active_width.data))) > 1:
                return
            else:
                self._active_width.delete()

        width, continuum = self._get_width_and_continuum_from_artist(e.artist)
        if not continuum:
            return

        self.widths.remove(width)
        self._active_width = width

        xydata = np.array([[e.mouseevent.xdata], [e.mouseevent.ydata]])
        i = np.argmin(np.sum((continuum.artist.get_data() - xydata)**2, axis=0))

        if not width.continua.index(continuum):
            width.continua = width.continua[::-1]

        x0 = width.continua[1].x0 if i else width.continua[1].xx

        width.refine()
        width.continua[1].refine()
        width.continua[1].set_data(x0)

        self.set_continuum(e.mouseevent)

    def del_width(self, e):

        if e.name == 'button_press_event':
            if not e.button == 3 or \
                    not self._active_width:
                return
            self._active_width.delete()
            self._active_width = None
            self.fig.canvas.draw()
            return

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.mouseevent.button == 3:
            return

        width, continuum = self._get_width_and_continuum_from_artist(e.artist)
        if not width:
            return

        self.widths.remove(width)
        width.delete()

        self._update_colors()

        self.fig.canvas.draw()

    def set_visible(self, visible):

        for width in self.widths:
            width.set_visible(visible)
        
    def delete(self):

        for width in self.widths:
            width.delete()

    def _get_width_and_continuum_from_artist(self, artist):

        for width in self.widths:

            if (width.artist.polygon is artist):
                return width, None

            continua_artists = [continuum.artist for continuum in width.continua]
            if artist in continua_artists:
                continuum = width.continua[continua_artists.index(artist)]
                return width, continuum

        return None, None

    def _update_colors(self):

        N = len(self.widths)

        for i, width in enumerate(self.widths):

            color = cm.get_cmap('gist_rainbow')(1.*i/N)
            width.set_color(color)

    def __iter__(self):
    
        return iter(self.widths)

class Interval (BaseInterval) :

    def __init__(self, intervals):

        BaseInterval.__init__(self, intervals)

        self.artists['points'] = self.objects = self.shallowpews = \
            ShallowPseudoEquivalentWidths(self)

class Intervals (BaseIntervals) :

    def new_interval(self):

        return Interval(self)

def draw(intervals):

    method = intervals.method

    e = type('event', (object,), dict(button=1, ydata=0))
    for i, continua in enumerate(method.continua):

        e.inaxes = intervals.ax[0]

        e.xdata = method.limits[i][0]
        intervals.add_interval(e)

        e.xdata = method.limits[i][1]
        intervals.set_interval(e)

        interval = intervals._active_interval

        e.inaxes = intervals.ax[1]
        for j, (x1, x2, x3, x4) in enumerate(continua):

            e.xdata = x1
            interval.shallowpews.add_continuum(e)
            e.xdata = x2
            interval.shallowpews.def_continuum(e)

            e.xdata = x3
            interval.shallowpews.add_continuum(e)
            e.xdata = x4
            interval.shallowpews.def_continuum(e)

            interval.shallowpews._active_width = None

def fit(intervals):

    method = intervals.method

    limits, continua = [], []
    for interval in intervals.intervals:
        limits.append(tuple(interval.data))
        continua.append([
            tuple(shallowpew.continua[0].data + shallowpew.continua[1].data)
            for shallowpew in interval.shallowpews
        ])
    res = method(limits, continua)

def main(gui, spectrum, header, *args, **kwargs):
    ''' - Width / Shallow pEW

Define pEWs by fitting the continuum on each side of the feature.

The upper panel shows the spectrum (black line), the 1-sigma, 2-sigma and 3-sigma errors (red, green and blue polygons, respectively) and the defined sections (colored semitransparent areas).
The lower panel shows the selected section of the spectrum (black line) and the pEWs (colored semitransparent areas) that are defined by two semitransparent markers on each side.


Use the cursor to define one or more sections of the spectrum in the upper panel and to choose between them.
To define a pEW, click and drag to define an area to fit a continuum on one side of the pEW and then do the same on the other side. Click on the semitransparent markers to adjust the continuum area.
Use right click to delete sections in the upper panel and pEWs in the lower panel.
To zoom in the upper panel, position the cursor on top of it and use the scrolling to zoom in and out and the middle button to center.'''

    method = ShallowpEW(spectrum)

    try:
        params = get_parameters_from_header(method, header)
    except KeyError:
        pass
    else:
        method(**params)

    if gui is None:
        return method

    ax = (gui.add_subplot(211, cursor='vertical', zoomable='horizontal'),
          gui.add_subplot(212, cursor='vertical'))

    gui.set_title(ax[0], 'Spectrum')
    ax[0].set_xlabel('Wavelength')
    ax[0].set_ylabel('Flux')

    gui.set_title(ax[1], 'Spectrum')
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
