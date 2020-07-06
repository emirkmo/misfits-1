from collections import OrderedDict

from matplotlib import cm

from .base import Base
from .point import BasePoint
from .point import BaseTogglePoint
from .point import BaseLabelTogglePoint
from .connection import BaseConnection

class BasePoints (Base) :

    def __init__(self, interval):

        Base.__init__(self, interval)
        self.intervals, self.interval = interval.intervals, interval

        self.points = list()

    def new_point(self):

        return BasePoint(self)

    def add_point(self, x, y):

        point = self.new_point()
        point.set_data(x, y)

        self.points.append(point)
        self.points.sort(key=lambda p: p.x)

    def del_point(self, x, y):

        i = [(point.x, point.y) for point in self.points].index((x, y))
        self.points.pop(i).delete()

    def set_data(self, points):

        _points = [(point.x, point.y) for point in self.points]
        for (x, y) in set(_points) - set(points):
            self.del_point(x, y)

        _points = [(point.x, point.y) for point in self.points]
        for (x, y) in set(points) - set(_points):
            self.add_point(x, y)

    def set_visible(self, visible):

        for point in self.points:
            point.set_visible(visible)

    def delete(self):

        for point in self.points:
            point.delete()

    def _get_point_from_artist(self, artist):

        for point in self.points:
            if point.artist is artist:
                return point

    def __iter__(self):

        return iter(self.points)

class BaseTogglePoints (BasePoints) :

    def __init__(self, interval):

        BasePoints.__init__(self, interval)

        interval.mpl_connect('pick_event', self.toggle_point)

    def new_point(self):

        return BaseTogglePoint(self)

    def toggle_point(self, e):

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.artist.get_visible() or \
                not hasattr(e.mouseevent, 'button') or \
                not e.mouseevent.button == 1:
            return

        point = self._get_point_from_artist(e.artist)
        if not point:
            return

        point.toggle()

        self._update_colors()

        self.fig.canvas.draw()

    def _update_colors(self):

        for i, point in enumerate(self.points):
            point.set_color('white')

        selected_points = [point for point in self.points if point.selected]
        N = len(selected_points)

        for i, point in enumerate(selected_points):
            color = cm.get_cmap('gist_rainbow')(1.*i/N)
            point.set_color(color)

class BaseLabelTogglePoints (BaseTogglePoints) :

    def __init__(self, interval):

        BaseTogglePoints.__init__(self, interval)

        interval.mpl_connect('key_press_event', self.fig.canvas.pick)
        interval.mpl_connect('pick_event', self.set_label_data)

    def new_point(self):

        return BaseLabelTogglePoint(self)

    def set_label_data(self, e):

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.artist.get_visible() or \
                e.mouseevent.key is None:
            return

        point = self._get_point_from_artist(e.artist)
        if not point or \
                not hasattr(point, 'label') or \
                not point.selected:
            return

        data = point.label._data if not point.label._data is None else ''
        if e.mouseevent.key == 'backspace':
            data = data[:-1]
        elif e.mouseevent.key == 'delete':
            data = ''
        elif len(e.mouseevent.key) > 1:
            return
        else:
            data += e.mouseevent.key

        if not point.label.validate(data):
            return

        point.label.set_data(data)

        self.fig.canvas.draw()

    def _get_point_from_artist(self, artist):

        for point in self.points:
            if point.artist is artist or \
                    (hasattr(point, 'label') and \
                        point.label.artist is artist):
                return point

class BaseConnectingPoints (BasePoints) :

    def __init__(self, interval):

        BasePoints.__init__(self, interval)

        self.connections = list()
        self._active_connection = None

        interval.mpl_connect('pick_event', self.add_connection)
        interval.mpl_connect('motion_notify_event', self.set_connection)
        interval.mpl_connect('pick_event', self.def_connection)
        interval.mpl_connect('pick_event', self.del_connection)

        interval.mpl_connect('button_release_event', self.fig.canvas.pick)

    def new_connection(self):

        return BaseConnection(self)

    def add_connection(self, e):

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.artist.get_visible() or \
                not e.mouseevent.name == 'button_press_event' or \
                not e.mouseevent.button == 1 or \
                self._active_connection:
            return

        point = self._get_point_from_artist(e.artist)
        if not point in self.points:
            return

        connection = self.new_connection()
        connection.point0 = point
        connection.set_data(x0=point.x, y0=point.y)
        self._active_connection = connection

        self.fig.canvas.draw()

    def set_connection(self, e):

        if not self._active_connection or \
                not e.inaxes is self.ax[1] or \
                not e.button == 1:
            return

        connection = self._active_connection
        connection.set_data(xx=e.xdata, yy=e.ydata)

        self.fig.canvas.draw()

    def def_connection(self, e):

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.artist.get_visible() or \
                not e.mouseevent.name == 'button_release_event' or \
                not self._active_connection:
            return

        connection = self._active_connection
        self._active_connection = None

        point = self._get_point_from_artist(e.artist)

        if point in self.points and not point is connection.point0:

            connection.set_data(xx=point.x, yy=point.y)
            del connection.point0

            if connection.data in [conn.data for conn in self.connections]:
                connection.delete()
            else:
                self.connections.append(connection)
                self.connections.sort(key=lambda c: c.x0)

        else:

            connection.delete()

        self._update_colors()

        self.fig.canvas.draw()

    def del_connection(self, e):

        if not e.mouseevent.inaxes is self.ax[1] or \
                not e.artist.get_visible() or \
                not e.mouseevent.button == 3:
            return

        connection = self._get_connection_from_artist(e.artist)
        if not connection:
            return

        connection.delete()
        self.connections.remove(connection)

        self._update_colors()

        self.fig.canvas.draw()

    def set_visible(self, visible):

        BasePoints.set_visible(self, visible)

        for connection in self.connections:
            connection.set_visible(visible)

    def delete(self):

        BasePoints.delete(self)

        for connection in self.connections:
            connection.delete()

    def _get_connection_from_artist(self, artist):

        for connection in self.connections:
            if connection.artist is artist:
                return connection

    def _update_colors(self):

        N = len(self.connections)

        for i, connection in enumerate(self.connections):
            color = cm.get_cmap('gist_rainbow')(1.*i/N)
            connection.set_color(color)

    def __iter__(self):

        return iter(self.connections)
