class Base () :

    def __init__(self, parent):

        self.fig = parent.gui.fig
        self.ax = parent.gui.ax

        self.gui = parent.gui
        self.method = parent.method
        self.spectrum = parent.spectrum
