import numpy as np

from .function import BaseFunction
from .variable import BaseVariable

class BaseContinuumVariable (BaseVariable) :

    def set_data(self, x=None, y=None, defining=False):

        x = None if not defining else x

        BaseVariable.set_data(self, x, y)

class BaseContinuum (BaseFunction) :

    def __init__(self, parent):

        BaseFunction.__init__(self, parent)

        self.artist.set_zorder(98)
        self.artist.set_linestyle('solid')
        self.artist.set_color('red')
        self.artist.set_picker(3)

        self.deletable = False

    def def_variables(self):

        return [
            BaseContinuumVariable(self),
            BaseContinuumVariable(self)
        ]

    @property
    def continuum(self):

        data = [(variable.x, variable.y) for variable in self.variables]

        try:
            return tuple(np.polyfit(*zip(*data), deg=1))
        except:
            return (0, self.variables[0].y)

    def set_parameters(self, continuum):

        continuum = np.poly1d(continuum)

        x0, xx = self.interval.data
        self.variables[0].set_data(x=x0, y=continuum(x0))
        self.variables[1].set_data(x=xx, y=continuum(xx))

    def update(self):

        BaseFunction.update(self)

        for function in self.parent.functions:

            if function is self:
                continue

            function.update()

    def __call__(self, x):

        return np.polyval(self.continuum, x)
