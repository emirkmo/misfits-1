from sys import version_info

import numpy as np

from inspect import currentframe, getframeinfo

if version_info.major == 3:
    from tkinter import messagebox
else:
    import tkMessageBox as messagebox

from .... import get_parameters_from_header

from ..base.intervals import BaseIntervals
from ..base.interval import BaseInterval
from ..base.functions import BaseLabelContinuumFunctions
from ..base.function import BaseContinuumFunction
from ..base.variable import BaseVariable, BaseLabelVariable
from ..base.label import BaseFloatLabel

from ....tools.velocity import Gaussians

class PositionAmplitudeVariable (BaseLabelVariable) :

    def def_label(self):

        return BaseFloatLabel(self)

    def set_data(self, x=None, y=None):

        try:
            width = 2 * np.sqrt(2*np.log(2)) * self.parent.stddev
        except:
            x0, xx = self.interval.data
            width = .2 * (xx - x0)

        BaseVariable.set_data(self, x, y)

        self.parent.variables[1].set_data(x=self.x+width/2)

    def update(self):

        continuum = self.parent.parent.continuum

        x = self.parent.mean
        y = self.parent.amplitude + continuum(x)

        self.artist.set_data(x, y)

class StddevVariable (BaseVariable) :

    def __init__(self, parent):

        BaseVariable.__init__(self, parent)

    def set_data(self, x=None, y=None):

        if x <= self.parent.mean:
            return

        BaseVariable.set_data(self, x, None)

    def update(self):

        continuum = self.parent.parent.continuum

        x = self.parent.mean + np.sqrt(2*np.log(2)) * self.parent.stddev
        y = continuum(x) + self.parent.amplitude / 2

        self.artist.set_data(x, y)

class Gaussian (BaseContinuumFunction) :

    def def_variables(self):

        return [
            PositionAmplitudeVariable(self),
            StddevVariable(self)
        ]

    @property
    def amplitude(self):

        continuum = self.parent.continuum(self.variables[0].x)
        return self.variables[0].y - continuum

    @property
    def mean(self):

        return self.variables[0].x

    @property
    def stddev(self):

        fwhm = 2 * (self.variables[1].x - self.variables[0].x)
        return fwhm / 2 / np.sqrt(2*np.log(2))

    def set_parameters(self, amplitude=None, mean=None, stddev=None):

        amplitude = amplitude if not amplitude is None else self.amplitude
        mean = mean if not mean is None else self.mean
        stddev = stddev if not stddev is None else self.stddev

        continuum = self.parent.continuum

        self.variables[0].x = mean
        self.variables[0].y = amplitude + continuum(mean)

        self.variables[1].x = mean + np.sqrt(2*np.log(2)) * stddev
        self.variables[1].y = amplitude / 2 + continuum(self.variables[1].x)

    def __call__(self, x):

        A, x0, s = self.amplitude, self.mean, self.stddev

        try:
            return A * np.exp( -(x-x0)**2 / 2 / s**2 )
        except:
            return np.zeros_like(x)

class GaussianFunctions (BaseLabelContinuumFunctions) :

    def new_function(self):

        return Gaussian(self)

class Interval (BaseInterval) :

    def __init__(self, intervals):

        BaseInterval.__init__(self, intervals)

        self.artists['functions'] = self.objects = self.functions = GaussianFunctions(self)

        self.artists['chi2'] = self.ax[1].text(1, 0, '', fontsize=8, 
            va='bottom', ha='right', transform=self.ax[1].transAxes)

    def set_data(self, x0=None, xx=None):

        BaseInterval.set_data(self, x0, xx)

        x0, xx = self.data
        y0, yy = self.spectrum[x0][1], self.spectrum[xx][1]

        continuum = self.artists['functions'].continuum
        continuum.variables[0].set_data(x0, y0, defining=True)
        continuum.variables[1].set_data(xx, yy, defining=True)

    def delete(self):

        chi2 = self.artists.pop('chi2')
        self.ax[1].texts.remove(chi2)

        BaseInterval.delete(self)

class Intervals (BaseIntervals) :

    def new_interval(self):

        return Interval(self)

def draw(intervals):

    method = intervals.method

    e = type('event', (object,), dict(inaxes=intervals.ax[0], button=1))
    em = e.mouseevent = type('mouse', (object,), dict(inaxes=intervals.ax[1], button=1))
    for i, x0s in enumerate(method.x0s):

        e.xdata = method.limits[i][0]
        intervals.add_interval(e)

        e.xdata = method.limits[i][1]
        intervals.set_interval(e)

        interval = intervals._active_interval

        continuum = method.continuum[i]
        interval.functions.continuum.set_parameters(continuum)

        e.artist = interval.functions.continuum.artist
        for j, x0 in enumerate(x0s):

            em.xdata, em.ydata = x0, method.amplitudes[i][j] + interval.functions.continuum(x0)

            interval.functions.add_function(e)
            function = interval.functions._active_variable.parent
            function.set_parameters(stddev=method.stddevs[i][j])
            if not method.references[i][j] is None:
                function.variables[0].label.set_data(str(method.references[i][j]))
            interval.functions._active_variable = None

            function.update()

        interval.functions.update()

def fit(intervals):

    method = intervals.method

    limits, continuum, amplitudes, means, stddevs, references = [], [], [], [], [], []
    for interval in intervals:
        limits.append(tuple(interval.data))
        continuum.append(interval.functions.continuum.continuum)
        amplitudes.append([function.amplitude for function in interval.functions])
        means.append([function.mean for function in interval.functions])
        stddevs.append([function.stddev for function in interval.functions])
        references.append([function.variables[0].label.data for function in interval.functions])
    res = method(limits, continuum, amplitudes, means, stddevs, references)

    selected_interval, failed_interval = intervals._selected_interval, None
    for i, interval in enumerate(intervals):

        intervals.show_interval(interval)

        if not len(res[0][i]) or None in res[0][i]:
            messagebox.showerror('Error', 'Unable to fit interval [%.2f,%.2f]' % limits[i])
            failed_interval = interval
            interval.artists['chi2'].set_text('')
            continue

        interval.functions.continuum.set_parameters(method.continuum[i])
        for j, function in enumerate(interval.functions):
            function.set_parameters(method.amplitudes[i][j], method.x0s[i][j], method.stddevs[i][j])
            function.update()
        interval.functions.update()

        interval.artists['chi2'].set_text(r'$\chi^2/\nu$ = %.2f  ' % res[2][i])

    if failed_interval:
        intervals.show_interval(failed_interval)
    elif selected_interval:
        intervals.show_interval(selected_interval)

    intervals.gui.fig.canvas.draw()

    return failed_interval

def main(gui, spectrum, header, fix_continuum=False):
    ''' - Velocity / Gaussians

Measure velocities by fitting Gaussians to sections of the spectrum.

The upper panel shows the spectrum (black line), the 1-sigma, 2-sigma and 3-sigma errors (red, green and blue polygons, respectively) and the defined sections (colored semitransparent areas).
The lower panel shows the selected section of the spectrum (black line), estimated continuum (red line), the individual Gaussians (dashed blue lines), the combined Gaussians (solid blue line) and adjustable variables (open semitransparent markers) with reference boxes above or below when applicable.


Use the cursor to define one or more sections of the spectrum in the upper panel and to choose between them.
Add Gaussians to the fit by dragging from the red continuum line in the lower panel and use the semitransparent open markers to adjust the function. If known, fill out the reference boxes by positioning the cursor on top of them and type the rest wavelength.
Use right click to delete sections in the upper panel and Gaussians in the lower panel.
Use the menu in the lower left corner to fit the functions to the sections and to toggle whether or not to fix the continuum.
To zoom in the upper panel, position the cursor on top of it and use the scrolling to zoom in and out and the middle button to center.'''

    method = Gaussians(spectrum)

    method.set_fix_continuum(fix_continuum)

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

    gui.set_title(ax[1], 'Fit')
    ax[1].set_xlabel('Wavelength')
    ax[1].set_ylabel('Flux')

    intervals = Intervals(gui, spectrum, method)

    if hasattr(method, 'limits'):
        draw(intervals)

    gui.set_limits(ax[0])

    gui.add_menu_button('Fit', lambda: fit(intervals))
    gui.add_menu_checkbox('Fix continuum', fix_continuum, lambda s: method.set_fix_continuum(s))
    gui.on_quit = lambda: fit(intervals)

    function = currentframe().f_globals[getframeinfo(currentframe()).function]
    gui.set_text('\n' + function.__doc__ + '\n')

    return method
