Annotation Tool Version:3

## Implementation in progress : highy unstable :(

### Description: 
This is a latest version of annotation tool which focus mainly on multi object annotation with better gui interface


### Requirements:
1. Python 2.7
2. [Tensorflow](https://www.tensorflow.org/) and its requirements.
5. [Ros-kinetic](http://wiki.ros.org/kinetic/Installation/Ubuntu)
      : Follow the link to install ros-kinetic into your system
        
    1. sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
    2. sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
    3. sudo apt-get update
    4. sudo apt-get install ros-kinetic-desktop-full
    5. echo "source /opt/ros/kinetic/setup.bash" >> ~/.bashrc
    6. source ~/.bashrc
    7. sudo apt install python-rosinstall python-rosinstall-generator python-wstool build-essential
            
    Note:In case of any error while installing ros, follow the link(http://wiki.ros.org/kinetic/Installation/Ubuntu)
    
5. Download checkpoints from path : http://bit.ly/2L5deYF   
   `Moved checkpoints directoriry into logs folder</Annotation tool V2.2/logs>    ` 
   
    `example: /home/mayank_sati/Desktop/git/2/AI/Annotation tool V2.2/logs/checkpoints`                  
   
6. You can find other project requirements in `requirements.txt`        
   install using `pip install -r requirements.txt`
   
   
#### To check the annotation script:
follow the script at 
`Annotation_tool_V3/system/main_mayank.py`
