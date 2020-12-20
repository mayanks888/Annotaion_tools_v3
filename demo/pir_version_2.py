import sys

basedir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(basedir, os.path.pardir)))
from tracker import re3_tracker
import numpy as np
import os
import cv2
import cv_bridge
import yaml
import rosbag


class bag_reader():
    def __init__(self, frame):
        self.frame = frame
        self.bbox = None
        self.bbox_crop = None
        self.yaml_list = []

    def select_box(self):
        self.bbox = cv2.selectROI(self.frame, False)
        cv2.destroyAllWindows()
        return self.bbox

    def select_crop(self):
        self.bbox_crop = cv2.selectROI(self.frame, False)
        self.frame = self.frame[int(self.bbox_crop[1]):int(self.bbox_crop[1] + 500),
                     int(self.bbox_crop[0]):int(self.bbox_crop[0] + 500)]  # forces to be square (keep y)
        cv2.destroyAllWindows()

    def cropak(self):
        self.frame = self.frame[int(self.bbox_crop[1]):int(self.bbox_crop[1] + 500),
                     int(self.bbox_crop[0]):int(self.bbox_crop[0] + 500)]  # forces to be square (keep y)
        return self.frame

    def return_frame(self):
        return self.frame

    def preprocess(self, msg):
        msg.encoding = 'yuv422'
        bridge = cv_bridge.CvBridge()
        cv_img = bridge.imgmsg_to_cv2(msg, 'yuv422')
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_YUV2BGR_YUY2)
        # cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        self.frame = cv2.resize(cv_img, None, fx=1, fy=1)

    def return_frame(self):
        return self.frame

    def add_to_yaml(self, data_labels):
        file_name, width, height, object_name, xmin, ymin, xmax, ymax = data_labels
        labels_list = []
        r = object_name
        o = False
        case = {"label": r, "occluded": o, 'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax, 'height': height,
                'width': width}
        data = dict(boxes=case)
        labels_list.append(data)
        save_image = file_name
        data = dict(boxes=labels_list, path=save_image)
        return data
        # self.yaml_list.append(data)

    # def return_yaml(self):
    #     return self.yaml_list


counter = 0


def get_iou(a, b, epsilon=1e-5):
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


bbox_previous = np.array([0, 0, 0, 0])
tracker = re3_tracker.Re3Tracker()
flag = True
bblabel = []
yaml_list = []
# ____________________________-
# path of bag file:
# bag_name_in = '/home/mayank_sati/Desktop/2018-11-24-09-30-09_0.bag'
bag_name_in = '/home/mayank_sati/Documents/datsets/Rosbag_files/short_range_images/2018-11-24-09-25-36_copy/2018-11-24-09-25-38_0.orig.bag'
# path for stroring data
CWD_PATH = os.getcwd()
print(CWD_PATH)
# storing Raw images
image_crop_path = CWD_PATH + "/GWM_dataset"
if not os.path.exists(image_crop_path):
    print("GWM_dataset folder not present. Creating New folder...")
    os.makedirs(image_crop_path)

# storage for annotated data
annotated_file_path = CWD_PATH + "/RE3_annotation"
if not os.path.exists(annotated_file_path):
    print("RE3_annotated folder not present. Creating New folder...")
    os.makedirs(annotated_file_path)
# bag_name_in = sys.argv[1]

b = None
info_dict = yaml.load(rosbag.Bag(bag_name_in, 'r')._get_yaml_info())

mytopic = "/apollo/sensor/camera/traffic/image_short"
# +++++++++++++++++++++++++++++++++++++++++++++++=
for topic, msg, t in rosbag.Bag(bag_name_in).read_messages():
    if topic == mytopic:
        # +++++++++++++++++++++++++++++++++++++++++++++++++++
        # image_path = image_file_path + str(counter) + '.jpg'
        if flag == True:
            ##############################################333
            msg.encoding = 'yuv422'
            bridge = cv_bridge.CvBridge()
            cv_img = bridge.imgmsg_to_cv2(msg, 'yuv422')
            cv_img = cv2.cvtColor(cv_img, cv2.COLOR_YUV2BGR_YUY2)
            b = bag_reader(cv_img)
            ######################################333333
            # fileImage="/home/mayanksati/PycharmProjects/models/tensorflow/re3-tensorflow-master/demo/baid_30.jpg"
            # cv_img=cv2.imread(fileImage)
            ########################################
            # b = bag_reader(cv_img)
            b.select_crop()
            bbox = b.select_box()
            image = b.return_frame()
            #################################################3
            # image = cv2.imread(image_path)
            # bbox = cv2.selectROI(image, False)
            # print (bbox)
            cv2.destroyAllWindows()
            p1 = (int(bbox[0]), int(bbox[1]));
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            # cv2.rectangle(image, p1, p2, (255, 0, 0), 2, 1)
            # minx = p1[0]
            # miny = p1[1]
            # maxx = p2[0]
            # maxy = p2[1]
            # print(minx, miny, maxx, maxy)
            # initial_bbox = [minx, miny, maxx, maxy]
            initial_bbox = [p1[0], p1[1], p2[0], p2[1]]
            tracker.track('ball', image, initial_bbox)
            flag = False
            bbox_previous = initial_bbox

        counter += 1
        print("Image_count : ", counter)
        ###########################################################333
        b.preprocess(msg)
        image = b.cropak()

        # image_crop_path=base_path+"Baidu_TL_dataset1"
        image_name = "/gwm_" + str(counter) + ".jpg"
        save_path = image_crop_path + image_name
        cv2.imwrite(save_path, image)
        # image = cv2.imread(image_path)
        ##############################################################3

        # Tracker expects RGB, but opencv loads BGR.
        imageRGB = image[:, :, ::-1]
        bbox = tracker.track('ball', imageRGB)
        # [int(i) for i in bbox]
        bbox = map(int, bbox)
        iou = get_iou(bbox, bbox_previous)
        # print("the current file running", image_path.split("/")[-1])
        # print("new_box_value",bbox)
        # print("prev_box_value",bbox_previous)
        print("running iou", iou)
        bbox_previous = bbox
        ###################################################################33
        cv2.rectangle(image, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), [0, 0, 255], 2)
        # annotated_images=(annotated_file_path + (image_path.split("/")[-1]))
        cv2.imshow('Image', image)
        cv2.waitKey(150)
        cv2.destroyAllWindows()
        #################################################################33
        if iou < .60:
            flag = True
            continue
        # 33###########################################################
        # annotated_images="./trackak_res1/out_"+str(counter)+".jpg"
        annotated_images = annotated_file_path + "/out_" + str(counter) + ".jpg"
        # annotated_images=os.path.join(annotated_file_path,"gwm_")
        cv2.imwrite(annotated_images, image)
        object_name = "traffic_light"
        file_name = save_path
        width, height = 500, 500
        # bbox=int(bbox)
        xmin, ymin, xmax, ymax = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        data_label = [image_name, width, height, object_name, xmin, ymin, xmax, ymax]
        # data_label = [file_name, width, height, object_name, xmin, ymin, xmax, ymax]
        if not ((xmin == xmax) and (ymin == ymax)):
            if (xmin < 0 or xmax > 500 or ymin < 0 or ymax > 500):
                print(xmin, ymin, xmax, ymax)
                flag = True
                continue
                #############################################3
                # for csv files
            bblabel.append(data_label)
            #######################################################333
            yaml_data = b.add_to_yaml(data_label)
            yaml_list.append(yaml_data)
            yaml_file_path = os.path.join(CWD_PATH, "mayank_first.yaml")
            if os.path.isfile(yaml_file_path):
                os.remove(yaml_file_path)
            print(yaml_file_path)
            with open(yaml_file_path, 'a') as outfile:
                yaml.dump(yaml_list, outfile)
            print ("Processed " + str(counter) + " image messages!")
            #############################################################
            # print(bblabel)
            # print()
        # if counter>50:
        #     break

# yaml_file_path=os.path.join(CWD_PATH, "mayank_first_old.yaml")
#
# if os.path.isfile(yaml_file_path):
#     os.remove(yaml_file_path)
# print(yaml_file_path)
# with open(yaml_file_path, 'a') as outfile:
#     yaml.dump(yaml_list, outfile)
# print ("Processed " + str(counter) + " image messages!")

# columns = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
# df = pd.DataFrame(bblabel, columns=columns )
# csv_path=os.path.join(CWD_PATH,"re3.csv")
# # df.to_csv('re3.csv',index=False)
# df.to_csv(csv_path,index=False)
