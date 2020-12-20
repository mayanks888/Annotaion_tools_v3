import os

import cv2
import pandas as pd
import tkMessageBox
import tkSimpleDialog


def callback():
    number = tkSimpleDialog.askinteger("Integer", "Enter your Image_id")
    image_id = number
    # self.root_new.destroy()


def id_default(self):
    # id_count += 1
    image_id = self.id_count


def id_option():
    input_status = tkMessageBox.askquestion("Confirm", "save or not")
    if input_status == "yes":
        return "Y"
    else:
        return "N"


bblabel = []
# root=''

# root = "/home/mayank_sati/Desktop/one_Shot_learning/xshui"
root = "/home/mayank_s/datasets/bdd/bdd100k_images/bdd100k/images/100k/train"
# csv_path="/home/mayanksati/Documents/Rosbag_files/short_range_images/gwm_data_train.csv"
# csv_path = '/home/mayank_sati/Desktop/git/2/AI/Annotation_tool_V3/system/Labels/xshui.csv'
csv_path = '/home/mayank_s/datasets/bdd/training_set/BBD_daytime_train.csv'
# saving_path="/media/mayank_sati/DATA/datasets/one_shot_datasets/Farmington/images/annotated_farm/"
data = pd.read_csv(csv_path)
# mydata = data.groupby('img_name')
mydata = data.groupby(['filename'], sort=True)
# print(data.groupby('class').count())
len_group = mydata.ngroups
mygroup = mydata.groups
# new = data.groupby(['img_name'])['class'].count()
###############################################3333
x = data.iloc[:, 0].values
y = data.iloc[:, 4:8].values
##################################################
loop = 1
# for da1 in mygroup.keys():
for da1 in sorted(mygroup.keys()):
    index = mydata.groups[da1].values
    # filename=da
    da = os.path.join(root, da1)
    # image_scale = cv2.imread(image_path, 1)
    image_scale = cv2.imread(da, 1)
    for read_index in index:
        print(index)
        top = (y[read_index][0], y[read_index][3])
        bottom = (y[read_index][2], y[read_index][1])
        cv2.rectangle(image_scale, pt1=top, pt2=bottom, color=(0, 255, 0), thickness=2)
        # cv2.putText(image_scale, y[read_index][4], ((y[read_index][0]+y[read_index][2])/2, y[read_index][1]), cv2.CV_FONT_HERSHEY_SIMPLEX, 2, 255)
        # cv2.putText(image_scale, str(y[read_index][4]),
        #             ((y[read_index][0] + y[read_index][2]) / 2, y[read_index][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5,
        #             (0, 255, 0), lineType=cv2.LINE_AA)
        y[read_index][0]
        print(da)
        # break
    cv2.imshow('streched_image', image_scale)
    ch = cv2.waitKey(100)
    mychoice = id_option()
    if ch & 0XFF == ord('q'):
        cv2.destroyAllWindows()
    # cv2.waitKey(1)
    cv2.destroyAllWindows()
    # output_path = (os.path.join(saving_path, str(loop)+".jpg"))
    loop += 1
    # cv2.imwrite(output_path, image_scale)
    # cv2.destroyAllWindows()

    if mychoice == "Y":
        data_label = [da, mychoice]
        bblabel.append(data_label)

    # if loop>=4:
    #     break
#################################################

columns = ['img_name', "status"]

df = pd.DataFrame(bblabel, columns=columns)
print("into csv file")
# df.to_csv('template-traffic_light.csv', index=False)
# csv_name = file_dir.split("/")[-1]
csv_name = "final_farm_test.csv"
df.to_csv(csv_name, index=False)
