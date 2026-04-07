#!/usr/bin/env python3
#coding=utf-8
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2

def Cam_RGB_Callback(msg):
    bridge = CvBridge()
    try:
        cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
    except CvBridgeError as e:
        rospy.logerr("ERROR: %s", e)
        return
    
    # 显示图像
    cv2.imshow("Camera RGB Image", cv_image)
    cv2.waitKey(1)

if __name__ == '__main__':
    rospy.init_node('image_node')
    pub = rospy.Subscriber("/kinect2/qhd/image_color_rect", Image,Cam_RGB_Callback, queue_size=10)
    rospy.spin()