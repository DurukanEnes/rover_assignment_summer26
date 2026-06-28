#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import numpy as np
import time

from geometry_msgs.msg import Twist 
from sensor_msgs.msg import LaserScan
from gazebo_msgs.srv import DeleteLight, DeleteLightRequest


class ReactiveRobot:

    #class constructor
    def __init__(self):
        rospy.init_node("reactive_robot_node")
        #istenen üzere parametleri .launch dosyasından okuyoruz okunamadığı durumda default değerler atıyoruz.
        self.forward_linear_speed = rospy.get_param("~forward_linear_speed", 0.7)
        self.turn_linear_speed = rospy.get_param("~turn_linear_speed", 0.3)
        self.turn_angular_speed = rospy.get_param("~turn_angular_speed", 0.6)
        self.obstacle_threshold = rospy.get_param("~obstacle_threshold", 2.3)
        #/scan kullanarak LiDAR verilerini alıyoruz ve cmd_vel topicine hareket komutunu yolluyoruz.
        self.scan_sub = rospy.Subscriber("/scan",LaserScan,self.scan_callback)
        self.pub = rospy.Publisher("/cmd_vel",Twist,queue_size=10)

        rospy.loginfo("Waiting for /gazebo/delete_light service...")
        #gazebo açılana kadarki süreçte kodun ilerlemesini önler.
        rospy.wait_for_service("/gazebo/delete_light")
        #ışık silmek için kullanacağımız nesneyi oluşturuyoruz.
        self.light_delete_client = rospy.ServiceProxy("/gazebo/delete_light",DeleteLight)
        rospy.loginfo("DeleteLight service is ready.")
        #robota yollacagımız hareket komutlarını içeren objeyi olusturuyoruz
        self.cmd_vel = Twist()
        #robotun güncel durumda başlangıç anında her yöne hızı 0
        self.current_state = None
        #tutulacak süre için start belirlenir.
        self.start_time = time.time()
        self.time_limit_reached = False

    def scan_callback(self, scan_data):
        #60 sn sınırının dolup dolmadığı kontrolü
        if self.time_limit_reached:
            return
        if time.time() - self.start_time >= 60.0:
            self.time_limit_reached = True
            self.stop_robot()
            return

        #lazer datasını topluyoruz
        ranges = np.array(scan_data.ranges)
        #hatalı veri toplama durumunda engel yok durumuna sokmak icin 10 atıyoruz
        ranges[np.isnan(ranges)] = 10.0
        ranges[np.isinf(ranges)] = 10.0
        #ön taraftaki engelleri buluyoruz
        front_center = min(
            np.min(ranges[:10]),
            np.min(ranges[350:])
        )
        #görülen alanın sağını hesaplıyoruz
        right = np.mean(ranges[270:360])
        #görülen alanın solunu hesaplıyoruz
        left = np.mean(ranges[:90])
        self.cmd_vel = Twist()

        #hız komutlarına default değer atıyoruz
        self.cmd_vel.linear.x = self.forward_linear_speed
        self.cmd_vel.angular.z = 0.0

        #obstacle avoid algoritması
        
        #robotun önünde engel olması durumu
        if front_center < self.obstacle_threshold:
            #sağın daha açık olması
            if right > left:
                if self.current_state != "right":
                    rospy.loginfo("Started rotating right.")
                    self.current_state = "right"
                #sağa dönüş
                self.cmd_vel.linear.x = self.turn_linear_speed
                self.cmd_vel.angular.z = -self.turn_angular_speed
            else: #solun daha açık olması
                if self.current_state != "left":
                    rospy.loginfo("Started rotating left.")
                    self.current_state = "left"
                #sola dönüş
                self.cmd_vel.linear.x = self.turn_linear_speed
                self.cmd_vel.angular.z = self.turn_angular_speed
        else: #önün daha açık olması 
            if self.current_state != "forward":
                rospy.loginfo("Moving forward.")
                self.current_state = "forward"
            #düz devam
            self.cmd_vel.linear.x = self.forward_linear_speed
            self.cmd_vel.angular.z = 0.0
        #if-elselere göre yapılan atamaları publishler
        self.pub.publish(self.cmd_vel)

    def stop_robot(self):
        #lineer ve açısal hızı sıfırlıyoruz
        self.cmd_vel.linear.x = 0.0
        self.cmd_vel.angular.z = 0.0
        self.pub.publish(self.cmd_vel)
        #istenen üzerine delete light yapıyoruz
        rospy.loginfo("Time limit reached. Stopping...")
        light_request = DeleteLightRequest()
        light_request.light_name = "sun"
        #light'ı kaldırıp node'u kapatıyoruz
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
        ReactiveRobot() #constructor
        rospy.spin() #loop part
    except rospy.ROSInterruptException: #manuel müdahale durumunda kodu temiz şekilde sonlandırır
        pass