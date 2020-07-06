import numpy as np

from .base import Base

class BaseFunction (Base) :

    def __init__(self, parent):

        Base.__init__(self, parent)
        self.intervals, self.interval = parent.intervals, parent.interval
        self.parent = parent

        self.variables = self.def_variables()

        self.artist, = self.ax[1].plot([], [], color='blue', ls='dashed')

        self.deletable = True

    def def_variables(self):

        return [BaseVariable(self)]

    def set_parameters(self, **params):

        pass

    def set_color(self, color):

        for variable in self.variables:
            variable.set_color(color)

    def set_visible(self, visible):

        self.artist.set_visible(visible)
        for variable in self.variables:
            variable.set_visible(visible)

    def update(self):

        wave = self.spectrum(*self.interval.data).wave
        self.artist.set_data(wave, self(wave))

        for variable in self.variables:
            variable.update()

    def delete(self):

        while self.variables:
            self.variables.pop().delete()
        self.ax[1].lines.remove(self.artist)

    def __iter__(self):

        return iter(self.variables)

    def __call__(self, x):

        return self.variables[0].y * np.ones_like(x)

class BaseContinuumFunction (BaseFunction) :

    def update(self):

        BaseFunction.update(self)

        x, y = self.artist.get_data()
        self.artist.set_ydata(y + self.parent.continuum(x))
