# TB3 Headless Launch Image

Container image with launch files for a headless TurtleBot3 simulation, used for SLAM and
navigation demos on edge devices.

- Repository: `ghcr.io/teknoir/ros-helm/tb3-headless-launch`
- Dockerfile: `docker/src/tb3_headless_launch/Dockerfile`
- Tags: `beta`, `latest`

## Use on an edge device

Reference it as an `artifacts` entry on a `ros` chart instance to run the headless simulator,
then pair it with a Cartographer SLAM instance:

```yaml
instances:
  - name: turtlebot3-simulation
    commands:
      - export TURTLEBOT3_MODEL=waffle_pi
      - colcon build
      - ros2 launch tb3_headless_launch tb3_house_headless_navigation.launch.py use_sim_time:=True
    artifacts:
      - name: tb3-headless
        image: ghcr.io/teknoir/ros-helm/tb3-headless-launch
        tag: dds-beta
```

See the [ROS2 HelmChart](../../ros2-helm/docs/index.md) docs for the full deployable manifest.

Reference: Teknoir Workshop 2 — Software Management and Helm Deployment Workflows.
