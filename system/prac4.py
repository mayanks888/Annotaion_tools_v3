# # from tkinter import *
# # from __future__ import division
#
# import glob
# import os
# import random
# import tkMessageBox
# import tkSimpleDialog
# from Tkinter import *
#
# import cv2
# import natsort
# from PIL import Image, ImageTk
# from tracker import re3_tracker
# # pip install pillow
# from PIL import Image, ImageTk
#
#
# class Window(Frame):
#     def __init__(self, master=None):
#         Frame.__init__(self, master)
#         self.master = master
#         self.pack(fill=BOTH, expand=1)
#
#         load = Image.open("/home/mayank_sati/Desktop/av.jpg")
#         # self.curimg_w, self.curimg_h = self.load.size
#         render = ImageTk.PhotoImage(load)
#         img = Label(self, image=render)
#         img.image = render
#         img.place(x=0, y=0)
#
#
# root = Tk()
# app = Window(root)
# root.wm_title("Tkinter window")
# # root.geometry("2064x1544")
# root.geometry("3000x3000")
# root.mainloop()


from PIL import Image, ImageTk
from Tkinter import *


class ScrolledCanvas(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.master.title("Spectrogram Viewer")
        self.pack(expand=YES, fill=BOTH)
        canv = Canvas(self, relief=SUNKEN)
        canv.config(width=2064, height=1544)
        canv.config(highlightthickness=0)
        sbarV = Scrollbar(self, orient=VERTICAL)
        sbarH = Scrollbar(self, orient=HORIZONTAL)
        sbarV.config(command=canv.yview)
        sbarH.config(command=canv.xview)
        canv.config(yscrollcommand=sbarV.set)
        canv.config(xscrollcommand=sbarH.set)
        sbarV.pack(side=RIGHT, fill=Y)
        sbarH.pack(side=BOTTOM, fill=X)
        canv.pack(side=LEFT, expand=YES, fill=BOTH)
        self.im = Image.open("av.jpg")
        width, height = self.im.size
        canv.config(scrollregion=(0, 0, width, height))
        self.im2 = ImageTk.PhotoImage(self.im)
        self.imgtag = canv.create_image(0, 0, anchor="nw", image=self.im2)


ScrolledCanvas().mainloop()
