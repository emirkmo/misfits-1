import numpy as np

from inspect import currentframe, getframeinfo

from .... import get_parameters_from_header
from ....tools.smooth import LowPass

def main(gui, spectrum, header):
    ''' - Smooth / Low-pass

Smoothing using a low-pass filter as described in Marion et al. (2009).
The filter is defined as,
  S / (S + N)
where S is the signal and N is the noise.

The upper panel shows the raw spectrum (blue line) and the smoothed spectrum (red line).
The lower panel shows the power spectrum of the spectrum (blue line), the best fit (dashed red line and solid marker) and the current signal and noise values (red plus).


Use the cursor to drag-and-drop the red cross in the lower panel to change the signal and noise values.
To toggle data points in the spectrum, click on individual flux points in the raw spectrum in the upper panel.
Move the cursor to a panel and use the scrolling to zoom in and out and the middle button to center.'''

    method = LowPass(spectrum)

    try:
        params = get_parameters_from_header(method, header)
        params = method.set_parameters(**params)
    except KeyError:
        params = method.auto()
    spectrum.set_smooth(method(**params))

    if gui is None:
        return method

    ax = (gui.add_subplot(211, zoomable='horizontal'),
          gui.add_subplot(212, zoomable='right', cursor='both'))

    i = method.get_mask()
    ax[0].plot(spectrum.wave, spectrum.flux, ls='', picker=10)
    ax[0].plot(spectrum.wave, spectrum.flux, color='blue', ls='dotted', alpha=0.5)
    flux, = ax[0].plot(spectrum.wave[i], spectrum.flux[i], color='blue')
    smooth, = ax[0].plot(spectrum.wave, spectrum.smooth, color='red')
    ax[0].set_xlabel('Wavelength'); ax[0].set_ylabel('Flux')
    gui.set_title(ax[0], 'Spectrum')
    gui.set_limits(ax[0])

    params = method.auto()
    lpwr, = ax[1].plot(method.bins, method.lpwr, color='blue')
    power_spectrum_fit = method.power_spectrum_fit_function(method.bins, **params)
    pwrfit, = ax[1].plot(method.bins, power_spectrum_fit, color='red', ls='dashed')
    sn, = ax[1].plot(params['signal'], params['noise'], color='red', marker='o')
    cursor = (ax[1].axvline(method.signal, color='red'),
              ax[1].axhline(method.noise, color='red'))
    ax[1].set_xlabel('Frequency Bin'); ax[1].set_ylabel('Power')
    gui.set_title(ax[1], 'Power Spectrum')
    gui.set_limits(ax[1], x0=0)

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

        spectrum.set_smooth(method(method.signal, method.noise, method.slope, flagged))

        i = method.get_mask()
        flux.set_data([spectrum.wave[i], spectrum.flux[i]])
        smooth.set_ydata(spectrum.smooth)
        lpwr.set_ydata(method.lpwr)
        params = method.auto()
        pwrfit.set_ydata(method.power_spectrum_fit_function(method.bins, **params))
        sn.set_data([params['signal'], params['noise']])

        gui.set_limits(ax[1], x0=0)
        gui.canvas.draw()

    gui.canvas.mpl_connect('pick_event', toggle_point)

    def set_smooth(e):

        if not e.inaxes is ax[1] or \
                (e.button == 1 and int(e.xdata) <= 1):
            return

        if e.button == 1:
            signal, noise = int(e.xdata), e.ydata
            spectrum.set_smooth(method(signal, noise))
        elif e.button == 3:
            spectrum.set_smooth(method(**method.auto()))

        smooth.set_ydata(spectrum.smooth)

        cursor[0].set_xdata(method.signal)
        cursor[1].set_ydata(method.noise)

        gui.canvas.draw()

    gui.canvas.mpl_connect('motion_notify_event', set_smooth)
    gui.canvas.mpl_connect('button_press_event', set_smooth)

    function = currentframe().f_globals[getframeinfo(currentframe()).function]
    gui.set_text('\n' + function.__doc__ + '\n')

    return method
