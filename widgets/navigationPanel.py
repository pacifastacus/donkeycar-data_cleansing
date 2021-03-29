import tkinter as tk

class NavPanel(tk.Frame):
    def __init__(self, master, callbackPrev, callbackNext, incVar):
        tk.Frame.__init__(self, master)
        self.prev_button = tk.Button(self, text="<<", command=callbackPrev)
        self.next_button = tk.Button(self, text=">>", command=callbackNext)
        self.step_scale = tk.Scale(self, label="step increment", orient=tk.HORIZONTAL,
                                   from_=1, to=100, resolution=1, variable=incVar)
        self.step_scale.pack(side=tk.TOP, anchor=tk.CENTER)
        self.prev_button.pack(side=tk.LEFT, anchor=tk.E)
        self.next_button.pack(side=tk.RIGHT, anchor=tk.W)
