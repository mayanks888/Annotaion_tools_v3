import os

import cv2
import pandas as pd

# root=''
# root = "/home/mayank_sati/Desktop/one_Shot_learning/xshui"
root = "/home/mayank_s/playing_git/new/snowball/modules/perception/src/oneshot/oneshot/data/gstreet/googlestreet"

# root = "/media/mayank_sati/DATA/datasets/one_shot_datasets/Farmington/images/2019-09-27-14-39-41_test"
# csv_path="/home/mayanksati/Documents/Rosbag_files/short_range_images/gwm_data_train.csv"
# csv_path = '/home/mayank_sati/Desktop/git/2/AI/Annotation_tool_V3/system/Labels/xshui.csv'
csv_path = '/home/mayank_s/playing_git/new/snowball/modules/perception/src/oneshot/oneshot/data/gstreet/googlestreet_eval_farm.csv'
# csv_path = '/media/mayank_sati/DATA/datasets/one_shot_datasets/Farmington/images/new_farm_imageS_with_correct_box_n_qual/2019-09-27-14-39-41_test.csv'
saving_path = "/home/mayank_sati/Desktop/gt/"
data = pd.read_csv(csv_path)
# mydata = data.groupby('img_name')
mydata = data.groupby(['img_name'], sort=True)
# print(data.groupby('class').count())
len_group = mydata.ngroups
mygroup = mydata.groups
# new = data.groupby(['img_name'])['class'].count()
###############################################3333
x = data.iloc[:, 0].values
y = data.iloc[:, 5:10].values
##################################################
loop = 0
for ind,da1 in enumerate(sorted(mygroup.keys())):
    loop += 1
    print(loop)
    index = mydata.groups[da1].values
    da = os.path.join(root, da1)
    # image_scale = cv2.imread(image_path, 1)
    image_scale = cv2.imread(da, 1)
    for read_index in index:
        # print(index)
        top = (y[read_index][0], y[read_index][3])
        bottom = (y[read_index][2], y[read_index][1])
        cv2.rectangle(image_scale, pt1=top, pt2=bottom, color=(0, 255, 0), thickness=2)
        # cv2.putText(image_scale, y[read_index][4], ((y[read_index][0]+y[read_index][2])/2, y[read_index][1]), cv2.CV_FONT_HERSHEY_SIMPLEX, 2, 255)
        cv2.putText(image_scale, str(y[read_index][4]),
                    ((y[read_index][0] + y[read_index][2]) / 2, y[read_index][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5,
                    (0, 255, 0), lineType=cv2.LINE_AA)
        y[read_index][0]
        # print(da)
        # break
    if ind>0:
        cv2.imshow('streched_image', image_scale)
        ch = cv2.waitKey(1000)
        if ch & 0XFF == ord('q'):
            cv2.destroyAllWindows()
    # cv2.waitKey(1)
    # cv2.destroyAllWindows()
    output_path = saving_path + da1
    #
    # cv2.imwrite(output_path, image_scale)
    # cv2.destroyAllWindows()
