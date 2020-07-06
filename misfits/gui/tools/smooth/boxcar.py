import numpy as np

from inspect import currentframe, getframeinfo

from .... import get_parameters_from_header
from ....tools.smooth import Boxcar

def main(gui, spectrum, header):
    ''' - Smooth / Boxcar

Smoothing by convolving the spectrum with a boxcar window with a user-specified width.

The upper panel shows the raw spectrum (blue line) and the smoothed spectrum (red line).
The lower panel shows the boxcar window (blue line) and the width indicator (white marker with blue edge).


Use the cursor to adjust the width of the boxcar window.
To toggle data points in the spectrum, click on individual flux points in the raw spectrum in the upper panel.
Move the cursor to a panel and use the scrolling to zoom in and out and the middle button to center. When zooming in the upper panel, the lower panel will zoom along with it so they have the same scale.'''

    method = Boxcar(spectrum)

    try:
        params = get_parameters_from_header(method, header)
        params = method.set_parameters(**params)
    except KeyError:
        params = method.auto()
    spectrum.set_smooth(method(**params))

    if gui is None:
        return method

    ax = (gui.add_subplot(211, zoomable='horizontal'),
          gui.add_subplot(212, zoomable='horizontal'))

    i = method.get_mask()
    ax[0].plot(spectrum.wave, spectrum.flux, ls='', picker=10)
    ax[0].plot(spectrum.wave, spectrum.flux, color='blue', ls='dotted', alpha=0.5)
    flux, = ax[0].plot(spectrum.wave[i], spectrum.flux[i], color='blue')
    smooth, = ax[0].plot(spectrum.wave, spectrum.smooth, color='red')
    gui.set_title(ax[0], 'Spectrum')
    ax[0].set_xlabel('Wavelength')
    ax[0].set_ylabel('Flux')
    gui.set_limits(ax[0])

    window, = ax[1].plot(np.arange(spectrum.N)-(spectrum.N-1)/2.,
                         method.window(params['width']), color='blue', drawstyle='steps-mid')
    ax[1].plot(np.arange(spectrum.N)-(spectrum.N-1)/2., np.zeros(spectrum.N), visible=False)
    pwidth, = ax[1].plot(params['width']/2., np.max(window.get_ydata())/2.,
                         ls='', marker='o', mec='blue', mfc='white', ms=10, picker=10)
    gui.set_title(ax[1], 'Window')
    ax[1].set_xlabel('Sample')
    ax[1].set_ylabel('Amplitude')
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

        spectrum.set_smooth(method(method.width, flagged))

        i = method.get_mask()
        flux.set_data([spectrum.wave[i], spectrum.flux[i]])
        smooth.set_ydata(spectrum.smooth)

        gui.canvas.draw()

    gui.canvas.mpl_connect('pick_event', toggle_point)

    def set_width(e):

        if e.name == 'pick_event':

            if not e.mouseevent.inaxes is ax[1] or \
                    e.mouseevent.button != 1:
                return

            set_width.active = True
            e = e.mouseevent 

        elif e.name == 'motion_notify_event' and e.button == 1 and set_width.active:

            if not e.inaxes is ax[1] or \
                    e.xdata <= 0:
                return

            spectrum.set_smooth(method(2*e.xdata))
            window.set_ydata(method.window(2*e.xdata))
            pwidth.set_data(e.xdata, np.max(window.get_ydata())/2.)
            smooth.set_ydata(spectrum.smooth)

            gui.set_limits(ax[1], *ax[1].get_xlim())
            gui.canvas.draw()

        elif e.button != 1:

            set_width.active = False

    set_width.active = False

    gui.canvas.mpl_connect('motion_notify_event', set_width)
    gui.canvas.mpl_connect('pick_event', set_width)

    def set_limits(e):

        if not e.inaxes is ax[0]:
            return

        x0, xx = ax[0].get_xlim()
        width = len(spectrum(x0, xx).wave)

        gui.set_limits(ax[1], x0=-width/2., xx=+width/2.)
        gui.canvas.draw()

    gui.canvas.mpl_connect('scroll_event', set_limits)

    function = currentframe().f_globals[getframeinfo(currentframe()).function]
    gui.set_text('\n' + function.__doc__ + '\n')

    return method
