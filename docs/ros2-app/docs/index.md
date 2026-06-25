# ROS2 App

The Robot Operating System (ROS2) application bundle for the Teknoir platform. It groups the
`ros` Helm chart with the container images it needs (ROS2, KITTI bag, Zenoh router, NVIROS,
Discovery, TB3 headless launch, NVIROS humanoid example).

## Deploy on an edge device

ROS2 workloads run on edge devices through the Teknoir platform using a K3s `HelmChart`
resource that points at the `ros` chart. See the
[ROS2 HelmChart](../../ros2-helm/docs/index.md) docs for the deployable manifest.

In short:

1. Onboard the edge device in the Teknoir Developer Platform.
2. Add a `HelmChart` resource (via Devstudio `add-app` or GitOps) referencing
   `repo: https://teknoir.github.io/ros-helm`, `chart: ros`.
3. Keep `valuesContent` minimal — only override image tags, node placement, and the
   instances/commands for your use case.
4. Visualize ROS data with Foxglove over `tnctl port-forward <device-name> 8765:31765`.

Reference: Teknoir Workshop 2 — Software Management and Helm Deployment Workflows.
