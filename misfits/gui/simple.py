import os, sys

import numpy as np

if sys.version_info.major == 3:
    from tkinter import *
    from tkinter import filedialog
else:
    from Tkinter import *
    import tkFileDialog as filedialog

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Cursor
from matplotlib.transforms import CompositeGenericTransform
from matplotlib.gridspec import SubplotSpec

from .scrolltext import ScrollText

class Simple (Tk) :

    def __init__(self, *args, **kwargs):

        Tk.__init__(self, *args, **kwargs)
        self.title('misfits')
        self.configure(background='white')

        left = Frame(self, name='canvas', background='white')

        self.fig, self.ax, self.cursor = Figure(), [], []
        self.fig.set_facecolor('white')
        self.fig.subplots_adjust(top=.92, bottom=.12, right=.93, left=.13, hspace=.25)

        self.canvas = FigureCanvasTkAgg(self.fig, master=left)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

        self.zoomable = {}
        self.canvas.mpl_connect('scroll_event', self.zoom)
        self.canvas.mpl_connect('button_press_event', self.zoom)

        left.pack(side=LEFT, fill=BOTH, expand=True)

        Frame(self, background='white', width=30).pack(side=RIGHT, fill=Y)

        right = Frame(self, background='white')

        self.text = ScrollText(right, background='white')
        self.text.set_width(32)
        self.text.pack(side=TOP, fill=BOTH, expand=True, pady=10)

        self.bind('<Control-s>', self.save_figure)

        self.on_quit = lambda: None
        quit = lambda: (self.quit(), self.destroy()) if self.on_quit() is None else None

        self.protocol('WM_DELETE_WINDOW', sys.exit)
        self.quit_button = Button(right, text='Done', state=DISABLED, command=quit)
        self.quit_button.pack(side=BOTTOM, fill=X, pady=10)

        right.pack(side=RIGHT, fill=Y, pady=20)

        def toggle_menu():

            try:
                self.menu[1].pack_info()
            except:
                self.menu[1].pack()
            else:
                self.menu[1].pack_forget()

        self.menu = [Frame(left, background='white')]
        self.menu.append(Frame(self.menu[0], width=150))
        self.menu[1].pack_propagate(False)
        Button(self.menu[0], text='^', command=toggle_menu).pack(side=BOTTOM, anchor=SW)

    def _add_menu_item(self):

        if not self.menu[0].place_info():
            self.menu[0].place(relx=.023, rely=.97, anchor=SW)

        self.menu[1].pack_propagate(True)
        self.menu[1].pack()

        self.update()

        self.menu[1].config(height=self.menu[1].winfo_height())
        self.menu[1].pack_forget()
        self.menu[1].pack_propagate(False)

    def add_menu_button(self, text, command):

        button = Button(self.menu[1], text=text, command=command)
        button.pack(side=TOP, fill=X, padx=1, pady=1)

        self._add_menu_item()

    def add_menu_scale(self, text, limits, value, command):

        resolution = (limits[1]-limits[0]) / 1000.
        scale = Scale(self.menu[1], label=text, from_=limits[0], to=limits[1], resolution=resolution,
                      highlightthickness=1, highlightcolor='gray', highlightbackground='gray',
                      showvalue=False, orient=HORIZONTAL, command=lambda v: command(float(v)))
        scale.set(value)
        scale.pack(side=TOP, fill=X, padx=1, pady=1)

        self._add_menu_item()

    def add_menu_checkbox(self, text, bstate, command):

        state = IntVar(); state.set(bstate)

        checkbutton = Checkbutton(self.menu[1], text=text, variable=state,
                                  command=lambda: command(bool(state.get())))
        checkbutton.pack(side=LEFT, fill=X, padx=1, pady=1)

        self._add_menu_item()

    def add_subplot(self, position, zoomable=False, cursor=False):

        if type(position) is SubplotSpec:
            self.ax.append(self.fig.add_subplot(position))
        else:
            if type(position) is int:
                position = [position]
            self.ax.append(self.fig.add_subplot(*position))

        self.zoomable[self.ax[-1]] = zoomable

        if cursor:
            horizOn = True if cursor in ('horisontal', 'both') else False
            vertOn = True if cursor in ('vertical', 'both') else False
            cursor = Cursor(self.ax[-1], horizOn=horizOn, vertOn=vertOn, useblit=True, color='black', lw=1)
            self.cursor.append(cursor)

        return self.ax[-1]

    def save_figure(self, e):

        filetypes = [
            ('Portable Network Graphics (*.png)', '*.png'),
            ('Encapsulated Postscript (*.eps)', '*.eps'),
            ('Portable Document Format', '*.pdf'),
            ('PGF code for LaTeX (*.pgf)', '*.pgf'),
            ('Postscript (*.ps)', '*.ps'),
            ('Raw RGBA bitmap (*.raw, *.rgba)', '*.raw, *.rgba'),
            ('Scalable Vector Graphics (*.svg, *.svgz)', '*.svg, *.vgz'),
        ]

        filename = filedialog.asksaveasfilename(parent=self, initialdir=os.getcwd(),
            title='Save the figure', filetypes=filetypes)

        if filename:
            self.fig.savefig(filename)

    def set_text(self, text):

        self.text.set_text(text)

    def set_title(self, ax, title, x=.95, y=.9):

        bbox = dict(boxstyle='square', ec='white', fc='white', alpha=.7)
        ax.text(x, y, title, fontsize=10, weight='bold', transform=ax.transAxes,
                va='top', ha='right', bbox=bbox)

    def set_limits(self, ax, x0=None, xx=None, y0=None, yy=None):

        _x0, _xx, _y0, _yy = np.inf, -np.inf, np.inf, -np.inf

        for artist in ax.lines + ax.patches:

            if not artist.get_visible() or \
                not type(artist.get_transform()) is CompositeGenericTransform or \
                (hasattr(artist, 'zoom_ignore') and artist.zoom_ignore is True):
                    continue

            if hasattr(artist, 'get_data'):
                x, y = map(lambda v: np.append([], v), artist.get_data())
            elif hasattr(artist, 'get_xy'):
                x, y = map(lambda v: np.append([], v), artist.get_xy().T)
            else:
                continue

            if not (len(x) and len(y)):
                continue
            i = np.arange(len(x))

            if not x0 is None:
                i = i[np.where(x0 <= x[i])]
            if not xx is None:
                i = i[np.where(x[i] <= xx)]
            if not y0 is None:
                i = i[np.where(y0 <= y[i])]
            if not yy is None:
                i = i[np.where(y[i] <= yy)]

            if x0 is None:
                _x0 = np.min(np.append(x[i], _x0))
            if xx is None:
                _xx = np.max(np.append(x[i], _xx))
            if y0 is None:
                _y0 = np.min(np.append(y[i], _y0))
            if yy is None:
                _yy = np.max(np.append(y[i], _yy))

        if x0 is None and xx is None:
            x0, xx = _x0 - .03*(_xx-_x0), _xx + .03*(_xx-_x0)
        elif x0 is None:
            x0 = _x0 - .03*(xx-_x0)
        elif xx is None:
            xx = _xx + .03*(_xx-x0)

        if y0 is None and yy is None:
            y0, yy = _y0 - .05*(_yy-_y0), _yy + .05*(_yy-_y0)
        elif y0 is None:
            y0 = _y0 - .05*(yy-_y0)
        elif yy is None:
            yy = _yy + .05*(_yy-y0)

        if np.isfinite(x0 + xx) and x0 < xx:
            ax.set_xlim(x0, xx)
        if np.isfinite(y0 + yy) and y0 < yy:
            ax.set_ylim(y0, yy)

        self.canvas.draw()

    def zoom(self, e):

        ax = e.inaxes
        if not ax:
            return

        zoomable = self.zoomable[ax]
        if not zoomable:
            return

        x, (x0, xx) = e.xdata, ax.get_xlim()
        y, (y0, yy) = e.ydata, ax.get_ylim()

        if zoomable == 'horizontal':

            if e.button == 2: # center
                x0, xx = x - (xx-x0)/2, x + (xx-x0)/2
            elif e.button == 'down':
                x0, xx = x - 0.8*np.abs(x-x0), x + 0.8*np.abs(xx-x)
            elif e.button == 'up':
                x0, xx = x - 1.2*np.abs(x-x0), x + 1.2*np.abs(xx-x)

        elif zoomable == 'right':

            x = x0
            if e.button == 'down':
                x0, xx = x - 0.8*np.abs(x-x0), x + 0.8*np.abs(xx-x)
            elif e.button == 'up':
                x0, xx = x - 1.2*np.abs(x-x0), x + 1.2*np.abs(xx-x)

        self.set_limits(ax, x0=x0, xx=xx)

    def mainloop(self):

        self.quit_button.config(state='normal')

        Tk.mainloop(self)
