import tkinter as tk

class ImageFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.img_fname = tk.StringVar()
        self.loaded_img = None

        self.canvas = tk.Canvas(self, width=200, height=200, bg="green")
        self.fname_label = tk.Label(self, textvariable=self.img_fname, relief=tk.RAISED)
        self.fname_label.pack()
        self.canvas.pack()


class ControlFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.classify_frame = ClassifyControls(self)
        self.classify_frame.pack(side=tk.LEFT, expand=1, fill=tk.Y)
        self.nav_frame = NavigationControls(self)
        self.nav_frame.pack(side=tk.RIGHT, expand=1, fill=tk.Y)


class ClassifyControls(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.img_class = tk.StringVar()
        self.img_class.trace_add('write', self.__refresh_label_color)

        self.class_label = tk.Label(self, textvariable=self.img_class, relief=tk.SUNKEN)
        self.good_button = tk.Button(self, text="Good (1)")
        self.unmark_button = tk.Button(self, text="Unlabel (Del)")
        self.bad_button = tk.Button(self, text="Bad (0)")
        self.class_label.pack(side=tk.TOP, anchor=tk.CENTER)
        self.unmark_button.pack(side=tk.BOTTOM)
        self.good_button.pack(side=tk.RIGHT, anchor=tk.W)
        self.bad_button.pack(side=tk.LEFT, anchor=tk.E)

    def __refresh_label_color(self, var, indx, mode):
        label = self.img_class.get().lower()
        color = "red" if label == "bad" else "green" if label == "good" else "yellow"
        self.class_label.configure(bg=color)



class NavigationControls(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.frame_increment = tk.IntVar()

        self.prev_button = tk.Button(self, text="<<", command=self.call_prev_frame)
        self.next_button = tk.Button(self, text=">>", command=self.call_next_frame)
        self.step_scale = tk.Scale(self, label="step increment", orient=tk.HORIZONTAL,
                                   from_=1, to=100, resolution=1, variable=self.frame_increment)
        self.step_scale.pack(side=tk.TOP, anchor=tk.CENTER)
        self.prev_button.pack(side=tk.LEFT, anchor=tk.E)
        self.next_button.pack(side=tk.RIGHT, anchor=tk.W)

    def call_next_frame(self):
        increment = self.frame_increment.get()
        if increment < 1:
            increment = 1
        old_frame_count = self.FRAME_COUNT
        self.FRAME_COUNT += increment
        if self.FRAME_COUNT >= len(self.parent.data):
            self.FRAME_COUNT = 0
        #  TODO   BUG: If user sweep through the directory, the labelling will be rewritten. Find a better solution
        #        if increment >1:
        #            for i in range(old_frame_count,self.FRAME_COUNT):
        #                self.data[i][1] = self.data[old_frame_count][1]

        self.parent.__show_frame()

    def call_prev_frame(self):
        increment = self.frame_increment.get()
        if increment < 1:
            increment = 1
        self.FRAME_COUNT -= increment
        if self.FRAME_COUNT < 0:
            FRAME_COUNT = len(self.parent.data)
        self.parent.__show_frame()

    def mod_increment(self, event):
        inc = self.frame_increment.get()
        res = self.step_scale.config()['resolution'][4]
        if event.keysym == "Up":
            self.frame_increment.set(inc + res)
        elif event.keysym == "Down":
            self.frame_increment.set(inc - res)
        else:
            raise Exception()