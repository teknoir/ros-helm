# Zenoh Router Image

Container image running a Zenoh router to bridge/route ROS2 (DDS) traffic across the edge
network and back to the Teknoir platform.

- Repository: `ghcr.io/teknoir/ros-helm/zenoh-router`
- Tags: `beta`, `latest`

## Use on an edge device

Deployed through the Teknoir platform as part of the `ros` chart rollout to connect ROS2
nodes across devices. Configure it as a `ros` chart instance and place it with a
`nodeSelector` when routing must run on a specific node.

See the [ROS2 HelmChart](../../ros2-helm/docs/index.md) docs for the full deployable manifest.

Reference: Teknoir Workshop 2 — Software Management and Helm Deployment Workflows.
