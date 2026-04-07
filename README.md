# ROS 机器人功能包集合（机器人工匠阿杰的教学实例和自己的一些拓展）

## 项目简介

这是一个基于 ROS (Robot Operating System) 的机器人开发工作空间，集成了多种传感器驱动、SLAM建图、导航、视觉检测等功能模块。

## 工作空间结构

### 传感器驱动
- **imu_pkg** - IMU惯性测量单元驱动
- **jy61p** - JY61P IMU传感器驱动
- **ldlidar_14** - LD14激光雷达驱动
- **lidar_pkg** - 激光雷达数据处理
- **vel_pkg** - 速度控制相关

### SLAM建图
- **slam_pkg** - SLAM建图功能包(hector)
- **slam2_pkg** - SLAM建图功能包(Gmapping)
### 导航功能
- **nav_pkg** - 自主导航功能包

### 视觉处理
- **cv_pkg** - 计算机视觉处理
- **img_pkg** - 图像处理
- **yolov5_ros** - YOLOv5目标检测ROS集成

### 消息定义
- **detection_msgs** - 检测相关的自定义消息类型

### 其他功能
- **atr_pkg** - ATR相关功能
- **ssr_pkg** - SSR相关功能
- **ros_tutorials** - ROS教程示例

### 机器人平台
- **wpb_home** - WPB Home机器人平台功能包集合
- **wpr_simulation** - WPR机器人仿真环境

## 环境要求

- ROS Noetic (Ubuntu 20.04)
- Python 3.x
- OpenCV
- CUDA (用于YOLOv5加速，可选,虚拟机用不到)

## 编译与运行

### 编译工作空间
```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
