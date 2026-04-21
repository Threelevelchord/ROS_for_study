# ROS 机器人综合感知与导航系统

## 📖 项目简介

这是一个基于 **ROS (Robot Operating System)** 的综合性机器人软件开发平台,主要围绕"WPR/WPB Home"系列服务机器人构建。项目集成了多传感器驱动、环境感知、SLAM建图、自主导航以及计算机视觉功能,提供了一套完整的从底层硬件驱动到上层应用算法的解决方案,适用于室内服务机器人的开发、教学和研究。

### ✨ 核心特性

- **多传感器融合**: 支持工业相机、激光雷达、IMU等多种传感器
- **实时目标检测**: 集成YOLOv5深度学习模型进行物体识别
- **SLAM建图定位**: 支持Hector和Gmapping两种主流SLAM算法
- **自主导航规划**: 完整的导航栈集成,包含自定义局部规划器
- **Gazebo仿真环境**: 提供完整的仿真测试环境,支持Sim-to-Real开发流程
- **模块化设计**: 各功能模块独立封装,便于扩展和维护

---

## 🏗️ 工作空间结构

### 📡 传感器驱动层

| 功能包 | 说明 | 语言 |
|--------|------|------|
| **galaxy_camera_ros_driver** | 大恒银河系列工业相机ROS驱动 | C++ |
| **ldlidar_14** | 镭神智能LD14激光雷达驱动 | C++ |
| **jy61p** | JY61P IMU惯性测量单元驱动 | C++ |
| **imu_pkg** | IMU数据解析与发布节点 | C++/Python |
| **lidar_pkg** | 激光雷达数据处理节点 | C++/Python |

### 👁️ 视觉处理层

| 功能包 | 说明 | 语言 |
|--------|------|------|
| **yolov5_ros** | YOLOv5目标检测ROS集成(支持PyTorch) | Python |
| **cv_pkg** | OpenCV图像处理(HSV转换、特征提取等) | C++ |
| **img_pkg** | 基础图像处理节点 | Python |

### 🗺️ SLAM建图层

| 功能包 | 说明 | 算法 |
|--------|------|------|
| **slam_pkg** | SLAM建图功能包 | Hector SLAM |
| **slam2_pkg** | SLAM建图功能包 | Gmapping |

### 🧭 导航控制层

| 功能包 | 说明 | 语言 |
|--------|------|------|
| **nav_pkg** | 自主导航客户端(发送导航目标) | C++/Python |
| **vel_pkg** | 速度控制节点(cmd_vel指令处理) | C++/Python |
| **wpb_home/wpbh_local_planner** | 自定义局部路径规划器插件 | C++ |
| **wpb_home/wpb_home_behaviors** | 机器人行为逻辑(充电、跟随等) | C++ |

### 🤖 机器人平台

| 功能包 | 说明 |
|--------|------|
| **wpb_home** | WPB Home机器人平台完整功能栈(驱动、控制、教程) |
| **wpr_simulation** | WPR/启智机器人Gazebo仿真环境 |

### 📨 消息定义

| 功能包 | 说明 |
|--------|------|
| **detection_msgs** | 检测结果相关的自定义消息类型 |

### 🔧 其他功能模块

| 功能包 | 说明 |
|--------|------|
| **atr_pkg** | ATR相关功能节点 |
| **ssr_pkg** | SSR相关功能节点(超控、遥控等) |
| **ros_tutorials** | ROS官方教程示例代码(参考学习用) |

---

## 💻 环境要求

### 系统配置
- **操作系统**: Ubuntu 20.04 LTS
- **ROS版本**: ROS Noetic Ninjemys
- **Python版本**: Python 3.8+
- **CMake**: ≥ 3.0.2
- **编译器**: GCC/G++ (支持C++11)

### 关键依赖库
- **OpenCV**: 计算机视觉处理
- **PCL**: 点云库(激光数据处理)
- **PyTorch**: YOLOv5深度学习推理
- **Gazebo**: 物理仿真引擎
- **Galaxy SDK**: 大恒相机官方SDK(需单独安装)

### 硬件要求(可选)
- **GPU**: NVIDIA GPU + CUDA (用于YOLOv5加速,虚拟机可不用)
- **传感器**: 
  - 大恒银河系列工业相机
  - 镭神LD14激光雷达
  - JY61P IMU模块
  - WPB/WPR机器人底盘

---

## 🚀 快速开始

### 1️⃣ 环境准备

#### 安装ROS Noetic
```bash
# 添加ROS软件源
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'

# 添加密钥
sudo apt install curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -

# 安装ROS
sudo apt update
sudo apt install ros-noetic-desktop-full

# 初始化rosdep
sudo rosdep init
rosdep update

# 设置环境变量
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

#### 安装常用工具
```bash
sudo apt install python3-catkin-tools python3-rosinstall-generator python3-wstool build-essential
```

### 2️⃣ 创建工作空间

```bash
# 创建catkin工作空间
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
catkin_init_workspace

# 克隆或复制本项目代码到src目录
# (如果已有代码则跳过此步)
```

### 3️⃣ 安装依赖

```bash
cd ~/catkin_ws

# 自动安装ROS依赖
rosdep install --from-paths src --ignore-src -r -y

# 安装YOLOv5依赖(如需使用目标检测)
cd src/yolov5_ros/src/yolov5
pip3 install -r requirements.txt

# 安装仿真环境依赖
cd ~/catkin_ws/src/wpr_simulation/scripts
./install_for_noetic.sh

# 安装WPB Home依赖
cd ~/catkin_ws/src/wpb_home/wpb_home_bringup/scripts
./install_for_noetic.sh
```

### 4️⃣ 编译工作空间

```bash
cd ~/catkin_ws

# 使用catkin_make编译
catkin_make

# 或使用catkin build(推荐)
# catkin build

# 刷新环境变量
source devel/setup.bash

# 建议将source命令添加到.bashrc
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
```

---

## 🎮 运行示例

### 📷 相机驱动测试

```bash
# 启动大恒相机节点
roslaunch galaxy_camera galaxy_camera.launch

# 查看图像
rosrun image_view image_view image:=/camera/image_raw
```

### 📡 传感器数据查看

```bash
# 启动IMU节点
rosrun imu_pkg imu_node

# 启动激光雷达
rosrun ldlidar_14 ldlidar_node

# 查看传感器数据
rostopic echo /imu/data
rostopic echo /scan
```

### 👁️ YOLOv5目标检测

```bash
# 启动YOLOv5检测节点
roslaunch yolov5_ros yolov5.launch

# 修改launch文件中的input_image_topic参数以订阅不同的图像话题
```

### 🗺️ SLAM建图

#### Hector SLAM
```bash
# 启动Hector SLAM
roslaunch slam_pkg hector_slam.launch

# 使用键盘控制机器人移动建图
rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```

#### Gmapping SLAM
```bash
# 启动Gmapping SLAM
roslaunch slam2_pkg gmapping_slam.launch
```

### 🧭 自主导航

```bash
# 启动导航系统
roslaunch nav_pkg navigation.launch

# 发送导航目标(使用rviz中的2D Nav Goal工具)
# 或使用命令行客户端
rosrun nav_pkg nav_client
```

### 🎲 Gazebo仿真测试

#### 启智机器人(WPB Home)
```bash
# 简单场景
roslaunch wpr_simulation wpb_simple.launch

# SLAM建图仿真
roslaunch wpr_simulation wpb_gmapping.launch

# 导航仿真
roslaunch wpr_simulation wpb_navigation.launch

# 物品抓取演示
roslaunch wpr_simulation wpb_table.launch
rosrun wpb_home_tutorials wpb_home_grab_client
```

#### 启明1服务机器人(WPR1)
```bash
# 简单场景
roslaunch wpr_simulation wpr1_simple.launch

# SLAM建图仿真
roslaunch wpr_simulation wpr1_gmapping.launch

# 导航仿真
roslaunch wpr_simulation wpr1_navigation.launch
```

### 🎯 视觉Demo

```bash
# HSV颜色空间处理演示
rosrun img_pkg hsv_node

# 人脸检测演示
rosrun wpr_simulation demo_cv_face_detect.py

# 颜色跟踪演示
rosrun wpr_simulation demo_cv_follow.py
```

---

## 📚 学习资源

### 📖 配套教材
1. **《机器人操作系统(ROS)及仿真应用(C++)》**
2. **《轮式智能移动操作机器人技术与应用(Python)》**

### 🎬 视频课程
- **Bilibili**: [机器人操作系统ROS 快速入门教程](https://www.bilibili.com/video/BV1BP4y1o7pw/)
- **YouTube**: [ROS Quick Start Tutorial](https://www.youtube.com/watch?v=Zs3ic0Im4D8&list=PLu0hA5NOMC0lZDGBkXwTb5NGUapAeUPPp)

### 🔗 相关仓库
- **WPB Home**: https://github.com/6-robot/wpb_home.git
- **WPR Simulation**: https://github.com/6-robot/wpr_simulation.git
- **Waterplus Map Tools**: https://github.com/6-robot/waterplus_map_tools.git
- **YOLOv5官方**: https://github.com/ultralytics/yolov5

---

## ⚙️ 开发指南

### 添加新功能包

```bash
# 创建新的ROS包
cd ~/catkin_ws/src
catkin_create_pkg my_package std_msgs roscpp rospy

# 编写代码后重新编译
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### 调试技巧

```bash
# 查看所有活跃节点
rosnode list

# 查看话题列表
rostopic list

# 查看话题消息频率
rostopic hz /topic_name

# 录制bag文件
rosbag record -a

# 回放bag文件
rosbag play recording.bag

# 启动rviz可视化工具
rviz

# 启动rqt工具箱
rqt
```

---

## ⚠️ 注意事项

### 常见问题

1. **编译错误:找不到头文件**
   ```bash
   # 确保已source环境变量
   source ~/catkin_ws/devel/setup.bash
   
   # 清理并重新编译
   cd ~/catkin_ws
   rm -rf build devel
   catkin_make
   ```

2. **YOLOv5推理速度慢**
   - 使用GPU加速(需安装CUDA和cuDNN)
   - 降低输入图像分辨率
   - 使用更小的模型(yolov5s而非yolov5x)

3. **相机无法打开**
   - 检查USB权限:`sudo chmod 666 /dev/bus/usb/*/*`
   - 确认已安装大恒相机SDK
   - 检查设备连接

4. **激光雷达无数据**
   - 检查串口权限:`sudo chmod 666 /dev/ttyUSB0`
   - 确认波特率配置正确
   - 检查设备是否被其他程序占用

### 性能优化建议

- **实时性**: ROS1通信非硬实时,高速运动控制需注意延迟
- **计算资源**: YOLOv5需要较高CPU/GPU资源,嵌入式平台建议使用TensorRT加速
- **网络配置**: 多机通信时需正确配置ROS_MASTER_URI和ROS_IP

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request!

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目部分子模块遵循各自的开源许可证,详情请参阅各子目录下的LICENSE文件。

---

## 📧 联系方式

- **项目维护**: 机器人工匠阿杰
- **技术支持**: 参考配套视频课程和教材
- **社区交流**: ROS中文社区、古月居等

---

## 🌟 致谢

感谢以下开源项目的支持:
- [ROS](http://www.ros.org/)
- [YOLOv5](https://github.com/ultralytics/yolov5)
- [OpenCV](https://opencv.org/)
- [Gazebo](http://gazebosim.org/)
- [6-Robot](https://github.com/6-robot)

---

**⭐ 如果这个项目对您有帮助,请给一个Star!**
