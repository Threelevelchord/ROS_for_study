#include <ros/ros.h>
#include <std_msgs/String.h>
int main(int argc, char *argv[])
{ 
   ros::init(argc, argv, "yao_node");
   printf("绝区零牛逼\n"); 
   
   ros::NodeHandle nh;
   ros::Publisher pub = nh.advertise<std_msgs::String>("yao_topic", 10);

   ros::Rate loop_rate(1);

   while (ros::ok())
   {
      /* code */
      printf("方舟牛逼\n"); 
      std_msgs::String msg;
      msg.data = "终末地牛逼";
      pub.publish(msg);
      loop_rate.sleep();
   }
    
   return 0;
}