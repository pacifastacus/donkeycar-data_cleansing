import tkinter as tk


class customWidget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.entry = tk.Entry(self)
        self.entry.pack()

    def get(self):
        return self.entry.get()