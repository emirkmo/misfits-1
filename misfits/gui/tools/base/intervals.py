from matplotlib import cm

from .base import Base
from ...plot import ErrorSnake

class BaseIntervals (Base) :

  def __init__(self, gui, spectrum, method):

    self.fig, self.ax = gui.fig, gui.ax
    self.gui, self.spectrum, self.method = gui, spectrum, method

    self.artists = dict()
    self.artists['spectrum'] = ErrorSnake(gui.ax[0], spectrum)

    self.intervals = list()
    self._active_interval, self._selected_interval, self._current_interval = None, None, None

    self.fig.canvas.mpl_connect('button_press_event', lambda e: self.add_interval(e))
    self.fig.canvas.mpl_connect('motion_notify_event', lambda e: self.set_interval(e))
    self.fig.canvas.mpl_connect('motion_notify_event', lambda e: self.pick_interval(e))
    self.fig.canvas.mpl_connect('button_press_event', lambda e: self.del_interval(e))

  def new_interval(self):

    return BaseInterval(self)

  def add_interval(self, e):

    if not e.inaxes is self.ax[0] or \
            not e.button == 1:
        return

    for interval in self.intervals:
      interval.set_visible(False)

    interval = self.new_interval()
    interval.set_data(x0=e.xdata, xx=e.xdata)

    self.intervals.append(interval)
    self.intervals.sort(key=lambda i: i.x0)
    self._active_interval = interval

    self.set_interval(e)

  def set_interval(self, e):

    if not self._active_interval or \
            not e.inaxes is self.ax[0]:
        return
    if not e.button == 1:
        self._active_interval = None
        return

    self._active_interval.set_data(xx=e.xdata)
    self._update_colors()

    self.gui.set_limits(self.ax[1])
    self.fig.canvas.draw()

  def pick_interval(self, e):

    if not e.inaxes is self.ax[0] or \
            self._active_interval:
        return

    intervals = [interval for interval in self.intervals if interval.in_interval(e.xdata)]
    intervals.sort(key=lambda i: e.xdata - i.x0)

    if not intervals:
        self._current_interval = None
        return
    if self._current_interval is intervals[0]:
        return

    self.show_interval(intervals[0])

  def show_interval(self, interval):

    self._current_interval = interval
    self._selected_interval = interval

    for interval in self.intervals:
      interval.set_visible(False)
    self._current_interval.set_visible(True)

    self.gui.set_limits(self.ax[1])
    self.fig.canvas.draw()

  def del_interval(self, e):

    if not self._current_interval or \
            not e.inaxes is self.ax[0] or \
            not e.button == 3:
        return

    self.intervals.remove(self._current_interval)
    self._current_interval.delete()
    self._current_interval = None
    self._selected_interval = None

    self._update_colors()

    self.gui.set_limits(self.ax[1])
    self.fig.canvas.draw()

  def _update_colors(self):

    N = len(self.intervals)

    for i, interval in enumerate(self.intervals):

      color = cm.get_cmap('gist_rainbow')(1.*i/N)
      interval.set_color(color)

  def __iter__(self):

    return iter(self.intervals)
