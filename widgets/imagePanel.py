import tkinter as tk

class ImagePanel(tk.Frame):
    def __init__(self, master, width=200, height=200):
        tk.Frame.__init__(self, master)
        self.img_fname = tk.StringVar()
        self.canvas = tk.Canvas(self, width=width, height=height, bg="green")
        self.fname_label = tk.Label(self, textvariable=self.img_fname, relief=tk.RAISED)
        self.fname_label.pack()
        self.canvas.pack()

    def load(self,im_fname):
        self.canvas.create_image(0,0,anchor='nw',image=im_fname)