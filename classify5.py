#!/usr/bin/env python3
import math
import tkinter as tk
import json

import numpy as np
from PIL import Image, ImageTk

WHEELS_TURNING_ANGLE = 45
THROTTLE_MAX_RADIUS = 120

LABEL_MAP = {0: "Straight",
             1: "Left",
             2: "Right",
             3: "LeftLeft",
             4: "RightRight",
             255: "Unlabelled"}
tk_pack_options={"expand":1,"fill":tk.BOTH}


def polar2cartesian(length, angle):
    angle = math.radians(angle)
    x = length*math.cos(angle)
    y = length*math.sin(angle)
    return x,y


class App(tk.Frame):
    def __init__(self, master=None, data=None):
        tk.Frame.__init__(self, master)
        self.frame_increment = tk.IntVar()
        self.data = data
        self.loaded_img = None
        self.loaded_json = None
        self.img_class = tk.StringVar()
        self.img_class.trace_add('write', self.__refresh_label_color)
        self.img_fname = tk.StringVar()
        self.canvas = None
        self.class_label = None
        self.step_scale = None
        self.FRAME_COUNT = 0
        self.pack(**tk_pack_options)
        img_frame = tk.Frame(self)
        img_frame.pack(side=tk.TOP,**tk_pack_options)
        ctrl_frame = tk.Frame(self)
        ctrl_frame.pack(side=tk.BOTTOM,expand=1,fill=tk.X)
        classify_frame = tk.Frame(ctrl_frame)
        classify_frame.pack(side=tk.LEFT,expand=1,fill=tk.Y)
        nav_frame = tk.Frame(ctrl_frame)
        nav_frame.pack(side=tk.RIGHT,expand=1,fill=tk.Y)
        self.canvas = tk.Canvas(img_frame, width=200, height=200, bg="green")
        fname_label = tk.Label(img_frame, textvariable=self.img_fname, relief=tk.RAISED)
        fname_label.pack()
        self.canvas.pack()
        # lmain = Label(img_frame)
        # lmain.pack()
        prev_button = tk.Button(nav_frame, text="<<", command=self.call_prev_frame)
        next_button = tk.Button(nav_frame, text=">>", command=self.call_next_frame)
        self.step_scale = tk.Scale(nav_frame, label="step increment", orient=tk.HORIZONTAL,
                                from_=1, to=100, resolution=1, variable=self.frame_increment)
        self.step_scale.pack(side=tk.TOP,anchor=tk.CENTER)
        prev_button.pack(side=tk.LEFT,anchor=tk.E)
        next_button.pack(side=tk.RIGHT,anchor=tk.W)
        self.class_label = tk.Label(classify_frame, textvariable=self.img_class, relief=tk.SUNKEN)
        straight_button = tk.Button(classify_frame, text="Straight (0)", command=self.mark_straight)
        unmark_button = tk.Button(classify_frame,text="Unlabel (Del)",command=self.unmark)
        left_button = tk.Button(classify_frame, text="Left (1)", command=self.mark_left)
        right_button = tk.Button(classify_frame, text="Right (2)", command=self.mark_right)
        leftleft_button = tk.Button(classify_frame, text="LeftLeft (3)", command=self.mark_leftleft)
        rightright_button = tk.Button(classify_frame, text="RightRight (4)", command=self.mark_rightright)
        self.class_label.pack(side=tk.TOP,anchor=tk.CENTER)
        unmark_button.pack(side=tk.BOTTOM)
        straight_button.pack(side=tk.BOTTOM)
        left_button.pack(side=tk.LEFT,anchor=tk.E)
        leftleft_button.pack(side=tk.LEFT)
        right_button.pack(side=tk.RIGHT, anchor=tk.W)
        rightright_button.pack(side=tk.RIGHT)
        self.__show_frame()
        self.canvas.config(width=self.loaded_img.width(), height=self.loaded_img.height())

    def __load_image(self):
        fname = self.data[self.FRAME_COUNT][0]
        self.loaded_img = ImageTk.PhotoImage(Image.open(fname, "r"))
        self.img_fname.set(fname)

    def __load_json(self):
        fname = self.data[self.FRAME_COUNT][2]
        with open(fname) as f:
            self.loaded_json = json.load(f)

    def __refresh_label_color(self,var,indx,mode):
        label = self.img_class.get().lower()
        color = "red" if label == "bad" else "green" if label == "good" else "yellow"
        self.class_label.configure(bg=color)

    def __show_frame(self):
        # global lmain
        self.__load_image()
        self.__load_json()
        self.img_class.set(LABEL_MAP[self.data[self.FRAME_COUNT][1]])
        self.canvas.create_image(0, 0, anchor='nw', image=self.loaded_img)
        x1 = 80
        y1 = 120
        #x2 = 80
        #y2 = 80
        #radangle = np.deg2rad(-1.0*round(self.loaded_json["user/angle"],2)*90)
        throttle = self.loaded_json["user/throttle"]*THROTTLE_MAX_RADIUS
        angle = self.loaded_json["user/angle"]*WHEELS_TURNING_ANGLE
        #newx2 = (x2*math.cos(radangle))-(y2*math.sin(radangle))
        #newy2 = (y2*math.cos(radangle))+(x2*math.sin(radangle))
        x3, y3 = polar2cartesian(throttle,angle)
        newx2,newy2 = y3+x1,y1-x3

        self.canvas.create_line(x1, y1, newx2, newy2,  fill="blue", width = 2, arrow=tk.LAST)
        #self.canvas.create_line(x1, y1, x2, y2,  fill="red", width = 2, arrow=tk.LAST)

    def call_next_frame(self):
        increment = self.frame_increment.get()
        if increment < 1:
            increment = 1
        self.FRAME_COUNT += increment
        if self.FRAME_COUNT >= len(self.data):
            self.FRAME_COUNT = 0
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
            "0": self.mark_straight,
            "1": self.mark_left,
            "2": self.mark_right,
            "3": self.mark_leftleft,
            "4": self.mark_rightright,
            "Delete": self.unmark,
            "Left": self.call_prev_frame,
            "Right": self.call_next_frame,
            "q": self.quit
        }
        try:
            switch[key]()
            if key in ["0", "1", "Delete"]:
                self.call_next_frame()
        except ValueError:
            return

    def mark_straight(self):
        self.data[self.FRAME_COUNT][1] = 0
        self.img_class.set(LABEL_MAP[0])

    def mark_left(self):
        self.data[self.FRAME_COUNT][1] = 1
        self.img_class.set(LABEL_MAP[1])

    def mark_right(self):
        self.data[self.FRAME_COUNT][1] = 2
        self.img_class.set(LABEL_MAP[2])

    def mark_leftleft(self):
        self.data[self.FRAME_COUNT][1] = 3
        self.img_class.set(LABEL_MAP[3])

    def mark_rightright(self):
        self.data[self.FRAME_COUNT][1] = 4
        self.img_class.set(LABEL_MAP[4])

    def unmark(self):
        self.data[self.FRAME_COUNT][1] = 255
        self.img_class.set(LABEL_MAP[255])

    def mod_increment(self, event):
        inc = self.frame_increment.get()
        res = self.step_scale.config()['resolution'][4]
        if event.keysym == "Up":
            self.frame_increment.set(inc + res)
        elif event.keysym == "Down":
            self.frame_increment.set(inc - res)
        else:
            raise Exception()


def sort_key_fname_number(e):
    import re
    e = os.path.basename(e)
    match = re.search('([^0-9]*)([0-9]+)(.*)', e)
    num = int(match[2])
    return num


def load_labeldoc(docpath, fimagelist):
    import os
    labels_ = [list(LABEL_MAP.keys())[list(LABEL_MAP.values()).index("Unlabelled")]] * len(fimagelist)
    try:
        doc = open(docpath, "r")
        doc.readline()  # Skip header
        for i, line in enumerate(doc):
            labels_[i] = int(line.split(",")[1])
        doc.close()
    except FileNotFoundError:
        pass
    return labels_


def save_labeldoc(docpath, data):
    doc = open(docpath, "w")
    print("IMAGE FILE,CLASS", file=doc)
    for entry in data:
        print("{},{}".format(entry[0], entry[1]), file=doc)
    doc.close()


if __name__ == '__main__':
    import sys, os, glob
    # Get list of images
    try:
        img_dir = 'test_dataset/img/'
    except IndexError:
        img_dir = input("dataset directory>")
    img_dir = img_dir[:-1] if img_dir[-1] == '/' else img_dir # remove the last '/' character if present
    dir_path,img_dir = os.path.split(img_dir)
    os.chdir(dir_path)
    fimage_names = glob.glob(img_dir + '/*[0-9]*.jpg')
    fimage_names.sort(key=sort_key_fname_number)

    fimages_json = glob.glob(img_dir + '/record_[0-9]*.json')
    fimages_json.sort(key=sort_key_fname_number)

    labels = load_labeldoc(img_dir+'_filter.csv', fimage_names)

    data = [list(d) for d in zip(fimage_names, labels, fimages_json)]
    del fimage_names, labels
    root = tk.Tk()
    root.geometry('400x300')
    root.resizable(0,0)
    app = App(data=data,master=root)
    app.master.title(__file__+" : "+img_dir)
    #mainmenu = tk.Menu(root)
    #mainmenu.add_command(label="Save (Ctrl+S)",command=save)
    #mainmenu.add_command(label="Load (Ctrl+O)",command=open_dialog)
    #mainmenu.add_command(label="Quit (q)",command=app.quit)
    #root.config(menu=mainmenu)

    app.bind("1", app.call_hotkey)
    app.bind("0", app.call_hotkey)
    app.bind("2", app.call_hotkey)
    app.bind("3", app.call_hotkey)
    app.bind("4", app.call_hotkey)
    app.bind("<Delete>", app.call_hotkey)
    app.bind("<Left>", app.call_hotkey)
    app.bind("<Right>", app.call_hotkey)
    app.bind("<Up>", app.mod_increment)
    app.bind("<Down>", app.mod_increment)
    app.bind("q", app.call_hotkey)
    app.focus()

    app.mainloop()

    save_labeldoc(os.path.basename(img_dir)+'_filter.csv', data)
