import os.path
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


counter = 0


def get_iou(a, b, epsilon=1e-5):
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


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print ("This is a  script will track a given bounding box.")
        print ("Please set the path to input bag file!")
        print ("script.py path_to_input_bagfile")
        quit()
    # *********************************
    threshold = 0.70
    # ***********************************
    bag_name_in = sys.argv[1]
    bbox_previous = np.array([0, 0, 0, 0])
    tracker = re3_tracker.Re3Tracker()
    flag = True
    yaml_list = []
    CWD_PATH = os.getcwd()
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
    b = None

    info_dict = yaml.load(rosbag.Bag(bag_name_in, 'r')._get_yaml_info())

    mytopic = "/apollo/sensor/camera/traffic/image_short"
    # +++++++++++++++++++++++++++++++++++++++++++++++=
    for topic, msg, t in rosbag.Bag(bag_name_in).read_messages():
        if topic == mytopic:
            if flag == True:
                msg.encoding = 'yuv422'
                bridge = cv_bridge.CvBridge()
                cv_img = bridge.imgmsg_to_cv2(msg, ''
                                                   '')
                cv_img = cv2.cvtColor(cv_img, cv2.COLOR_YUV2BGR_YUY2)
                b = bag_reader(cv_img)
                b.select_crop()
                bbox = b.select_box()
                image = b.return_frame()
                # cv2.destroyAllWindows()
                p1 = (int(bbox[0]), int(bbox[1]));
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                initial_bbox = [p1[0], p1[1], p2[0], p2[1]]
                tracker.track('ball', image, initial_bbox)
                flag = False
                bbox_previous = initial_bbox

            counter += 1
            # print("Image_count : ", counter)
            b.preprocess(msg)
            image = b.cropak()
            image_name = "gwm_" + str(counter) + ".jpg"
            save_path = os.path.join(image_crop_path, image_name)
            cv2.imwrite(save_path, image)
            # image = cv2.imread(image_path)
            # Tracker expects RGB, but opencv loads BGR.
            imageRGB = image[:, :, ::-1]
            bbox = tracker.track('ball', imageRGB)
            bbox = map(int, bbox)
            iou = get_iou(bbox, bbox_previous)
            print ("Running iou", iou)
            bbox_previous = bbox
            cv2.rectangle(image, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), [0, 0, 255], 2)
            cv2.imshow('Image', image)
            cv2.waitKey(150)
            cv2.destroyAllWindows()
            if iou < threshold:
                flag = True
                continue

            annotated_images = annotated_file_path + "/out_" + str(counter) + ".jpg"

            cv2.imwrite(annotated_images, image)
            object_name = "traffic_light"
            file_name = save_path
            width, height = 500, 500

            xmin, ymin, xmax, ymax = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            data_label = [image_name, width, height, object_name, xmin, ymin, xmax, ymax]
            if not ((xmin == xmax) and (ymin == ymax)):
                if (xmin < 0 or xmax > 500 or ymin < 0 or ymax > 500):
                    print(xmin, ymin, xmax, ymax)
                    flag = True
                    continue
                yaml_data = b.add_to_yaml(data_label)
                yaml_list.append(yaml_data)
                yaml_file_path = os.path.join(CWD_PATH, "rosbag_annotation.yaml")
                if os.path.isfile(yaml_file_path):
                    os.remove(yaml_file_path)
                with open(yaml_file_path, 'a') as outfile:
                    yaml.dump(yaml_list, outfile)
                print ("Processed " + str(counter) + " image messages!")
            # if counter>30:
            #     break
