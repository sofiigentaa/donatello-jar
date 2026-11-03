FROM ros:humble-ros-base-jammy

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
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
    python3-numpy \
    python3-opencv \
    xauth \
    mesa-utils \
    && curl -fsSL https://packages.osrfoundation.org/gazebo.gpg \
       -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
       > /etc/apt/sources.list.d/gazebo-stable.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    ignition-fortress \
    && rm -rf /var/lib/apt/lists/*

# Resolve dependencies from every ROS package manifest so the bind-mounted
# workspace can be built and tested in a fresh container.
COPY src/yahboom_rosmaster/yahboom_rosmaster/package.xml \
     /tmp/donatello-rosdep/src/yahboom_rosmaster/package.xml
COPY src/yahboom_rosmaster/yahboom_rosmaster_bringup/package.xml \
     /tmp/donatello-rosdep/src/yahboom_rosmaster_bringup/package.xml
COPY src/yahboom_rosmaster/yahboom_rosmaster_description/package.xml \
     /tmp/donatello-rosdep/src/yahboom_rosmaster_description/package.xml
COPY src/yahboom_rosmaster/yahboom_rosmaster_gazebo/package.xml \
     /tmp/donatello-rosdep/src/yahboom_rosmaster_gazebo/package.xml
COPY src/yahboom_rosmaster/yahboom_rosmaster_msgs/package.xml \
     /tmp/donatello-rosdep/src/yahboom_rosmaster_msgs/package.xml

RUN if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then \
      rosdep init; \
    fi \
    && rosdep update --rosdistro humble \
    && apt-get update \
    && rosdep install \
      --from-paths /tmp/donatello-rosdep/src \
      --ignore-src \
      --rosdistro humble \
      --default-yes \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/donatello-rosdep

WORKDIR /root/donatello_ws

CMD ["/bin/bash"]
