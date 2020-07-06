from inspect import getframeinfo, currentframe

import numpy as np
from scipy.stats import norm
from matplotlib import cm, gridspec

from ...plot import ErrorSnake
from ....tools.uncertainty import MonteCarlo

def main(gui, spectrum, feature, output=None, N=1000, smooth=None):
    ''' - Uncertainty / Monte Carlo

Remeasure features in N realizations of the spectrum.

The upper panel shows the spectrum (black line), the 1-sigma, 2-sigma and 3-sigma errors (red, green and blue polygons, respectively) and the selected section (colored semitransparent area) encapsulating colored markers indicating the measured features.
The lower panel(s) show the results with the color of each subplot's spine matching the markers in the upper panel. The red, green and blue vertical lines indicate 1-sigma, 2-sigma and 3-sigma, respectively of the histogram (gray bars) and approximated normal distribution shown (dashed black line).
The buttons on the bottom changes between sections and quantitative results are printed beneath this text.'''

    method = MonteCarlo(spectrum, feature, output, N, smooth)

    if gui is None:
        return method

    nintervals, bins = len(feature.limits), int(1 + 3.322*np.log10(N))
    locations = feature.locations() if hasattr(feature, 'locations') else None
    for i,(x0,xx) in enumerate(feature.limits):

        nfeatures = len(method.data[i])

        if i:
            gui.add_canvas()
        gui.show_canvas(i)

        gs = gridspec.GridSpec(2, nfeatures if nfeatures else 1)
        gs.update(hspace=0.32, bottom=0.1)
        ax = [gui.add_subplot(gs[0,:])]

        color = cm.get_cmap('gist_rainbow')(1.*i/nintervals)
        ax[0].axvspan(x0, xx, lw=.5, fc=color, ec='black', alpha=0.5)
        errorsnake = ErrorSnake(ax[0], spectrum)

        for j in range(nfeatures):

            color = cm.get_cmap('gist_rainbow')(1.*j/nfeatures)

            ax.append(gui.add_subplot(gs[1,j]))
            ax[-1].set_xlabel('Wavelength')
            ax[-1].tick_params(color=color)
            for spine in ax[-1].spines.values():
                spine.set_edgecolor(color)

            try:
                ax[-1].hist(method.data[i][j], bins, density=1, color='black', alpha=0.3)
            except:
                ax[-1].hist(method.data[i][j], bins, normed=1, color='black', alpha=0.3)

            if not len(method.data[i][j]):
                continue

            ax[0].plot(*locations[i][j], ms=10, marker='o', mew=1.5, mec='black', mfc=color, alpha=.6)

            x = np.linspace(method.min(i,j), method.max(i,j), 100)
            ax[-1].plot(x, norm.pdf(x, method.mean(i,j), method.std(i,j)), color='black', lw=1, ls='dashed')

            ax[-1].axvline(method.mean(i,j), color='black', lw=2)
            pct_color = [(00.27, 'b'), (04.55, 'g'), (31.73, 'r'), (68.27, 'r'), (95.45, 'g'), (99.73,'b')] 
            for pct, color in pct_color:
                ax[-1].axvline(method.pctile(i, j, pct), color=color, lw=1)

            ax[-1].get_xaxis().get_major_formatter().set_useOffset(False)

        gui.set_title(ax[0], 'Spectrum')
        ax[0].set_xlabel('Wavelength')
        ax[0].set_ylabel('Flux')
        gui.set_limits(ax[0])#, x0=x0-0.5*(xx-x0), xx=xx+0.5*(xx-x0))

    function = currentframe().f_globals[getframeinfo(currentframe()).function]

    if len(feature.limits):
        gui.show_canvas_callback = lambda i: \
            gui.set_text('\n' + function.__doc__ + '\n' + ''.join([
                method.summary(i,j) for j in range(len(method.data[i]))
            ])[:-1])
    else:
        gui.set_text('\n' + function.__doc__ + '\n')

    gui.show_canvas(0)

    return method
