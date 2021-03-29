import tkinter as tk

LABEL_MAP = {0: "Bad",
             1: "Good",
             255: "Unlabelled"}


class ClassifyPanel(tk.Frame):
    def __init__(self, master, callbackGood, callbackBad, callbackUnmark):
        tk.Frame.__init__(self, master)
        self.varImgClass = tk.StringVar()
        self.varImgClass.trace_add('write', self.__refresh_label_color)

        self.label_class = tk.Label(self, textvariable=self.varImgClass, relief=tk.SUNKEN)
        self.button_good = tk.Button(self, text="Good (1)", command=callbackGood)
        self.button_unmark = tk.Button(self, text="Unlabel (Del)", command=callbackUnmark)
        self.button_bad = tk.Button(self, text="Bad (0)", command=callbackBad)
        self.label_class.pack(side=tk.TOP, anchor=tk.CENTER)
        self.button_unmark.pack(side=tk.BOTTOM)
        self.button_good.pack(side=tk.RIGHT, anchor=tk.W)
        self.button_bad.pack(side=tk.LEFT, anchor=tk.E)

    def __refresh_label_color(self,var,indx,mode):
        var_as_string = self.varImgClass.get().lower()
        color = "red" if var_as_string == "bad" else "green" if var_as_string == "good" else "yellow"
        self.label_class.configure(bg=color)

    def getLabel(self):
        return self.varImgClass.get()

    def setLabel(self,label: int):
        self.varImgClass.set(LABEL_MAP[label])