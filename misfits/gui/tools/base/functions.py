import numpy as np
from matplotlib import cm

from .base import Base
from .continuum import BaseContinuum

class BaseFunctions (Base) :

    def __init__(self, interval):

        Base.__init__(self, interval)
        self.intervals, self.interval = interval.intervals, interval

        self.artist, = self.ax[1].plot([], [], color='blue')

        self.functions = []
        self._active_variable = None

        interval.mpl_connect('pick_event', self.pick_variable)
        interval.mpl_connect('motion_notify_event', self.set_variable)
        interval.mpl_connect('pick_event', self.del_function)

    def new_function(self):

        return BaseFunction(self)

    def add_function(self, e):

        function = self.new_function()
        self.functions.append(function)

        x, y = e.mouseevent.xdata, e.mouseevent.ydata
        for variable in function:
            variable.set_data(x, y)

        self.update()
        self.gui.canvas.draw()

    def pick_variable(self, e):

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.artist.get_visible() or \
                not hasattr(e.mouseevent, 'button') or \
                not e.mouseevent.button == 1 or \
                self._active_variable:
            return

        function, variable = self._get_function_and_variable_from_artist(e.artist)
        if not variable:
            return

        self._active_variable = variable

    def set_variable(self, e):

        if not e.inaxes is self.ax[1] or \
                not hasattr(e, 'button'):
            return
        if not e.button == 1:
            self._active_variable = None
            return
        if not self._active_variable:
            return

        self._active_variable.set_data(x=e.xdata, y=e.ydata)

        self.update()
        self.fig.canvas.draw()

    def del_function(self, e):

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.artist.get_visible() or \
                not hasattr(e.mouseevent, 'button') or \
                not e.mouseevent.button == 3:
            return

        function, variable = self._get_function_and_variable_from_artist(e.artist)
        if not function or not function.deletable:
            return

        self.functions.remove(function)
        function.delete()

        self.update()
        self.fig.canvas.draw()

    def update(self):

        x0, xx = self.interval.data
        i = np.where((x0 <= self.spectrum.wave) & (self.spectrum.wave <= xx))
        self.artist.set_data(self.spectrum.wave[i], self(self.spectrum.wave[i]))

        self.gui.set_limits(self.ax[1])
        self._update_colors()

    def set_visible(self, visible):

        for functions in self.functions:
            functions.set_visible(visible)
        self.artist.set_visible(visible)

    def delete(self):

        for function in self.functions:
            function.delete()
        self.ax[1].lines.remove(self.artist)

    def _get_function_and_variable_from_artist(self, artist):

        for function in self.functions:
            for variable in function:
                if variable.artist is artist:
                    return function, variable

        return None, None

    def _update_colors(self):

        N = len(self.functions)

        functions = sorted(self.functions, key=lambda f: f.variables[0].x)
        for i, function in enumerate(functions):

            color = cm.get_cmap('gist_rainbow')(1.*i/N)
            function.set_color(color)

    def __iter__(self):

        return iter(sorted(self.functions, key=lambda f: f.variables[0].x))

    def __call__(self, x):

        return sum([function(x) for function in self.functions])

class BaseContinuumFunctions (BaseFunctions) :

    def __init__(self, interval):

        BaseFunctions.__init__(self, interval)

        self.continuum = BaseContinuum(self)
        self.functions.insert(0, self.continuum)

        interval.mpl_connect('pick_event', self.add_function)

    def add_function(self, e):

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.artist.get_visible() or \
                not hasattr(e.mouseevent, 'button') or \
                not e.mouseevent.button == 1 or \
                not e.artist is self.continuum.artist or \
                self._active_variable:
            return

        BaseFunctions.add_function(self, e)

        self._active_variable = self.functions[-1].variables[0]

    def _update_colors(self):

        self.functions = self.functions[1:]
        BaseFunctions._update_colors(self)
        self.functions.insert(0, self.continuum)

    def __iter__(self):

        return iter(sorted(self.functions[1:], key=lambda f: f.variables[0].x))

    def __call__(self, x):

        return sum([function(x) for function in self.functions])

class BaseLabelContinuumFunctions (BaseContinuumFunctions) :

    def __init__(self, interval):

        BaseContinuumFunctions.__init__(self, interval)

        interval.mpl_connect('key_press_event', self.fig.canvas.pick)
        interval.mpl_connect('pick_event', self.set_label_data)

    def update(self):

        BaseContinuumFunctions.update(self)

        for function in self.functions:
            for variable in function:
                if hasattr(variable, 'label'):
                    variable.label.update()

    def set_label_data(self, e):

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.artist.get_visible() or \
                e.mouseevent.key is None:
            return

        function, variable = self._get_function_and_variable_from_artist(e.artist)
        if not variable or not hasattr(variable, 'label'):
            return

        data = variable.label._data if not variable.label._data is None else ''
        if e.mouseevent.key == 'backspace':
            data = data[:-1]
        elif e.mouseevent.key == 'delete':
            data = ''
        elif len(e.mouseevent.key) > 1:
            return
        else:
            data += e.mouseevent.key

        if not variable.label.validate(data):
            return

        variable.label.set_data(data)

        self.fig.canvas.draw()

    def _get_function_and_variable_from_artist(self, artist):

        for function in self.functions:
            for variable in function:
                if (variable.artist is artist) or \
                        (hasattr(variable, 'label') and \
                        variable.label.artist is artist):
                    return function, variable

        return None, None
