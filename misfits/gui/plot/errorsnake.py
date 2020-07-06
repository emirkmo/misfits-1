from matplotlib.patches import Polygon

from ... import SpectrumError

class ErrorSnake (object) :

    def __init__(self, ax, spectrum):

        self.ax, self.spectrum = ax, spectrum

        self.patches = []
        for sigma, color in zip((1,2,3), ('red','green','blue')):            
            d = self.data(sigma, loop_back=bool(sigma-1))
            self.patches.append(ax.add_patch(Polygon(d, color=color, alpha=.5, lw=.3)))

        self.artist, = ax.plot(self.wave, self.flux, color='black')

    def data(self, sigma, loop_back=False):

        self.wave = self.spectrum.wave
        self.error = self.spectrum.error

        try:
            self.flux = self.spectrum.smooth
        except SpectrumError:
            self.flux = self.spectrum.flux

        d = list(zip(self.wave, self.flux + sigma*self.error))
        if loop_back:
            d += list(zip(self.wave, self.flux + (sigma-1)*self.error))[::-1]
            d += list(zip(self.wave, self.flux - (sigma-1)*self.error))
        d += list(zip(self.wave, self.flux - sigma*self.error))[::-1]

        return d

    def update(self):

        for sigma, patch in zip((1,2,3), self.patches):
            patch.set_xy(self.data(sigma, loop_back=bool(sigma-1)))
        self.artist.set_data([self.wave, self.flux])

    def set_visible(self, visible):

        self.patches.set_visible(visible)
        self.artist.set_visible(visible)

    def __setattr__(self, name, value):

        if name == 'zoom_ignore':

            for patch in self.patches:
                patch.zoom_ignore = value
            self.artist.zoom_ignore = value

        else:

            object.__setattr__(self, name, value)

    def delete(self):

        self.patches.remove(self.patches)
        self.lines.remove(self.artist)
