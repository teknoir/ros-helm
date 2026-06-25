# Kitti Bag Image

Container image holding a KITTI rosbag, used as an init `artifact` to pre-load bag data for
playback on edge devices.

- Repository: `ghcr.io/teknoir/ros-helm/kitti-bag`
- Dockerfile: `docker/bags/kitti-bag/Dockerfile`
- Tags: `beta`, `latest`

## Use on an edge device

Reference it as an `artifacts` entry on a `ros` chart instance, then loop playback:

```yaml
instances:
  - name: play-kitti-bag
    commands:
      - ros2 bag play bags/kitti_2011_09_26_drive_0002_synced_rosbag_v2 --loop
    artifacts:
      - name: kitti-bag
        image: ghcr.io/teknoir/ros-helm/kitti-bag
        tag: beta
```

See the [ROS2 HelmChart](../../ros2-helm/docs/index.md) docs for the full deployable manifest.

Reference: Teknoir Workshop 2 — Software Management and Helm Deployment Workflows.
