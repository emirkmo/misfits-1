from sys import version_info

from .simple import Simple

if version_info.major == 3:
    from tkinter import *
else:
    from Tkinter import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SimpleMultipage (Simple) :

    def __init__(self, *args, **kwargs):

        Simple.__init__(self, *args, **kwargs)

        self.i = None
        self.lfig = [self.fig]
        self.lax = [self.ax]
        self.lcanvas = [self.canvas]
        self.lzoomable = [self.zoomable]

        self.left = self.children['canvas']

        Frame(self.left, background='white', height=20).pack(side=BOTTOM)

        navigator = Frame(self.left, background='white')

        next_button = Button(navigator, text='Next', width=20, command=self.next_canvas)
        next_button.pack(side=RIGHT, padx=10)

        prev_button = Button(navigator, text='Previous', width=20, command=self.prev_canvas)
        prev_button.pack(side=LEFT, padx=10)

        navigator.pack(side=BOTTOM, pady=10)

        self.show_canvas_callback = lambda i: None

    def add_canvas(self):

        fig, ax, cursor = Figure(), [], []
        fig.set_facecolor('white')
        fig.subplots_adjust(top=.92, bottom=.12, right=.93, left=.13, hspace=.25)

        canvas = FigureCanvasTkAgg(fig, master=self.left)

        zoomable = {}
        canvas.mpl_connect('scroll_event', self.zoom)
        canvas.mpl_connect('button_press_event', self.zoom)

        self.lfig.append(fig)
        self.lax.append(ax)
        self.lcanvas.append(canvas)
        self.lzoomable.append(zoomable)

    def next_canvas(self):

        N = len(self.lcanvas)
        i = (self.i + 1) % N
        self.show_canvas(i)

    def prev_canvas(self):

        N = len(self.lcanvas)
        i = (self.i - 1) % N
        self.show_canvas(i)

    def show_canvas(self, i):

        self.i = i

        self.canvas.get_tk_widget().pack_forget()
        self.fig, self.ax = self.lfig[i], self.lax[i]
        self.canvas, self.zoomable = self.lcanvas[i], self.lzoomable[i]
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

        self.show_canvas_callback(i)
