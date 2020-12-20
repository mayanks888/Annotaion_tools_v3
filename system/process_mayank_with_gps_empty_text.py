import glob
import os

import natsort
import pandas as pd

filename = []
width = 0
height = 0
Class = []
xmin = []
ymin = []
xmax = []
ymax = []
light_color = []
bblabel = []
loop = 1

############################################33
# file_dir = '/home/mayank_sati/Desktop/git/2/AI/Annotation_tool_V3/system/Labels/2019-09-27-14-39-41/'
# file_dir = '/home/mayank_sati/codebase/git/AI/Annotation_tool_V3/system/Labels/2019-09-27-14-39-41_test'
file_dir = './Labels/farm_2_images2_scaled'
filelist = glob.glob(os.path.join(file_dir, '*.txt'))
filelist = natsort.natsorted(filelist, reverse=False)
if len(filelist) == 0:
    print 'No .txt files found in the specified dir!'
for files in filelist:
    # if os.path.exists(labelfilename):
    title, ext = os.path.splitext(os.path.basename(files))
    with open(files) as f:
        for (i, line) in enumerate(f):
            file_data = line.strip().split()
            img_name = title + ".jpg"
            # obj_class=file_data[0]
            obj_class = "traffic_light"
            # xmin = int(float(file_data[1]))
            # ymin = int(float(file_data[2]))
            # xmax = int(float(file_data[3]))
            # ymax = int(float(file_data[4]))

            xmin = int(float(file_data[1])*1.5)
            ymin = int(float(file_data[2])*1.5)
            xmax = int(float(file_data[3])*1.5)
            ymax = int(float(file_data[4])*1.5)


            time_stamp = title.split("_")[0]
            x_pos = title.split("_")[1]
            y_pos = title.split("_")[2]
            obj_id = file_data[5]
            if obj_id == '5055':
                continue
            data_label = [img_name, time_stamp, width, height, obj_class, xmin, ymin, xmax, ymax, obj_id, x_pos, y_pos]
            # data_label = [img_name, time_stamp, width, height, obj_class, xmin*1.5, ymin*1.5, xmax*1.5, ymax*1.5, obj_id, x_pos, y_pos]
            bblabel.append(data_label)
#################################################

columns = ['img_name', 'time_stamp', 'width', 'height', 'obj_class', 'xmin', 'ymin', 'xmax', 'ymax', 'obj_id', 'x_pos',
           'y_pos']

df = pd.DataFrame(bblabel, columns=columns)
print("into csv file")
# df.to_csv('template-traffic_light.csv', index=False)
csv_name = file_dir.split("/")[-1]
csv_name = file_dir + ".csv"
df.to_csv(csv_name, index=False)

#
# for section in cfg:
#     print(section)
#     loop += 1
#     xmax = section['boxes'][0]['boxes']['xmax']
#     xmin = section['boxes'][0]['boxes']['xmin']
#     ymax = section['boxes'][0]['boxes']['ymax']
#     ymin = section['boxes'][0]['boxes']['ymin']
#     height = section['boxes'][0]['boxes']['height']
#     width = section['boxes'][0]['boxes']['width']
#     # ___________________________________________
#     # playing with file
#     file_path = section['path']
#     file_name = file_path.split("/")[-1]
#     new_path = image_path + "/" + file_name
#     file_path = new_path
#     data_label = [file_path, width, height, object_name, xmin, ymin, xmax, ymax]
#     if not ((xmin == xmax) and (ymin == ymax)):
#         bblabel.append(data_label)
#         # print()
#     # if loop>=1018:
#     #     break
#
# columns = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
#
# df = pd.DataFrame(bblabel, columns=columns)
# print("into csv file")
# df.to_csv('square3_3.csv', index=False)
