#!/usr/bin/env python3
# coding=utf-8

import rospy
from std_msgs.msg import String

if __name__ == '__main__':
    rospy.init_node('yao2_node')
    rospy.logwarn('人生漫长')
    pub = rospy.Publisher('yao2_topic', String, queue_size=10)
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        rospy.loginfo('I am still alive!')
        msg = String()
        msg.data = '我也用Python'
        pub.publish(msg)
        rate.sleep()