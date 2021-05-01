#!/usr/bin/env python3
import math
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import json
import csv
import os.path
from PIL import Image, ImageTk

WHEELS_TURNING_ANGLE = 45
THROTTLE_MAX_RADIUS = 120

LABEL_MAP = {2: "Straight",
             1: "Left",
             3: "Right",
             0: "LeftLeft",
             4: "RightRight",
             255: "Unlabelled"}
#Inverse mapping
LABEL_MAP_INV = {}
for k,v in LABEL_MAP.items():
    LABEL_MAP_INV[v] = k

tk_pack_options = {"expand": 1, "fill": tk.BOTH}


def sort_key_fname_number(e):
    import re
    e = os.path.basename(e)
    match = re.search('([^0-9]*)([0-9]+)(.*)', e)
    num = int(match[2])
    return num


def findFirstNonClassified(data):
    for i, rec in enumerate(data):
        if rec[1] == 255:
            return i
    return 0


def polar2cartesian(length, angle):
    angle = math.radians(angle)
    x = length * math.cos(angle)
    y = length * math.sin(angle)
    return x, y


class App(tk.Frame):
    def __init__(self, master=None, directory=None):
        tk.Frame.__init__(self, master)
        self.pack(**tk_pack_options)
        # Internal variables
        # GUI state vars
        self.img_class = tk.StringVar()
        self.img_class.trace_add('write', self.__refresh_label_color)
        self.frame_increment = tk.IntVar()
        self.img_fname = tk.StringVar()
        # Application state vars
        self.loaded_img = None
        self.loaded_json = None
        self.datadir = directory
        self.data = self.load_labeldoc(directory + '_filter.csv')
        self.FRAME_COUNT = findFirstNonClassified(self.data)
        # End of Internal variables

        self.canvas = None
        self.class_label = None
        self.step_scale = None

        # Image view panel
        img_frame = tk.Frame(self)
        img_frame.pack(side=tk.TOP, **tk_pack_options)
        self.canvas = tk.Canvas(img_frame, width=200, height=200, bg="green")
        fname_label = tk.Label(img_frame, textvariable=self.img_fname, relief=tk.RAISED)
        fname_label.pack()
        self.canvas.pack()
        # End of Image view panel

        # Control panel
        ctrl_frame = tk.Frame(self)
        ctrl_frame.pack(side=tk.BOTTOM, expand=1, fill=tk.X)
        # labelling controls
        classify_frame = tk.Frame(ctrl_frame)
        classify_frame.pack(side=tk.LEFT, expand=1, fill=tk.Y)
        self.class_label = tk.Label(classify_frame, textvariable=self.img_class, relief=tk.SUNKEN)
        straight_button = tk.Button(classify_frame, text="Straight (2)", command=self.mark_straight)
        unmark_button = tk.Button(classify_frame,text="Unlabel (Del)",command=self.unmark)
        left_button = tk.Button(classify_frame, text="Left (1)", command=self.mark_left)
        right_button = tk.Button(classify_frame, text="Right (3)", command=self.mark_right)
        leftleft_button = tk.Button(classify_frame, text="LeftLeft (0)", command=self.mark_leftleft)
        rightright_button = tk.Button(classify_frame, text="RightRight (4)", command=self.mark_rightright)
        self.class_label.grid(row=0, column=0)
        unmark_button.grid(row=0, column=1)
        straight_button.grid(row=1, column=0, columnspan=2)
        left_button.grid(row=2, column=0)
        leftleft_button.grid(row=3, column=0)
        right_button.grid(row=2, column=1)
        rightright_button.grid(row=3, column=1)
        # navigation controls
        nav_frame = tk.Frame(ctrl_frame)
        nav_frame.pack(side=tk.RIGHT, expand=1, fill=tk.Y)
        prev_button = tk.Button(nav_frame, text="<<", command=self.call_prev_frame)
        next_button = tk.Button(nav_frame, text=">>", command=self.call_next_frame)
        self.step_scale = tk.Scale(nav_frame, label="step increment", orient=tk.HORIZONTAL,
                                   from_=1, to=100, resolution=1, variable=self.frame_increment)
        self.step_scale.pack(side=tk.TOP, anchor=tk.CENTER)
        prev_button.pack(side=tk.LEFT, anchor=tk.E)
        next_button.pack(side=tk.RIGHT, anchor=tk.W)
        # End of control panel

        # Load the first image then fit the canvas to the image
        self.__show_frame()
        self.canvas.config(width=self.loaded_img.width(), height=self.loaded_img.height())

    def __del__(self):
        self.save_labeldoc()

    def __load_image(self):
        # fname = self.data[self.FRAME_COUNT][0]
        fname = os.path.join(self.datadir, self.loaded_json["cam/image_array"])
        self.loaded_img = ImageTk.PhotoImage(Image.open(fname, "r"))
        self.img_fname.set(fname)

    def __load_json(self):
        fname = self.data[self.FRAME_COUNT][0]
        with open(fname) as f:
            self.loaded_json = json.load(f)

    def __refresh_label_color(self, var, indx, mode):
        color_map = {
            "straight" : "white",
            "left" : "red",
            "leftleft" : "red",
            "right" : "blue",
            "rightright":"blue",
            "unlabelled":"yellow"
        }
        label = self.img_class.get().lower()
        self.class_label.configure(bg=color_map[label])

    def __show_frame(self):
        # global lmain
        self.__load_json()
        self.__load_image()
        self.img_class.set(LABEL_MAP[self.data[self.FRAME_COUNT][1]])
        self.canvas.create_image(0, 0, anchor='nw', image=self.loaded_img)
        x1 = 80
        y1 = 120
        throttle = self.loaded_json["user/throttle"] * THROTTLE_MAX_RADIUS
        angle = self.loaded_json["user/angle"] * WHEELS_TURNING_ANGLE
        x2, y2 = polar2cartesian(throttle, angle)
        x2, y2 = y2 + x1, y1 - x2

        self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2, arrow=tk.LAST)

    def call_next_frame(self):
        increment = self.frame_increment.get()
        if increment < 1:
            increment = 1
        old_frame_count = self.FRAME_COUNT
        self.FRAME_COUNT += increment
        if self.FRAME_COUNT >= len(self.data):
            self.FRAME_COUNT = 0
#  TODO   BUG: If user sweep through the directory, the labelling will be rewritten. Find a better solution
#        if increment >1:
#            for i in range(old_frame_count,self.FRAME_COUNT):
#                self.data[i][1] = self.data[old_frame_count][1]

        self.__show_frame()

    def call_prev_frame(self):
        increment = self.frame_increment.get()
        if increment < 1:
            increment = 1
        self.FRAME_COUNT -= increment
        if self.FRAME_COUNT < 0:
            FRAME_COUNT = len(self.data)
        self.__show_frame()

    def call_hotkey(self, event):
        key = event.keysym
        switch = {
            "2": self.mark_straight,
            "1": self.mark_left,
            "3": self.mark_right,
            "0": self.mark_leftleft,
            "4": self.mark_rightright,
            "Delete": self.unmark,
            "Left": self.call_prev_frame,
            "Right": self.call_next_frame,
            "q": self.quit
        }
        try:
            switch[key]()
            if key in ["0", "1", "2", "3", "4", "Delete"]:
                self.call_next_frame()
        except ValueError:
            return

    def __mark(self,label : int):
        self.data[self.FRAME_COUNT][1] = label
        increment = self.frame_increment.get()
        if increment > 1:
            for i in range(self.FRAME_COUNT, self.FRAME_COUNT + increment):
                self.data[i][1] = label
        self.img_class.set(LABEL_MAP[label])

    def mark_straight(self):
        self.__mark(LABEL_MAP_INV["Straight"])

    def mark_left(self):
        self.__mark(LABEL_MAP_INV["Left"])

    def mark_right(self):
        self.__mark(LABEL_MAP_INV["Right"])

    def mark_leftleft(self):
        self.__mark(LABEL_MAP_INV["LeftLeft"])

    def mark_rightright(self):
        self.__mark(LABEL_MAP_INV["RightRight"])

    def unmark(self):
        self.__mark(LABEL_MAP_INV["Unlabelled"])

    def mod_increment(self, event):
        inc = self.frame_increment.get()
        res = self.step_scale.config()['resolution'][4]
        if event.keysym == "Up":
            self.frame_increment.set(inc + res)
        elif event.keysym == "Down":
            self.frame_increment.set(inc - res)
        else:
            raise Exception()

    #    @staticmethod
    #    def load_labeldoc(self, docpath, fimagelist):
    #        labels_ = [list(LABEL_MAP.keys())[list(LABEL_MAP.values()).index("Unlabelled")]] * len(fimagelist)
    #        try:
    #            doc = open(docpath, "r")
    #            doc.readline()  # Skip header
    #            for i, line in enumerate(doc):
    #                labels_[i] = int(line.split(",")[1])
    #            doc.close()
    #        except FileNotFoundError:
    #            pass
    #        return labels_

    @staticmethod
    def load_labeldoc(docpath):
        labels_ = []
        json_files = []
        try:
            doc = open(docpath, "r")
            reader = csv.reader(doc, delimiter=",")
            next(reader, None)
            for row in reader:
                json_files.append(row[0])
                labels_.append(int(row[1]))
            doc.close()
        except FileNotFoundError:
            json_files = glob.glob(img_dir + '/record_[0-9]*.json')
            json_files.sort(key=sort_key_fname_number)
            labels_ = [list(LABEL_MAP.keys())[list(LABEL_MAP.values()).index("Unlabelled")]]
            labels_ *= len(json_files)

        return [list(d) for d in zip(json_files, labels_)]

    def save_labeldoc(self, docpath=None):
        if not docpath:
            docpath = self.datadir + '_filter.csv'
        doc = open(docpath, "w")
        print("IMAGE FILE,CLASS", file=doc)
        for entry in self.data:
            print("{},{}".format(entry[0], entry[1]), file=doc)
        doc.close()

    def open_dir(self):
        newdir = filedialog.askdirectory(mustexist=True, title="Select Directory")
        if (newdir):
            # Save work
            self.save_labeldoc()

            # go to the parent directory
            dir_path, dataset = os.path.split(newdir)
            os.chdir(dir_path)

            # Update internal vars
            self.datadir = dataset
            self.data = self.load_labeldoc(self.datadir + '_filter.csv')
            self.FRAME_COUNT = findFirstNonClassified(self.data)
            self.__show_frame()


if __name__ == '__main__':
    import sys, os, glob

    root = tk.Tk()
    root.geometry('400x300')
    root.resizable(1, 1)
    # Get list of images
    try:
        img_dir = sys.argv[1]  # 'test_data/img/'
    except IndexError:
        img_dir = filedialog.askdirectory(mustexist=True, title="Select Directory")
        if not img_dir:
            messagebox.showerror("Error!","Nothing selected! Quit")
            quit(1)
        img_dir = os.path.relpath(img_dir,os.getcwd())



    img_dir = img_dir[:-1] if (
                img_dir[-1] == '/' or img_dir[-1] == '\\') else img_dir  # remove the last '/' character if present
    dir_path, img_dir = os.path.split(img_dir)
    os.chdir(dir_path)

    app = App(master=root, directory=img_dir)
    app.master.title('Classify.py')

    mainmenu = tk.Menu(root)
    # mainmenu.add_command(label="Save (Ctrl+S)",command=save)
    mainmenu.add_command(label="Open Directory", command=app.open_dir)
    mainmenu.add_command(label="Quit (q)", command=app.quit)
    root.config(menu=mainmenu)

    app.bind("4", app.call_hotkey)
    app.bind("3", app.call_hotkey)
    app.bind("2", app.call_hotkey)
    app.bind("1", app.call_hotkey)
    app.bind("0", app.call_hotkey)
    app.bind("<Delete>", app.call_hotkey)
    app.bind("<Left>", app.call_hotkey)
    app.bind("<Right>", app.call_hotkey)
    app.bind("<Up>", app.mod_increment)
    app.bind("<Down>", app.mod_increment)
    app.bind("q", app.call_hotkey)
    app.focus_force()

    app.mainloop()
    app.save_labeldoc()
