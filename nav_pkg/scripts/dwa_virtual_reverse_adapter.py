#!/usr/bin/env python3
# coding=utf-8

import copy
import math
import threading

import actionlib
import rospy
import tf
import tf2_ros
from actionlib_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped, TransformStamped, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseFeedback, MoveBaseGoal, MoveBaseResult
from nav_msgs.msg import OccupancyGrid, Odometry, Path


MODE_NORMAL = "NORMAL"
MODE_REVERSE_X = "REVERSE_X"


def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def yaw_from_pose(pose):
    q = pose.orientation
    return tf.transformations.euler_from_quaternion([q.x, q.y, q.z, q.w])[2]


def set_pose_yaw(pose, yaw):
    q = tf.transformations.quaternion_from_euler(0.0, 0.0, yaw)
    pose.orientation.x = q[0]
    pose.orientation.y = q[1]
    pose.orientation.z = q[2]
    pose.orientation.w = q[3]


class DwaVirtualReverseAdapter:
    def __init__(self):
        self.external_action_name = rospy.get_param("~external_action_name", "move_base")
        self.internal_action_name = rospy.get_param("~internal_action_name", "/dwa_internal/move_base")
        self.map_frame = rospy.get_param("~map_frame", "map")
        self.real_base_frame = rospy.get_param("~real_base_frame", "base_footprint")
        self.virtual_base_frame = rospy.get_param("~virtual_base_frame", "dwa_base_footprint")
        self.raw_cmd_topic = rospy.get_param("~cmd_vel_raw_topic", "/cmd_vel_dwa_raw")
        self.cmd_topic = rospy.get_param("~cmd_vel_topic", "/cmd_vel")
        self.odom_topic = rospy.get_param("~odom_topic", "/odom")
        self.virtual_odom_topic = rospy.get_param("~virtual_odom_topic", "/odom_dwa_virtual")

        self.reverse_min_distance = rospy.get_param("~reverse_min_distance", 0.25)
        self.reverse_angle_tolerance = rospy.get_param("~reverse_angle_tolerance", 0.60)
        self.reverse_lateral_tolerance = rospy.get_param("~reverse_lateral_tolerance", 0.35)
        self.reverse_yaw_tolerance = rospy.get_param("~reverse_yaw_tolerance", 0.35)
        self.tf_publish_rate = rospy.get_param("~tf_publish_rate", 30.0)

        self.mode = MODE_NORMAL
        self.mode_lock = threading.Lock()

        self.tf_listener = tf.TransformListener()
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()

        self.cmd_pub = rospy.Publisher(self.cmd_topic, Twist, queue_size=10)
        self.virtual_odom_pub = rospy.Publisher(self.virtual_odom_topic, Odometry, queue_size=20)
        self.simple_goal_sub = rospy.Subscriber(
            "/move_base_simple/goal", PoseStamped, self.simple_goal_callback, queue_size=1
        )
        self.raw_cmd_sub = rospy.Subscriber(self.raw_cmd_topic, Twist, self.raw_cmd_callback, queue_size=10)
        self.odom_sub = rospy.Subscriber(self.odom_topic, Odometry, self.odom_callback, queue_size=20)
        self.display_relays = [
            self.make_relay(
                "/dwa_internal/move_base/global_costmap/costmap",
                "/move_base/global_costmap/costmap",
                OccupancyGrid,
            ),
            self.make_relay(
                "/dwa_internal/move_base/local_costmap/costmap",
                "/move_base/local_costmap/costmap",
                OccupancyGrid,
            ),
            self.make_relay(
                "/dwa_internal/move_base/GlobalPlanner/plan",
                "/move_base/GlobalPlanner/plan",
                Path,
            ),
            self.make_relay(
                "/dwa_internal/move_base/DWAPlannerROS/global_plan",
                "/move_base/DWAPlannerROS/global_plan",
                Path,
            ),
            self.make_relay(
                "/dwa_internal/move_base/DWAPlannerROS/local_plan",
                "/move_base/DWAPlannerROS/local_plan",
                Path,
            ),
        ]

        self.internal_client = actionlib.SimpleActionClient(self.internal_action_name, MoveBaseAction)
        self.external_server = actionlib.SimpleActionServer(
            self.external_action_name,
            MoveBaseAction,
            execute_cb=self.execute_action_goal,
            auto_start=False,
        )

        rospy.Timer(rospy.Duration(1.0 / self.tf_publish_rate), self.publish_virtual_tf)

    def make_relay(self, src_topic, dst_topic, msg_type):
        pub = rospy.Publisher(dst_topic, msg_type, queue_size=1, latch=True)

        def callback(msg):
            pub.publish(msg)

        sub = rospy.Subscriber(src_topic, msg_type, callback, queue_size=1)
        return pub, sub

    def start(self):
        rospy.loginfo("Waiting for internal move_base action server: %s", self.internal_action_name)
        self.internal_client.wait_for_server()
        self.external_server.start()
        rospy.loginfo("DWA virtual reverse adapter ready. Public action: /%s", self.external_action_name)

    def publish_virtual_tf(self, _event):
        transform = TransformStamped()
        transform.header.stamp = rospy.Time.now()
        transform.header.frame_id = self.real_base_frame
        transform.child_frame_id = self.virtual_base_frame
        transform.transform.translation.x = 0.0
        transform.transform.translation.y = 0.0
        transform.transform.translation.z = 0.0

        with self.mode_lock:
            yaw_offset = math.pi if self.mode == MODE_REVERSE_X else 0.0

        q = tf.transformations.quaternion_from_euler(0.0, 0.0, yaw_offset)
        transform.transform.rotation.x = q[0]
        transform.transform.rotation.y = q[1]
        transform.transform.rotation.z = q[2]
        transform.transform.rotation.w = q[3]
        self.tf_broadcaster.sendTransform(transform)

    def raw_cmd_callback(self, msg):
        with self.mode_lock:
            mode = self.mode

        if mode == MODE_REVERSE_X:
            cmd = Twist()
            cmd.linear.x = -msg.linear.x
            cmd.linear.y = -msg.linear.y
            cmd.linear.z = msg.linear.z
            cmd.angular.x = msg.angular.x
            cmd.angular.y = msg.angular.y
            cmd.angular.z = msg.angular.z
        else:
            cmd = copy.deepcopy(msg)

        self.cmd_pub.publish(cmd)

    def odom_callback(self, msg):
        with self.mode_lock:
            mode = self.mode

        odom = copy.deepcopy(msg)
        odom.child_frame_id = self.virtual_base_frame

        if mode == MODE_REVERSE_X:
            pose_yaw = yaw_from_pose(odom.pose.pose)
            set_pose_yaw(odom.pose.pose, normalize_angle(pose_yaw + math.pi))
            odom.twist.twist.linear.x = -msg.twist.twist.linear.x
            odom.twist.twist.linear.y = -msg.twist.twist.linear.y
            odom.twist.twist.angular.x = -msg.twist.twist.angular.x
            odom.twist.twist.angular.y = -msg.twist.twist.angular.y

        self.virtual_odom_pub.publish(odom)

    def simple_goal_callback(self, pose_stamped):
        goal = MoveBaseGoal()
        goal.target_pose = pose_stamped
        adapted_goal, mode = self.adapt_goal(goal)
        self.set_mode(mode)
        rospy.loginfo("Simple goal mode: %s, forwarding to %s", mode, self.internal_action_name)
        self.internal_client.send_goal(adapted_goal, done_cb=self.simple_done_callback)

    def simple_done_callback(self, _state, _result):
        self.set_mode(MODE_NORMAL)

    def execute_action_goal(self, goal):
        adapted_goal, mode = self.adapt_goal(goal)
        self.set_mode(mode)
        rospy.loginfo("Action goal mode: %s", mode)

        self.internal_client.send_goal(
            adapted_goal,
            done_cb=None,
            active_cb=None,
            feedback_cb=self.feedback_callback,
        )

        rate = rospy.Rate(20)
        while not rospy.is_shutdown():
            if self.external_server.is_preempt_requested():
                self.internal_client.cancel_goal()
                self.set_mode(MODE_NORMAL)
                self.external_server.set_preempted(MoveBaseResult(), "Goal preempted")
                return

            state = self.internal_client.get_state()
            if state in [
                GoalStatus.SUCCEEDED,
                GoalStatus.ABORTED,
                GoalStatus.REJECTED,
                GoalStatus.PREEMPTED,
                GoalStatus.RECALLED,
                GoalStatus.LOST,
            ]:
                result = self.internal_client.get_result() or MoveBaseResult()
                self.set_mode(MODE_NORMAL)
                if state == GoalStatus.SUCCEEDED:
                    self.external_server.set_succeeded(result, "Goal reached")
                elif state in [GoalStatus.PREEMPTED, GoalStatus.RECALLED]:
                    self.external_server.set_preempted(result, "Goal preempted")
                else:
                    self.external_server.set_aborted(result, "Goal failed")
                return

            rate.sleep()

    def feedback_callback(self, feedback):
        if self.external_server.is_active():
            self.external_server.publish_feedback(feedback or MoveBaseFeedback())

    def set_mode(self, mode):
        with self.mode_lock:
            if mode != self.mode:
                rospy.loginfo("Virtual reverse mode change: %s -> %s", self.mode, mode)
            self.mode = mode

    def adapt_goal(self, goal):
        mode = self.select_mode(goal.target_pose)
        adapted = copy.deepcopy(goal)
        adapted.target_pose.header.stamp = rospy.Time.now()

        if mode == MODE_REVERSE_X:
            target_yaw = yaw_from_pose(adapted.target_pose.pose)
            set_pose_yaw(adapted.target_pose.pose, normalize_angle(target_yaw + math.pi))
            rospy.loginfo(
                "Adapted reverse goal yaw %.2f -> %.2f",
                target_yaw,
                normalize_angle(target_yaw + math.pi),
            )

        return adapted, mode

    def select_mode(self, target_pose_stamped):
        try:
            now = rospy.Time(0)
            self.tf_listener.waitForTransform(
                self.map_frame, self.real_base_frame, now, rospy.Duration(0.5)
            )
            (_trans, rot) = self.tf_listener.lookupTransform(self.map_frame, self.real_base_frame, now)

            goal_for_tf = copy.deepcopy(target_pose_stamped)
            goal_for_tf.header.stamp = now
            target_in_base = self.tf_listener.transformPose(self.real_base_frame, goal_for_tf)
            target_in_map = self.tf_listener.transformPose(self.map_frame, goal_for_tf)
        except (tf.Exception, tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as exc:
            rospy.logwarn("Could not evaluate reverse mode, using NORMAL: %s", exc)
            return MODE_NORMAL

        x = target_in_base.pose.position.x
        y = target_in_base.pose.position.y
        distance = math.hypot(x, y)

        if distance < self.reverse_min_distance:
            return MODE_NORMAL

        angle_to_target = abs(normalize_angle(math.atan2(y, x) - math.pi))
        lateral_ok = abs(y) <= self.reverse_lateral_tolerance
        behind_ok = x < -self.reverse_min_distance and angle_to_target <= self.reverse_angle_tolerance

        current_yaw = tf.transformations.euler_from_quaternion(rot)[2]
        target_yaw = yaw_from_pose(target_in_map.pose)
        yaw_err = normalize_angle(target_yaw - current_yaw)
        yaw_ok = abs(yaw_err) <= self.reverse_yaw_tolerance

        if behind_ok and lateral_ok and yaw_ok:
            rospy.loginfo(
                "Reverse goal detected: x=%.2f y=%.2f dist=%.2f yaw_err=%.2f",
                x,
                y,
                distance,
                yaw_err,
            )
            return MODE_REVERSE_X

        rospy.loginfo(
            "Normal goal: x=%.2f y=%.2f dist=%.2f behind=%s lateral=%s yaw=%s yaw_err=%.2f",
            x,
            y,
            distance,
            behind_ok,
            lateral_ok,
            yaw_ok,
            yaw_err,
        )
        return MODE_NORMAL


if __name__ == "__main__":
    rospy.init_node("dwa_virtual_reverse_adapter")
    adapter = DwaVirtualReverseAdapter()
    adapter.start()
    rospy.spin()
