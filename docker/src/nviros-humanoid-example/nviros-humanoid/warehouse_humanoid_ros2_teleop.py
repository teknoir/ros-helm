"""
warehouse_humanoid_ros2_teleop_compressed.py

Headless Isaac Sim standalone script that:
- Loads Simple Warehouse environment
- Loads Humanoid asset
- Attaches an RGB camera to the humanoid
- Publishes sensor_msgs/msg/CompressedImage (JPEG) on ROS2
- Subscribes to geometry_msgs/msg/Twist (cmd_vel) via Isaac Sim ROS2 bridge node
- Applies Twist as simple planar motion (x/y) + yaw (steer)

Tested conceptually against Isaac Sim 5.x APIs shown in docs; you may need to adjust
asset paths slightly if your asset packs are older/newer.
"""

import argparse
import io
import math
import sys
import time

import numpy as np

# -----------------------------------------------------------------------------
# Parse args (keep it simple; you can also hardcode constants if you prefer)
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--cmd-vel-topic", default="/humanoid/cmd_vel", help="ROS2 Twist topic to subscribe to")
parser.add_argument("--image-topic", default="/humanoid/camera/image/compressed", help="ROS2 CompressedImage topic to publish")
parser.add_argument("--frame-id", default="humanoid_camera_optical", help="frame_id in CompressedImage.header")
parser.add_argument("--width", type=int, default=640)
parser.add_argument("--height", type=int, default=480)
parser.add_argument("--publish-hz", type=float, default=10.0, help="Compressed image publish rate")
parser.add_argument("--jpeg-quality", type=int, default=80, help="JPEG quality (1-95 typical)")
args, _unknown = parser.parse_known_args()

# -----------------------------------------------------------------------------
# Isaac Sim must be imported AFTER SimulationApp is created
# -----------------------------------------------------------------------------
from isaacsim import SimulationApp

simulation_app = SimulationApp(
    {
        "headless": True,
        # You can add renderer settings if needed; keep minimal by default.
        # "renderer": "RayTracedLighting",
    }
)

# Enable required extensions (support both 5.x and older naming if present)
from isaacsim.core.utils.extensions import enable_extension

def _enable_first(ext_names):
    last_exc = None
    for ext in ext_names:
        try:
            enable_extension(ext)
            print(f"[isaac] enabled extension: {ext}")
            return ext
        except Exception as e:
            last_exc = e
    raise RuntimeError(f"Could not enable any of: {ext_names}. Last error: {last_exc}")

_enable_first(["isaacsim.ros2.bridge", "omni.isaac.ros2_bridge"])
_enable_first(["isaacsim.sensors.camera", "omni.isaac.sensor"])

simulation_app.update()

# -----------------------------------------------------------------------------
# Isaac Sim / Omniverse imports
# -----------------------------------------------------------------------------
import omni.graph.core as og
import omni.timeline

import isaacsim.core.utils.numpy.rotations as rot_utils
import isaacsim.core.utils.prims as prim_utils
from isaacsim.core.api import World
from isaacsim.core.prims import XFormPrim
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.storage.native import get_assets_root_path
from isaacsim.sensors.camera import Camera

# -----------------------------------------------------------------------------
# ROS2 Python publisher for sensor_msgs/CompressedImage
# -----------------------------------------------------------------------------
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage

from PIL import Image  # used to JPEG-encode

class CompressedCamPublisher(Node):
    def __init__(self, topic: str, frame_id: str, jpeg_quality: int):
        super().__init__("isaac_sim_compressed_cam_pub")
        self._pub = self.create_publisher(CompressedImage, topic, qos_profile_sensor_data)
        self._frame_id = frame_id
        self._jpeg_quality = int(jpeg_quality)

    def publish_rgb(self, rgb_u8: np.ndarray):
        """
        rgb_u8: HxWx3 uint8 RGB image
        """
        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self._frame_id
        msg.format = "jpeg"

        pil_img = Image.fromarray(rgb_u8, mode="RGB")
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=self._jpeg_quality)
        msg.data = buf.getvalue()

        self._pub.publish(msg)

# -----------------------------------------------------------------------------
# Build the scene (warehouse + humanoid + camera)
# -----------------------------------------------------------------------------
assets_root = get_assets_root_path()
if not assets_root:
    raise RuntimeError(
        "get_assets_root_path() returned None/empty. "
        "Make sure Isaac Sim assets are installed and asset_root is configured."
    )

# Environment USD (documented under /Isaac/Environments/... in asset packs)
#WAREHOUSE_USD = assets_root + "/Isaac/Environments/Simple_Warehouse/warehouse_with_forklifts.usd"
WAREHOUSE_USD = assets_root + "/Isaac/Environments/Simple_Warehouse/full_warehouse.usd"

#HUMANOID_USD = assets_root + "/Isaac/Robots/IsaacSim/Humanoid/humanoid.usd"
#HUMANOID_USD = assets_root + "/Isaac/Robots/Unitree/H1/h1.usd"
HUMANOID_USD = assets_root + "/Isaac/Robots/NVIDIA/NovaCarter/nova_carter.usd"

world = World(stage_units_in_meters=1.0)

print(f"[isaac] loading warehouse: {WAREHOUSE_USD}")
add_reference_to_stage(WAREHOUSE_USD, "/World/Warehouse")

print(f"[isaac] loading humanoid: {HUMANOID_USD}")
add_reference_to_stage(HUMANOID_USD, "/World/Humanoid")

# Wrap humanoid root so we can move it
humanoid_root = XFormPrim("/World/Humanoid", name="HumanoidRoot")
_pose_pos = np.zeros((1, 3), dtype=np.float64)
_pose_quat = np.zeros((1, 4), dtype=np.float64)

# Spawn pose (adjust to taste)
pos = np.array([0.0, 0.0, 0.0], dtype=np.float64)
yaw = 0.0
_pose_pos[0, :] = pos
_pose_quat[0, :] = rot_utils.euler_angles_to_quats(np.array([0.0, 0.0, yaw]), degrees=False)
humanoid_root.set_world_poses(positions=_pose_pos, orientations=_pose_quat)

import omni.usd
from pxr import Usd, UsdGeom, Gf  # IMPORTANT: import AFTER SimulationApp is running

# Camera mount: child prim under humanoid head so it follows humanoid head motion
stage = omni.usd.get_context().get_stage()

humanoid_root_path = "/World/Humanoid"
humanoid_prim = stage.GetPrimAtPath(humanoid_root_path)

if not humanoid_prim or not humanoid_prim.IsValid():
    print(f"[error] Prim not found or invalid: {humanoid_root_path}")
else:
    print(f"[humanoid] root: {humanoid_prim.GetPath()}")
    # Traverse all prims under the humanoid root using Usd.PrimRange
    for prim in Usd.PrimRange(humanoid_prim):
        print(f"[humanoid] {prim.GetPath()}")

cam_mount_path = "/World/Humanoid/chassis_link"
# cam_mount_path = "/World/Humanoid/mid360_link"

existing = stage.GetPrimAtPath(cam_mount_path)
if existing and existing.IsValid():
    print(f"[isaac] reusing existing prim: {cam_mount_path}")
else:
    prim_utils.create_prim(cam_mount_path, "Xform")
    print(f"[isaac] created prim: {cam_mount_path}")

# Always (re)set the local transform so reruns are deterministic
prim = stage.GetPrimAtPath(cam_mount_path)
xform = UsdGeom.XformCommonAPI(prim)
xform.SetTranslate(Gf.Vec3d(0.0, 0.0, 0.0))

camera = Camera(
    prim_path=cam_mount_path + "/rgb",
    resolution=(args.width, args.height),
    frequency=60,
)

world.reset()
camera.initialize()

camera.set_local_pose(
    translation=np.array([0.10, 0.00, 0.02]),     # forward, left, up
    orientation=np.array([1.0, 0.0, 0.0, 0.0]),   # identity (w,x,y,z)
    camera_axes="world",
)

import math
w, h = args.width, args.height
cx, cy = w / 2.0, h / 2.0

target_fov_deg = 130.0
fx = (w / 2.0) / math.tan(math.radians(target_fov_deg) / 2.0)
fy = fx

camera.set_opencv_pinhole_properties(cx=cx, cy=cy, fx=fx, fy=fy, pinhole=[0.0]*12)

# -----------------------------------------------------------------------------
# ROS2SubscribeTwist graph (teleop via Isaac Sim ROS2 bridge node)
# -----------------------------------------------------------------------------
GRAPH_PATH = "/ActionGraph"

keys = og.Controller.Keys
try:
    og.Controller.edit(
        {"graph_path": GRAPH_PATH, "evaluator_name": "push"},
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("SubTwist", "isaacsim.ros2.bridge.ROS2SubscribeTwist"),
            ],
            keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "SubTwist.inputs:execIn"),
            ],
            keys.SET_VALUES: [
                ("SubTwist.inputs:topicName", args.cmd_vel_topic),
                ("SubTwist.inputs:queueSize", 1),
            ],
        },
    )
except Exception:
    # Backward compatibility for older extension name (pre-5.x)
    og.Controller.edit(
        {"graph_path": GRAPH_PATH, "evaluator_name": "push"},
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("SubTwist", "omni.isaac.ros2_bridge.ROS2SubscribeTwist"),
            ],
            keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "SubTwist.inputs:execIn"),
            ],
            keys.SET_VALUES: [
                ("SubTwist.inputs:topicName", args.cmd_vel_topic),
                ("SubTwist.inputs:queueSize", 1),
            ],
        },
    )

lin_attr = og.Controller.attribute(f"{GRAPH_PATH}/SubTwist.outputs:linearVelocity")
ang_attr = og.Controller.attribute(f"{GRAPH_PATH}/SubTwist.outputs:angularVelocity")

# -----------------------------------------------------------------------------
# Start ROS2 publisher + run loop
# -----------------------------------------------------------------------------
rclpy.init(args=None)
cam_pub = CompressedCamPublisher(args.image_topic, args.frame_id, args.jpeg_quality)

timeline = omni.timeline.get_timeline_interface()
timeline.play()

publish_period = 1.0 / max(args.publish_hz, 1e-6)
last_pub_t = 0.0
sim_t = 0.0

# Warm up a few frames for rendering
for _ in range(10):
    world.step(render=True)

print("[isaac] running. Topics:")
print(f"  cmd_vel (Twist sub): {args.cmd_vel_topic}")
print(f"  camera (CompressedImage pub): {args.image_topic}")
print("CTRL+C to stop.")

try:
    while simulation_app.is_running():
        world.step(render=True)

        dt = world.get_physics_dt()
        sim_t += dt

        # Read Twist outputs from the ROS2 bridge node
        try:
            lin = np.array(lin_attr.get(), dtype=np.float64)  # [vx, vy, vz]
            ang = np.array(ang_attr.get(), dtype=np.float64)  # [wx, wy, wz]
        except Exception:
            lin = np.zeros(3)
            ang = np.zeros(3)

        vx, vy = float(lin[0]), float(lin[1])
        wz = float(ang[2])

        # Integrate planar motion + yaw
        yaw += wz * dt
        dx_world = (vx * math.cos(yaw) - vy * math.sin(yaw)) * dt
        dy_world = (vx * math.sin(yaw) + vy * math.cos(yaw)) * dt

        pos[0] += dx_world
        pos[1] += dy_world

        _pose_pos[0, :] = pos
        _pose_quat[0, :] = rot_utils.euler_angles_to_quats(np.array([0.0, 0.0, yaw]), degrees=False)
        humanoid_root.set_world_poses(positions=_pose_pos, orientations=_pose_quat)

        # Publish JPEG CompressedImage at throttled rate
        if (sim_t - last_pub_t) >= publish_period:
            rgba = camera.get_rgba()
            if rgba is not None and hasattr(rgba, "shape") and rgba.size > 0:
                rgb = rgba[..., :3]

                # Make sure uint8 RGB
                if rgb.dtype != np.uint8:
                    # Some pipelines return float in [0, 1]
                    if np.nanmax(rgb) <= 1.0:
                        rgb = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
                    else:
                        rgb = np.clip(rgb, 0.0, 255.0).astype(np.uint8)

                cam_pub.publish_rgb(rgb)

            last_pub_t = sim_t

        # No subscriptions in rclpy here, but this keeps rclpy happy in long runs
        rclpy.spin_once(cam_pub, timeout_sec=0.0)

except KeyboardInterrupt:
    pass
finally:
    try:
        cam_pub.destroy_node()
        rclpy.shutdown()
    except Exception:
        pass

    simulation_app.close()