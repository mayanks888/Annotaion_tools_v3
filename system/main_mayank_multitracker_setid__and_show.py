# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
from __future__ import division

import glob
import os
import random

import cv2
import natsort
import tkMessageBox
import tkSimpleDialog
from PIL import Image, ImageTk
from Tkinter import *
from tracker import re3_tracker

# -------------------------------------------------------------------------------
# from __future__ import division

MAIN_COLORS = ['darkolivegreen', 'darkseagreen', 'darkorange', 'darkslategrey', 'darkturquoise', 'darkgreen',
               'darkviolet', 'darkgray', 'darkmagenta', 'darkblue', 'darkkhaki', 'darkcyan', 'darkred', 'darksalmon',
               'darkslategray', 'darkgoldenrod', 'darkgrey', 'darkslateblue', 'darkorchid', 'skyblue', 'yellow',
               'orange', 'red', 'pink', 'violet', 'green', 'brown', 'gold', 'Olive', 'Maroon', 'blue', 'cyan', 'black',
               'olivedrab', 'lightcyan', 'silver']
# image sizes for the examples
SIZE = 256, 256
classes = []
try:
    with open('classes.txt', 'r') as cls:
        classes = cls.readlines()
    classes = [cls.strip() for cls in classes]
except IOError as io:
    print("[ERROR] Please create classes.txt and put your all classes")
    sys.exit(1)
COLORS = random.sample(set(MAIN_COLORS), len(classes))


class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.tracker = re3_tracker.Re3Tracker()
        self.curimg_h = 0
        self.curimg_w = 0
        self.cur_cls_id = -1
        self.parent = master
        self.parent.title("GWM Annotation Tool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=FALSE, height=FALSE)
        self.meta_info = {}
        self.unq_id = []
        self.id_count = 1000

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.bboxListCls = []
        self.image_list_id = []
        self.object_id_list = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text="Image Dir:")
        self.label.grid(row=0, column=0, sticky=E)
        self.entry = Entry(self.frame)
        self.entry.focus_set()
        self.entry.bind('<Return>', self.loadEntry)
        self.entry.grid(row=0, column=1, sticky=W + E)
        self.ldBtn = Button(self.frame, text="Load", command=self.loadDir)
        self.ldBtn.grid(row=0, column=2, sticky=W + E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("<Left>", self.prevImage)  # press 'a' to go backforward
        self.parent.bind("<Right>", self.nextImage)  # press 'd' to go forward
        self.mainPanel.grid(row=1, column=1, rowspan=4, sticky=W + N)

        # showing bbox info & delete bbox
        self.tkvar = StringVar(self.parent)
        self.cur_cls_id = 0
        self.tkvar.set(classes[0])  # set the default option
        self.popupMenu = OptionMenu(self.frame, self.tkvar, *classes, command=self.change_dropdown)
        self.popupMenu.grid(row=1, column=2, sticky=E + S)
        self.chooselbl = Label(self.frame, text='Choose Class:')
        self.chooselbl.grid(row=1, column=2, sticky=W + S)
        self.lb1 = Label(self.frame, text='Bounding boxes:')
        self.lb1.grid(row=2, column=2, sticky=W + N)
        self.listbox = Listbox(self.frame, width=30, height=12)
        self.listbox.grid(row=3, column=2, sticky=N)
        self.btnDel = Button(self.frame, text='Delete', command=self.delBBox)
        self.btnDel.grid(row=4, column=2, sticky=W + E + N)
        self.btnClear = Button(self.frame, text='ClearAll', command=self.clearBBox)
        self.btnClear.grid(row=5, column=2, sticky=W + E + N)
        #####################################################33333
        self.btntrack_update = Button(self.frame, text='Update Tracker', command=self.tracker_update)
        self.btntrack_update.grid(row=7, column=2, sticky=W + E + N)
        #############################################################
        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=6, column=1, columnspan=2, sticky=W + E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width=10, command=self.prevImage)
        self.prevBtn.pack(side=LEFT, padx=5, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width=10, command=self.nextImage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=LEFT, padx=5)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image No.")
        self.tmpLabel.pack(side=LEFT, padx=5)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoImage)
        self.goBtn.pack(side=LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border=10)
        self.egPanel.grid(row=1, column=0, rowspan=5, sticky=N)
        self.tmpLabel2 = Label(self.egPanel, text="Examples: enter 'gwm'")
        self.tmpLabel2.pack(side=TOP, pady=5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side=TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side=RIGHT)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)

    def loadEntry(self, event):
        self.loadDir()

    def loadDir(self, dbg=False):
        if not dbg:
            try:
                s = self.entry.get()
                self.parent.focus()
                self.category = s
            except ValueError as ve:
                tkMessageBox.showerror("Error!", message="The folder should be numbers")
                return
        if not os.path.isdir('./Images/%s' % self.category):
            tkMessageBox.showerror("Error!", message="The specified dir doesn't exist!")
            return
        # store directory path
        self.imageDir = os.path.join(r'./Images', '%s' % (self.category))
        # get the list of the all the images
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        self.imageList = natsort.natsorted(self.imageList, reverse=False)
        if len(self.imageList) == 0:
            print 'No .jpg images found in the specified dir!'
            tkMessageBox.showerror("Error!", message="No .jpg images found in the specified dir!")
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        # set up output dir
        if not os.path.exists('./Labels'):
            os.mkdir('./Labels')
        self.outDir = os.path.join(r'./Labels', '%s' % (self.category))
        # patah for label output
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        self.loadImage()
        print '%d images loaded from %s' % (self.total, s)

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.curimg_w, self.curimg_h = self.img.size
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width=max(self.tkimg.width(), 400), height=max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.progLabel.config(text="%04d/%04d" % (self.cur, self.total))

        # load labels
        self.clearBBox()
        # self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        self.imagename = os.path.splitext(os.path.basename(imagepath))[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    yolo_data = line.strip().split()
                    # tmp = self.deconvert(yolo_data[1:])
                    tmp = [int(float(loop)) for loop in yolo_data[1:-1]]
                    self.bboxList.append(tuple(tmp))
                    self.bboxListCls.append(yolo_data[0])
                    self.image_list_id.append(yolo_data[-1])
                    # this is a most important function to update the bounding box on image
                    tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                            tmp[2], tmp[3], \
                                                            width=2, \
                                                            outline=COLORS[int(yolo_data[0])])
                    # self.mainPanel.create_text(tmp[0]+10, tmp[1]-50,text=yolo_data[-1])

                    ############333
                    self.object_id = self.mainPanel.create_text(int(tmp[2] + tmp[0]) / 2, tmp[1] - 15,
                                                                text=yolo_data[-1])
                    self.object_id_list.append(self.object_id)
                    self.object_id = None
                    ###################

                    self.bboxIdList.append(tmpId)
                    # self.listbox.insert(END, '(%d, %d) -> (%d, %d) -> (%s)->(%d)' %(tmp[0], tmp[1], tmp[2], tmp[3], classes[int(yolo_data[0])],int(yolo_data[-1])))
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)->(%d)' % (
                    tmp[0], tmp[1], tmp[2], tmp[3], int(yolo_data[-1])))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[int(yolo_data[0])])

    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            for bbox, bboxcls, imgi_d_l in zip(self.bboxList, self.bboxListCls, self.image_list_id):
                xmin, ymin, xmax, ymax = bbox
                # b = (float(xmin), float(xmax), float(ymin), float(ymax))
                bb = (float(xmin), float(ymin), float(xmax), float(ymax))
                # bb = b
                # bb = self.convert((self.curimg_w,self.curimg_h), b)
                # f.write(str(bboxcls) + " " + " ".join([str(a) for a in bb]) + str(imgi_d_l)+ '\n')
                f.write(str(bboxcls) + " " + " ".join([str(a) for a in bb]) + " " + str(imgi_d_l) + '\n')
        print 'Image No. %d saved' % (self.cur)

    # def tracker_update_2(self):
    #     self.meta_info={}
    #     # self.tracker = re3_tracker.Re3Tracker()
    #     for index,(bbox,bboxcls) in enumerate( zip(self.bboxList,self.bboxListCls)):
    #         xmin,ymin,xmax,ymax = bbox
    #         # b = (float(xmin), float(xmax), float(ymin), float(ymax))
    #         bb = [float(xmin), float(ymin), float(xmax), float(ymax)]
    #         dat = "light_" + str(index)
    #         self.meta_info.update({dat: bb})
    #     self.unq_id = self.meta_info.keys()
    #     id=self.unq_id
    #     ################################
    #     imagepath = self.imageList[self.cur - 1]
    #     image = cv2.imread(imagepath)
    #     # try:
    #     if len(id)<2:
    #         self.tracker.track('ball', image, bb)
    #     else:
    #         self.tracker.multi_track(id, image, self.meta_info)
    #     print (1)

    def tracker_update(self):
        self.meta_info = {}
        # self.tracker = re3_tracker.Re3Tracker()
        for index, (bbox, bboxcls, img_id) in enumerate(zip(self.bboxList, self.bboxListCls, self.image_list_id)):
            xmin, ymin, xmax, ymax = bbox
            # b = (float(xmin), float(xmax), float(ymin), float(ymax))
            bb = [float(xmin), float(ymin), float(xmax), float(ymax)]
            # dat = "light_" + str(index)
            dat = img_id
            self.meta_info.update({dat: bb})
        # self.unq_id = self.meta_info.keys()
        self.unq_id = self.image_list_id
        id = self.unq_id
        ################################
        imagepath = self.imageList[self.cur - 1]
        image = cv2.imread(imagepath)
        # try:
        if len(id) < 2:
            self.tracker.track('ball', image, bb)
        else:
            self.tracker.multi_track(id, image, self.meta_info)
        print (1)

    def trackImage(self):
        bbox_cnt = 0
        # if os.path.exists(self.labelfilename):
        #     with open(self.labelfilename) as f:
        #         for (i, line) in enumerate(f):
        #####################################################
        imagepath = self.imageList[self.cur]
        print("tracked for path ", imagepath)
        image = cv2.imread(imagepath)
        # Tracker expects RGB, but opencv loads BGR.
        imageRGB = image[:, :, ::-1]
        try:
            if len(self.unq_id) < 2:
                bbox_list = self.tracker.track('ball', imageRGB)
            else:
                bbox_list = self.tracker.multi_track(self.unq_id, imageRGB)
        except:
            tkMessageBox.showerror("Error!", message="Press Update Tracker!")
        ###################################################################33
        # self.imagename = os.path.splitext(os.path.basename(imagepath))[0]
        next_imagename = os.path.splitext(os.path.basename(imagepath))[0]
        labelname = next_imagename + '.txt'
        next_labelfilename = os.path.join(self.outDir, labelname)
        with open(next_labelfilename, 'w') as f:
            if len(self.unq_id) < 2:
                # for bbox, bboxcls in zip(bbox_list, self.bboxListCls):
                xmin, ymin, xmax, ymax = bbox_list
                # b = (float(xmin), float(xmax), float(ymin), float(ymax))
                bb = (float(xmin), float(ymin), float(xmax), float(ymax))
                # bb=b
                # bb = self.convert((self.curimg_w, self.curimg_h), b)
                bboxcls = 0
                imgi_d_l = self.image_list_id[-1]
                f.write(str(bboxcls) + " " + " ".join([str(a) for a in bb]) + '\n')
                f.write(str(bboxcls) + " " + " ".join([str(a) for a in bb]) + " " + str(imgi_d_l) + '\n')
                print 'Image No. %d saved' % (self.cur)
            else:
                for bbox, bboxcls, imgi_d_l in zip(bbox_list, self.bboxListCls, self.image_list_id):
                    xmin, ymin, xmax, ymax = bbox
                    # b = (float(xmin), float(xmax), float(ymin), float(ymax))
                    bb = (float(xmin), float(ymin), float(xmax), float(ymax))
                    # bb=b
                    # bb = self.convert((self.curimg_w, self.curimg_h), b)
                    bboxcls = 0
                    # f.write(str(bboxcls) + " " + " ".join([str(a) for a in bb]) + '\n')
                    f.write(str(bboxcls) + " " + " ".join([str(a) for a in bb]) + " " + str(imgi_d_l) + '\n')
                    print 'Image No. %d saved' % (self.cur)

        #######################################################################

    def callback(self):
        self.number = tkSimpleDialog.askinteger("Integer", "Enter your Image_id")
        self.image_id = self.number
        # self.root_new.destroy()

    def id_default(self):
        self.id_count += 1
        self.image_id = self.id_count

    def id_option(self):
        input_status = tkMessageBox.askquestion("Confirm", "Create custom Image_Id")
        if input_status == "yes":
            self.callback()
        else:
            self.id_default()

        # messagebox.askquestion("Confirm", "Are you sure?")

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            self.id_option()
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2))
            self.bboxListCls.append(self.cur_cls_id)
            #######################################3333'
            self.image_list_id.append(self.image_id)
            self.object_id = self.mainPanel.create_text(int(x1 + x2) / 2, y1 - 15, text=str(self.image_id))
            self.object_id_list.append(self.object_id)
            self.object_id = None
            ##############################################
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            # self.listbox.insert(END, '(%d, %d) -> (%d, %d) -> (%s)' %(x1, y1, x2, y2, classes[self.cur_cls_id]))
            # self.listbox.insert(END, '(%d, %d) -> (%d, %d) -> (%s) -> (%d)' %(x1, y1, x2, y2, classes[self.cur_cls_id],self.image_id))
            self.listbox.insert(END, '(%d, %d) -> (%d, %d) -> (%d)' % (x1, y1, x2, y2, self.image_id))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[self.cur_cls_id])
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width=2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width=2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                          event.x, event.y, \
                                                          width=2, \
                                                          outline=COLORS[self.cur_cls_id])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.mainPanel.delete(self.object_id_list[idx])
        self.image_list_id.pop(idx)
        self.bboxIdList.pop(idx)
        self.object_id_list.pop(idx)
        self.bboxList.pop(idx)
        print(self.bboxListCls, idx)
        self.bboxListCls.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
            self.mainPanel.delete(self.object_id_list[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.bboxListCls = []
        self.image_list_id = []
        self.object_id_list = []

    def prevImage(self, event=None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()
        else:
            tkMessageBox.showerror("Information!", message="This is first image")

    def nextImage(self, event=None):
        self.saveImage()
        self.trackImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()
        else:
            tkMessageBox.showerror("Information!", message="All images annotated")

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()

    def change_dropdown(self, *args):
        cur_cls = self.tkvar.get()
        self.cur_cls_id = classes.index(cur_cls)

    def convert(self, size, box):
        dw = 1. / size[0]
        dh = 1. / size[1]
        x = (box[0] + box[1]) / 2.0
        y = (box[2] + box[3]) / 2.0
        w = box[1] - box[0]
        h = box[3] - box[2]
        x = x * dw
        w = w * dw
        y = y * dh
        h = h * dh
        return (x, y, w, h)

    def deconvert(self, annbox):
        ox = float(annbox[0])
        oy = float(annbox[1])
        ow = float(annbox[2])
        oh = float(annbox[3])
        x = ox * self.curimg_w
        y = oy * self.curimg_h
        w = ow * self.curimg_w
        h = oh * self.curimg_h
        xmax = (((2 * x) + w) / 2)
        xmin = xmax - w
        ymax = (((2 * y) + h) / 2)
        ymin = ymax - h
        return [int(xmin), int(ymin), int(xmax), int(ymax)]

    def get_iou(self, a, b, epsilon=1e-5):
        """ Given two boxes `a` and `b` defined as a list of four numbers:
                [x1,y1,x2,y2]
            where:
                x1,y1 represent the upper left corner
                x2,y2 represent the lower right corner
            It returns the Intersect of Union score for these two boxes.

        Args:
            a:          (list of 4 numbers) [x1,y1,x2,y2]
            b:          (list of 4 numbers) [x1,y1,x2,y2]
            epsilon:    (float) Small value to prevent division by zero

        Returns:
            (float) The Intersect of Union score.
        """
        # COORDINATES OF THE INTERSECTION BOX
        x1 = max(a[0], b[0])
        y1 = max(a[1], b[1])
        x2 = min(a[2], b[2])
        y2 = min(a[3], b[3])

        # AREA OF OVERLAP - Area where the boxes intersect
        width = (x2 - x1)
        height = (y2 - y1)
        # handle case where there is NO overlap
        if (width < 0) or (height < 0):
            return 0.0
        area_overlap = width * height

        # COMBINED AREA
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        area_combined = area_a + area_b - area_overlap

        # RATIO OF AREA OF OVERLAP OVER COMBINED AREA
        iou = area_overlap / (area_combined + epsilon)
        return iou


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width=True, height=True)
    root.mainloop()
