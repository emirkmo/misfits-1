from sys import version_info

if version_info.major == 3:
    from tkinter import *
else:
    from Tkinter import *

class ScrollText (Frame) :

    def __init__(self, *args, **kwargs):

        Frame.__init__(self, *args, **kwargs)

        self.text = Text(self, highlightbackground='gray', highlightthickness=1)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(self, command=self.text.yview)
        self.text['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side=RIGHT, fill=Y)

    def set_width(self, width):

        self.text.configure(width=width)

    def set_text(self, text):

        self.text.configure(state='normal')
        self.text.delete('1.0', END)
        self.text.insert(INSERT, text)
        self.text.configure(state='disabled')
