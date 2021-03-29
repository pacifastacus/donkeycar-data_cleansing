import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os.path
import math

from widgets import NavPanel,ImagePanel,ClassifyPanel,LABEL_MAP

tk_pack_options={"expand":1,"fill":tk.BOTH}
overwrite_msg = "Please overwrite this method for your needs."

class GUI(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.loaded_img = None
        self.loaded_json = None
        self.incVar = tk.IntVar()
        frame_img = tk.Frame(self)
        frame_img.pack(side=tk.TOP,**tk_pack_options)
        self.imPanel = ImagePanel(frame_img)
        self.imPanel.pack()

        frame_ctrl = tk.Frame(self)
        frame_ctrl.pack(side=tk.BOTTOM,expand=1,fill=tk.X)
        self.navPanel = NavPanel(frame_ctrl,
                                 self.callOnPrev,
                                 self.callOnNext,
                                 incVar=self.incVar)
        self.navPanel.pack(side=tk.RIGHT,expand=1,fill=tk.Y)
        self.classPanel = ClassifyPanel(frame_ctrl,
                                        self.callOnGood,
                                        self.callOnBad,
                                        self.callOnUnmark)
        self.classPanel.pack(side=tk.LEFT,expand=1,fill=tk.Y)

    def callOnPrev(self):
        print("prev",overwrite_msg)

    def callOnNext(self):
        print("next",overwrite_msg)

    def callOnGood(self):
        print("good",overwrite_msg)

    def callOnBad(self):
        print("bad",overwrite_msg)

    def callOnUnmark(self):
        print("unmark",overwrite_msg)


if __name__ == "__main__":
    def callbackprev():
        print("prev")
    def callbacknext():
        print("next")
    def callbackgood():
        print("good")
    def callbackbad():
        print("bad")
    def callbackunmark():
        print("unmark")

    callbacks = {"callbackPrev":callbackprev,
                 "callbackNext":callbacknext,
                 "callbackGood":callbackgood,
                 "callbackBad":callbackbad,
                 "callbackUnmark":callbackunmark}

    root = tk.Tk()
    root.geometry('400x300')
    root.resizable(0,0)
    root.title("widgets.GUI")
    gui = GUI(root,callbacks)
    gui.pack()
    root.mainloop()