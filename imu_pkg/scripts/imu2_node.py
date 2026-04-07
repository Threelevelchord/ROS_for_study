#!/usr/bin/env python3
# coding=utf-8
import rospy
from sensor_msgs.msg import Imu
from tf.transformations import euler_from_quaternion
import math

def imuCallback(msg):
    if msg.orientation_covariance[0] < 0:
        return
    quaternion = (
        msg.orientation.x,
        msg.orientation.y,
        msg.orientation.z,
        msg.orientation.w
    )
    (roll, pitch, yaw) = euler_from_quaternion(quaternion)
    roll = roll * 180.0 / math.pi
    pitch = pitch * 180.0 / math.pi
    yaw = yaw * 180.0 / math.pi
    rospy.loginfo("Roll: %f, Pitch: %f, Yaw: %f", roll, pitch, yaw)

if __name__ == '__main__':
    rospy.init_node('imu_node')
    rospy.Subscriber('/imu/data', Imu, imuCallback, queue_size=10)
    rospy.spin()
