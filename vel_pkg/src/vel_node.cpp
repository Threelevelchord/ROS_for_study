#include <ros/ros.h>
#include<geometry_msgs/Twist.h>

int main(int argc, char *argv[])
{
    ros::init(argc, argv, "vel_node");
    ros::NodeHandle n;
    ros::Publisher vel_pub = n.advertise<geometry_msgs::Twist>("cmd_vel", 10);
    geometry_msgs::Twist msg;
    
    msg.linear.x = 0.0;
    msg.linear.y = 0.0;
    msg.linear.z = 0.0;
    msg.angular.x = 0.0;
    msg.angular.y = 0.0;
    msg.angular.z = 0.5;
    ros::Rate loop_rate(30);
    while (ros::ok())
    {
        vel_pub.publish(msg);
        loop_rate.sleep();
    }
    return 0;
}