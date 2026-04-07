#!/usr/bin/env python3
#coding=utf-8
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

if __name__ == '__main__':
    rospy.init_node('nav_client2')
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    client.wait_for_server()
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = 'map'
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = -3.0
    goal.target_pose.pose.position.y = 2.0
    goal.target_pose.pose.position.z = 0.0
    goal.target_pose.pose.orientation.x = 0.0
    goal.target_pose.pose.orientation.y = 0.0
    goal.target_pose.pose.orientation.z = 0.0
    goal.target_pose.pose.orientation.w = 1.0
    client.send_goal(goal)
    client.wait_for_result()
    if client.get_state() == actionlib.GoalStatus.SUCCEEDED:
        rospy.loginfo("Navigation succeeded!")
    else:
        rospy.loginfo("Navigation failed!")