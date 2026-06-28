# Reaktif Engel Kaçınma Robotu

Bu proje, **İTÜ Rover Obstacle Avoidance Assignment** kapsamında geliştirilmiştir.

## Proje Hakkında

Bu projede TurtleBot3 robotu, `/scan` topic'inden aldığı **LaserScan** verilerini kullanarak çevresindeki engelleri algılar ve reaktif (reactive) bir algoritma ile engellerden kaçınır.

Robot, önündeki engel durumuna göre hareket yönünü belirler ve parkur boyunca mümkün olduğunca akıcı (smooth) bir şekilde ilerler.

## Gerçekleştirilen İsterler

Projede aşağıdaki gereksinimler yerine getirilmiştir:

* `/scan` topic'inden alınan **LaserScan** verileri kullanılarak engel algılama
* Ön taraftaki en yakın engele göre sağa veya sola yönelme
* Robotun dönüş sırasında tamamen durmadan ilerlemeye devam etmesi
* Hareket hızlarının launch dosyasından parametre olarak alınması
* Hareket değişimlerinin `rospy.loginfo` ile terminale yazdırılması
* Robotun 60 saniye boyunca çalışması
* Süre sonunda robotun durdurulması
* `/scan` topic'inden unsubscribe olunması
* Gazebo ortamındaki **sun** ışığının `DeleteLight` servisi kullanılarak kaldırılması
* Node'un güvenli şekilde kapatılması

## Kullanılan Teknolojiler

* ROS Noetic
* Python
* TurtleBot3
* Gazebo
* NumPy

## Proje Yapısı

```text
reactive_robot/
│
├── launch/
│   └── reactive_robot.launch
│
├── scripts/
│   └── reactive_robot.py
│
├── package.xml
├── CMakeLists.txt
└── README.md
```

## Çalıştırma

```bash
catkin build
source devel/setup.bash
roslaunch reactive_robot reactive_robot.launch
```

## Algoritma

Robot aşağıdaki adımları takip eder:

1. `/scan` topic'inden LaserScan verilerini alır.
2. Ön, sağ ve sol bölgelerdeki mesafeleri hesaplar.
3. Ön tarafta engel yoksa düz ilerler.
4. Ön tarafta engel varsa sağ ve sol tarafın boşluklarını karşılaştırır.
5. Daha açık olan yöne doğru dönerek engelden kaçınır.
6. 60 saniyenin sonunda robot durdurulur, Gazebo'daki **sun** ışığı kaldırılır ve node güvenli şekilde kapatılır.
