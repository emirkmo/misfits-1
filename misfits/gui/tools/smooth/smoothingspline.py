import numpy as np

from inspect import currentframe, getframeinfo

from .... import get_parameters_from_header
from ...plot import ErrorSnake
from ....tools.smooth import SmoothingSpline

def main(gui, spectrum, header):
    ''' - Smooth / Smoothing Spline

Smoothing using the error spectrum to create a smoothing spline fit to spectrum.

The upper panel shows the raw spectrum (blue line) the error spectrum (black error bars) and the smoothed spectrum (red line).
The lower panel shows the smoothed spectrum (black line) and the 1-sigma, 2-sigma and 3-sigma errors (red, green and blue polygons, respectively).


To toggle data points in the spectrum, click on individual flux points in the raw spectrum in the upper panel.
Move the cursor to a panel and use the scrolling to zoom in and out and the middle button to center.'''

    method = SmoothingSpline(spectrum)

    try:
        params = get_parameters_from_header(method, header)
        params = method.set_parameters(**params)
    except KeyError:
        params = method.auto()
    spectrum.set_smooth(method(**params))

    ax = (gui.add_subplot(211, zoomable='horizontal'),
          gui.add_subplot(212, zoomable='horizontal'))

    i = method.get_mask()
    ax[0].plot(spectrum.wave, spectrum.flux, ls='', picker=10)
    ax[0].plot(spectrum.wave, spectrum.flux, color='blue', ls='dotted', alpha=0.5)
    flux = ax[0].errorbar(spectrum.wave[i], spectrum.flux[i], spectrum.error[i],
                          capsize=3.5, color='blue', ecolor='black')
    smooth, = ax[0].plot(spectrum.wave, spectrum.smooth, color='red', zorder=3)
    gui.set_title(ax[0], 'Spectrum')
    ax[0].set_xlabel('Wavelength')
    ax[0].set_ylabel('Flux')
    gui.set_limits(ax[0])

    errorsnake = ErrorSnake(ax[1], spectrum)
    gui.set_title(ax[1], '1$\sigma$, 2$\sigma$ and 3$\sigma$')
    ax[1].set_xlabel('Wavelength')
    ax[1].set_ylabel('Flux')
    gui.set_limits(ax[1])

    flagged = method.flagged.copy()
    def toggle_point(e):

        if not e.mouseevent.inaxes is ax[0] or \
                e.mouseevent.button != 1:
            return

        i = e.ind[np.argmin((spectrum.wave[e.ind]-e.mouseevent.xdata)**2)]
        if i in flagged:
            flagged.remove(i)
        else:
            flagged.append(i)

        spectrum.set_smooth(method(flagged))

        i = method.get_mask()
        flux.lines[0].set_data([spectrum.wave[i], spectrum.flux[i]])#, spectrum.error[i]])
        smooth.set_ydata(spectrum.smooth)

        errorsnake.update()
        gui.canvas.draw()

    gui.canvas.mpl_connect('pick_event', toggle_point)

    function = currentframe().f_globals[getframeinfo(currentframe()).function]
    gui.set_text('\n' + function.__doc__ + '\n')

    return method
