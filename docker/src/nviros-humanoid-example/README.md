# NVIROS Humanoid Teleop Example

## Example: HelmChart to deploy Isaac Sim with NVIROS Humanoid Teleop

```yaml
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: ros
  namespace: default
spec:
  repo: https://teknoir.github.io/ros-helm
  chart: ros
  targetNamespace: default
  valuesContent: |-
    instances:
      - name: isaac-sim
        image:
          repository: us-docker.pkg.dev/teknoir/gcr.io/nviros
          tag: jazzy-20260129-141956
        nviros: true
        artifacts:
          - name: nviros-humanoid
            image: us-docker.pkg.dev/teknoir/gcr.io/nviros-humanoid
            tag: jazzy-20260130-080259    
        commands:
          - ./python.sh teknoir-examples/nviros-humanoid/warehouse_humanoid_ros2_teleop.py

```