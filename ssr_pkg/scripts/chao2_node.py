#!/usr/bin/env python3
# coding=utf-8

import rospy
from std_msgs.msg import String

if __name__ == '__main__':
    rospy.init_node('chao2_node')
    rospy.logwarn('人生苦短')
    pub = rospy.Publisher('chao2_topic', String, queue_size=10)
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        rospy.loginfo('I am alive!')
        msg = String()
        msg.data = '我用Python'
        pub.publish(msg)
        rate.sleep()