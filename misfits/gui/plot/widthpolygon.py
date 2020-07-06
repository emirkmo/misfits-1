from matplotlib.patches import Polygon

class WidthPolygon (object) :

    def __init__(self, ax, x, y, *args, **kwargs):

        self.ax, self.x, self.y = ax, x, y
        self.data = list(zip(x, y)) # [(x[0],y[0])] + zip(x,y) + [(x[-1],y[-1])]

        self.polygon = Polygon(self.data, *args, **kwargs)
        self.ax.add_patch(self.polygon)
        self.continuum, = self.ax.plot([x[0], x[-1]], [y[0], y[-1]], color='black', lw=1)

    def set_data(self, x, y):

        self.data = list(zip(x,y))
        self.polygon.set_xy(self.data)
        self.continuum.set_data([[x[0], x[-1]], [y[0], y[-1]]])

    def set_color(self, color):

        self.polygon.set_facecolor(color)

    def set_visible(self, visible):

        self.polygon.set_visible(visible)
        self.continuum.set_visible(visible)

    def __setattr__(self, name, value):

        if name == 'zoom_ignore':

            self.polygon.zoom_ignore = value
            self.continuum.zoom_ignore = value

        else:

            object.__setattr__(self, name, value)

    def delete(self):

        self.ax.patches.remove(self.polygon)
        self.ax.lines.remove(self.continuum)
