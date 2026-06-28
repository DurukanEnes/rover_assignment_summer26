#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import numpy as np
import time

from geometry_msgs.msg import Twist 
from sensor_msgs.msg import LaserScan
from gazebo_msgs.srv import DeleteLight, DeleteLightRequest


class ReactiveRobot:

    def __init__(self):
        rospy.init_node("reactive_robot_node")
        # Parameters (Launch dosyasından okunur)
        self.forward_linear_speed = rospy.get_param("~forward_linear_speed", 0.7)
        self.turn_linear_speed = rospy.get_param("~turn_linear_speed", 0.3)
        self.turn_angular_speed = rospy.get_param("~turn_angular_speed", 0.6)
        self.obstacle_threshold = rospy.get_param("~obstacle_threshold", 2.3)
        self.scan_sub = rospy.Subscriber("/scan",LaserScan,self.scan_callback)
        self.pub = rospy.Publisher("/cmd_vel",Twist,queue_size=10)

        rospy.loginfo("Waiting for /gazebo/delete_light service...")
        rospy.wait_for_service("/gazebo/delete_light")

        self.light_delete_client = rospy.ServiceProxy("/gazebo/delete_light",DeleteLight)
        rospy.loginfo("DeleteLight service is ready.")
        self.cmd_vel = Twist()
        self.current_state = None
        self.start_time = time.time()
        self.time_limit_reached = False

    def scan_callback(self, scan_data):
        if self.time_limit_reached:
            return

        if time.time() - self.start_time >= 60.0:
            self.time_limit_reached = True
            self.stop_robot()
            return

        ranges = np.array(scan_data.ranges)
        # Sensör hatalarını temizle
        ranges[np.isnan(ranges)] = 10.0
        ranges[np.isinf(ranges)] = 10.0
        front_center = min(
            np.min(ranges[:10]),
            np.min(ranges[350:])
        )
        right = np.mean(ranges[270:360])
        left = np.mean(ranges[:90])
        self.cmd_vel = Twist()

        # Varsayılan hareket
        self.cmd_vel.linear.x = self.forward_linear_speed
        self.cmd_vel.angular.z = 0.0

        if front_center < self.obstacle_threshold:
            if right > left:
                if self.current_state != "right":
                    rospy.loginfo("Started rotating right.")
                    self.current_state = "right"

                self.cmd_vel.linear.x = self.turn_linear_speed
                self.cmd_vel.angular.z = -self.turn_angular_speed

            else:
                if self.current_state != "left":
                    rospy.loginfo("Started rotating left.")
                    self.current_state = "left"

                self.cmd_vel.linear.x = self.turn_linear_speed
                self.cmd_vel.angular.z = self.turn_angular_speed
        else:
            if self.current_state != "forward":
                rospy.loginfo("Moving forward.")
                self.current_state = "forward"

            self.cmd_vel.linear.x = self.forward_linear_speed
            self.cmd_vel.angular.z = 0.0

        self.pub.publish(self.cmd_vel)

    def stop_robot(self):

        self.cmd_vel.linear.x = 0.0
        self.cmd_vel.angular.z = 0.0
        self.pub.publish(self.cmd_vel)

        rospy.loginfo("Time limit reached. Stopping...")
        light_request = DeleteLightRequest()
        light_request.light_name = "sun"

        try:
            self.light_delete_client(light_request)
            rospy.loginfo("Light in Gazebo environment is removed.")

        except rospy.ServiceException as e:
            rospy.logerr(f"DeleteLight service failed: {e}")

        self.scan_sub.unregister()
        rospy.loginfo("/scan topic is unsubscribed.")

        rospy.signal_shutdown("60 second limit reached.")

if __name__ == "__main__":
    try:
        ReactiveRobot()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass