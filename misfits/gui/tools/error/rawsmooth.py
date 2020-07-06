from inspect import getframeinfo, currentframe

import numpy as np

from .... import get_parameters_from_header
from ...plot import ErrorSnake
from ....tools.error import RawSmooth

def main(gui, spectrum, header):
    ''' - Error / Raw - Smooth

Estimate the error spectrum by smoothing the |raw-smooth| residuals.
The residuals are then scaled to encapsulate 68% (1-sigma) of the residual points.

The upper panel shows the residuals (black line), the absolute values of the residuals (blue line) and the estimated error spectrum (red line).
The lower panel shows the smoothed spectrum (black line) and the 1-sigma, 2-sigma and 3-sigma errors (red, green and blue polygons, respectively).

Adjust the smoothing of the error spectrum from the menu in the lower left corner.
To toggle data points in the residuals, click on individual points of the plot showing the absolute values of the residuals in the upper panel.
Move the cursor to a panel and use the scrolling to zoom in and out and the middle button to center.'''

    method = RawSmooth(spectrum)

    try:
        params = get_parameters_from_header(method, header)
        params = method.set_parameters(**params)
    except KeyError:
        params = method.auto()
    spectrum.set_error(method(**params))

    if gui is None:
        return method

    ax = (gui.add_subplot(211, zoomable='horizontal'),
                gui.add_subplot(212, zoomable='horizontal'))

    i = method.get_mask()
    res, = ax[0].plot(spectrum.wave[i], method.residuals[i], color='black')
    ax[0].plot(spectrum.wave, method.abs_residuals, color='blue', ls='dotted', alpha=0.5, picker=3)
    abs_res, = ax[0].plot(spectrum.wave[i], method.abs_residuals[i], color='blue')
    error, = ax[0].plot(spectrum.wave, spectrum.error, color='red')
    gui.set_title(ax[0], 'Residuals')
    ax[0].set_xlabel('Wavelength')
    ax[0].set_ylabel('Flux Residuals')
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

        if e.ind[0] in flagged:
            flagged.remove(e.ind[0])
        else:
            flagged.append(e.ind[0])

        spectrum.set_error(method(method.length, flagged))

        i = method.get_mask()
        res.set_data([spectrum.wave[i], method.residuals[i]])
        abs_res.set_data([spectrum.wave[i], method.abs_residuals[i]])
        error.set_ydata(spectrum.error)

        errorsnake.update()
        gui.canvas.draw()

    gui.canvas.mpl_connect('pick_event', toggle_point)

    def set_length(length):

        length = np.exp(length)
        spectrum.set_error(method(length))
        error.set_ydata(spectrum.error)

        errorsnake.update()
        gui.canvas.draw()

    gui.add_menu_scale('Smoothing', [-3,np.log(spectrum.N)], np.log(params['length']), set_length)

    function = currentframe().f_globals[getframeinfo(currentframe()).function]
    gui.set_text('\n' + function.__doc__ + '\n')

    return method
