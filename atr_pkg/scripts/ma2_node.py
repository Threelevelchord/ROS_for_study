#!/usr/bin/env python3
# coding=utf-8
import rospy
from std_msgs.msg import String

def yao_callback(msg):
    rospy.logwarn(msg.data)

def chao_callback(msg):
    rospy.loginfo(msg.data)

if __name__ == '__main__':
    rospy.init_node('ma2_node')
    sub = rospy.Subscriber('chao2_topic', String, chao_callback, queue_size=10)
    sub2 = rospy.Subscriber('yao2_topic', String, yao_callback, queue_size=10)
    rospy.spin()