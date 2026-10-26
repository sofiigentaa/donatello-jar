FROM ros:humble-desktop-jammy

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release \
    git \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    xauth \
    mesa-utils \
    && curl -fsSL https://packages.osrfoundation.org/gazebo.gpg \
       -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
       > /etc/apt/sources.list.d/gazebo-stable.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    ignition-fortress \
    ros-humble-ros-gz \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-gz-ros2-control \
    ros-humble-cv-bridge \
    ros-humble-xacro \
    ros-humble-tf-transformations \
    ros-humble-teleop-twist-keyboard \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/donatello_ws

CMD ["/bin/bash"]
