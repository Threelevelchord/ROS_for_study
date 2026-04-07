#include <ros/ros.h>
#include <std_msgs/String.h>

void chao_callback(const std_msgs::String msg)
{
   ROS_INFO(msg.data.c_str());
}

void yao_callback(const std_msgs::String msg)
{
   ROS_WARN(msg.data.c_str());
}

int main(int argc, char *argv[])
{ 
   setlocale(LC_ALL,"");
   ros::init(argc, argv, "ma_node");
   ros::NodeHandle nh;
   ros::Subscriber sub = nh.subscribe("chao_topic", 10, chao_callback);
   ros::Subscriber sub2 = nh.subscribe("yao_topic", 10, yao_callback);
   while (ros::ok())
   {
    ros::spinOnce();
   }
   return 0;
}
   