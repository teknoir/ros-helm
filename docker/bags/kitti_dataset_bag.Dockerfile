FROM tyoung96/kitti2bag AS kitti2bag

RUN  #apk add --no-cache unzip wget
RUN apt-get update && apt-get install -y wget unzip

RUN wget https://s3.eu-central-1.amazonaws.com/avg-kitti/raw_data/2011_09_26_drive_0002/2011_09_26_drive_0002_sync.zip
RUN wget https://s3.eu-central-1.amazonaws.com/avg-kitti/raw_data/2011_09_26_calib.zip
RUN unzip 2011_09_26_drive_0002_sync.zip
RUN unzip 2011_09_26_calib.zip
RUN /kitti2bag/docker_entrypoint.sh -t 2011_09_26 -r 0002 raw_synced .

FROM python:3.9-slim AS kitti_bag_final

WORKDIR /data
COPY --from=kitti2bag /data /data

RUN pip install --upgrade pip && pip install --no-cache-dir --ignore-installed 'rosbags>=0.9.11'
RUN rosbags-convert kitti_2011_09_26_drive_0002_synced.bag --dst kitti_2011_09_26_drive_0002_synced_rosbag_v2

FROM alpine:3

ARG TARGETARCH

RUN  apk add --no-cache rsync

COPY --from=kitti_bag_final /data/kitti_2011_09_26_drive_0002_synced_rosbag_v2 /bags/kitti_2011_09_26_drive_0002_synced_rosbag_v2

CMD ["sh", "-c", "mkdir -p /ros_ws/bags/kitti_2011_09_26_drive_0002_synced_rosbag_v2 && rsync --checksum --itemize-changes --delete-before -avhr /bags/kitti_2011_09_26_drive_0002_synced_rosbag_v2/ /ros_ws/bags/kitti_2011_09_26_drive_0002_synced_rosbag_v2/"]
