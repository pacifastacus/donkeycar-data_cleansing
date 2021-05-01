#!/usr/bin/env python3
import math
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import json
import csv
import os.path
from PIL import Image, ImageTk

from AppFrames import ImageFrame, ControlFrame

WHEELS_TURNING_ANGLE = 45
THROTTLE_MAX_RADIUS = 120

LABEL_MAP = {0: "Bad",
             1: "Good",
             255: "Unlabelled"}
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


        # Application state vars
        self.loaded_json = None
        self.datadir = directory
        self.data = self.load_labeldoc(directory + '_filter.csv')
        self.FRAME_COUNT = findFirstNonClassified(self.data)
        # End of Internal variables


        # Image view panel
        self.img_frame = ImageFrame(self)
        self.img_frame.pack(side=tk.TOP, **tk_pack_options)
        # End of Image view panel

        # Control panel
        self.ctrl_frame = ControlFrame(self)
        self.ctrl_frame.pack(side=tk.BOTTOM, expand=1, fill=tk.X)
        self.ctrl_frame.classify_frame.good_button.bind("<Button>",self.mark_good())
        self.ctrl_frame.classify_frame.bad_button.bind("<Button>", self.mark_bad())
        self.ctrl_frame.classify_frame.unmark_button.bind("<Button>", self.unmark())

        # End of control panel

        # Load the first image then fit the canvas to the image
        self.__show_frame()
        self.img_frame.canvas.config(width=self.loaded_img.width(), height=self.loaded_img.height())

    def __del__(self):
        self.save_labeldoc()

    def __load_image(self):
        # fname = self.data[self.FRAME_COUNT][0]
        fname = os.path.join(self.datadir, self.loaded_json["cam/image_array"])
        self.loaded_img = ImageTk.PhotoImage(Image.open(fname, "r"))
        self.img_frame.img_fname.set(fname)

    def __load_json(self):
        fname = self.data[self.FRAME_COUNT][0]
        with open(fname) as f:
            self.loaded_json = json.load(f)


    def __show_frame(self):
        # global lmain
        self.__load_json()
        self.__load_image()
        self.ctrl_frame.classify_frame.img_class.set(LABEL_MAP[self.data[self.FRAME_COUNT][1]])
        self.img_frame.canvas.create_image(0, 0, anchor='nw', image=self.loaded_img)
        x1 = 80
        y1 = 120
        throttle = self.loaded_json["user/throttle"] * THROTTLE_MAX_RADIUS
        angle = self.loaded_json["user/angle"] * WHEELS_TURNING_ANGLE
        x2, y2 = polar2cartesian(throttle, angle)
        x2, y2 = y2 + x1, y1 - x2

        self.img_frame.canvas.create_line(x1, y1, x2, y2, fill="red", width=2, arrow=tk.LAST)


    def call_hotkey(self, event):
        key = event.keysym
        switch = {
            "0": self.mark_bad,
            "1": self.mark_good,
            "Delete": self.unmark,
            "Left": self.ctrl_frame.nav_frame.call_prev_frame,
            "Right": self.ctrl_frame.nav_frame.call_next_frame,
            "q": self.quit
        }
        try:
            switch[key]()
            if key in ["0", "1", "Delete"]:
                self.ctrl_frame.nav_frame.call_next_frame()
        except ValueError:
            return

    def mark_good(self):
        self.data[self.FRAME_COUNT][1] = 1
        increment = self.ctrl_frame.nav_frame.frame_increment.get()
        if increment > 1:
            for i in range(self.FRAME_COUNT, self.FRAME_COUNT+increment):
                self.data[i][1] = 1
        self.ctrl_frame.classify_frame.img_class.set(LABEL_MAP[1])

    def mark_bad(self):
        self.data[self.FRAME_COUNT][1] = 0
        increment = self.ctrl_frame.nav_frame.frame_increment.get()
        if increment > 1:
            for i in range(self.FRAME_COUNT, self.FRAME_COUNT + increment):
                self.data[i][1] = 0
        self.ctrl_frame.classify_frame.img_class.set(LABEL_MAP[0])

    def unmark(self):
        self.data[self.FRAME_COUNT][1] = 255
        increment = self.ctrl_frame.nav_frame.frame_increment.get()
        if increment > 1:
            for i in range(self.FRAME_COUNT, self.FRAME_COUNT + increment):
                self.data[i][1] = 255
        self.ctrl_frame.classify_frame.img_class.set(LABEL_MAP[255])


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
    root.resizable(0, 0)
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

    app.bind("1", app.call_hotkey)
    app.bind("0", app.call_hotkey)
    app.bind("<Delete>", app.call_hotkey)
    app.bind("<Left>", app.call_hotkey)
    app.bind("<Right>", app.call_hotkey)
    app.bind("<Up>", app.ctrl_frame.nav_frame.mod_increment)
    app.bind("<Down>", app.ctrl_frame.nav_frame.mod_increment)
    app.bind("q", app.call_hotkey)
    app.focus_force()

    app.mainloop()
    app.save_labeldoc()
