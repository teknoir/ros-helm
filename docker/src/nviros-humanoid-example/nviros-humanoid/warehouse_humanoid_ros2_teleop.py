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
import os
import cv2
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
parser.add_argument("--publish-hz", type=float, default=5.0, help="Compressed image publish rate")
parser.add_argument("--jpeg-quality", type=int, default=55, help="JPEG quality (1-95 typical)")
args, _unknown = parser.parse_known_args()

# def is_jetson() -> bool:
#     # Works in most Jetson containers
#     for p in ("/etc/nv_tegra_release", "/proc/device-tree/model"):
#         try:
#             with open(p, "r") as f:
#                 s = f.read().lower()
#             if "jetson" in s or "orin" in s or "tegra" in s or "nvidia" in s:
#                 return True
#         except Exception:
#             pass
#     return False
#
# ON_JETSON = is_jetson()

config = {
    "headless": True,
}

# if ON_JETSON:
#     config = {
#         "headless": True,
#         "renderer": "RayTracedLighting", # Force Real-Time (NOT PathTracing)
#         "display_options": 3286, # 3286 = Hide UI elements to save resources
#     }

# -----------------------------------------------------------------------------
# Isaac Sim must be imported AFTER SimulationApp is created
# -----------------------------------------------------------------------------
from isaacsim import SimulationApp

simulation_app = SimulationApp(config)

import carb
# def optimize_headless_render_for_orin():
#     settings = carb.settings.get_settings()
#
#     # 1. Force Real-Time (Raster)
#     settings.set_int("/rtx/rendermode", 0)
#
#     # 2. CRITICAL: Disable NRD (Denoiser) to stop shader compile errors
#     settings.set_bool("/rtx/denoising/enabled", False)
#
#     # 3. Disable DLSS (Causes grain at 640x480, adds overhead)
#     settings.set_bool("/rtx/post/dlss/enabled", False)
#
#     # 4. Disable Ray Traced Shadows (Sampled Lighting)
#     # This forces simple shadow maps, which are much faster and don't require denoising
#     settings.set_bool("/rtx/directLighting/sampledLighting/enabled", False)
#
#     # 5. Disable other heavy features
#     settings.set_bool("/rtx/reflections/enabled", False)
#     settings.set_bool("/rtx/ambientOcclusion/enabled", False)
#     settings.set_bool("/rtx/indirectDiffuse/enabled", False)
#     settings.set_bool("/rtx/translucency/enabled", False)
#
#     # --- FIX FOR PHYSX ERROR 222 ---
#     # Force Physics to run on CPU.
#     # For 1 robot, CPU is faster than the overhead of launching broken GPU kernels.
#     settings.set_bool("/physics/physx/useGpu", False)
#
#     # Optional: Reduce thread count if CPU is busy
#     settings.set_int("/physics/physx/solver/numThreads", 4)
#
#     settings.set_bool("/rtx/hydra/material/texture_compression_enabled", False)
#     settings.set_bool("/rtx/material/compressTextures", False)
#
#     print("--- Optimized for Jetson Orin Headless ---")

# def optimize_headless_render_for_orin():
#     settings = carb.settings.get_settings()
#
#     # 1. FORCE REAL-TIME MODE (Disable Path Tracing)
#     # 0 = Real-Time, 1 = Path Tracing, 2 = Iray
#     settings.set_int("/rtx/rendermode", 0)
#
#     # 2. ENABLE DLSS (Crucial for Orin AGX)
#     # Enable DLSS (Deep Learning Super Sampling)
#     settings.set_bool("/rtx/post/dlss/enabled", True)
#     # Set DLSS to "Ultra Performance" mode
#     # 0: Standard, 1: Ultra Performance, 2: Max Performance, 3: Balanced, 4: Max Quality
#     settings.set_int("/rtx/post/dlss/execMode", 1)
#
#     # 3. ELIMINATE "GRAININESS" (Denoising)
#     # If using Ray Tracing, you need a denoiser.
#     # If you just want raw speed and don't care about shadows, turn RT off (see step 4).
#     settings.set_bool("/rtx/hydra/subdivision/refinementLevel", 0)
#
#     # 4. DISABLE EXPENSIVE LIGHTING FEATURES (The "Lightweight" setup)
#     # Disable Ray Traced Reflections
#     settings.set_bool("/rtx/reflections/enabled", False)
#     # Disable Ray Traced Ambient Occlusion
#     settings.set_bool("/rtx/ambientOcclusion/enabled", False)
#     # Disable Global Illumination (Indirect Lighting)
#     settings.set_bool("/rtx/indirectDiffuse/enabled", False)
#     # Disable Translucency
#     settings.set_bool("/rtx/translucency/enabled", False)
#
#     # 5. LIMIT SAMPLES
#     # Reduce samples per pixel. For RL, 1 sample is often enough if textures are simple.
#     settings.set_int("/rtx/pathtracing/spp", 1)
#     settings.set_int("/rtx/pathtracing/totalSpp", 1)
#
#     # 6. SHADOWS
#     # If you don't need accurate shadows, disable them for massive speedup
#     settings.set_bool("/rtx/directLighting/sampledLighting/enabled", False)
#
#     print("--- Optimized for Jetson Orin Headless ---")

def optimize_headless_render():
    settings = carb.settings.get_settings()

    # 1. Force Real-Time (Raster)
    settings.set_int("/rtx/rendermode", 0)

    # 2. Keep Denoiser enabled to smooth out ray-traced lighting
    settings.set_bool("/rtx/denoising/enabled", True)

    # 3. Enable DLSS and set to Max Quality for 1080p on Ada generation
    settings.set_bool("/rtx/post/dlss/enabled", True)
    settings.set_int("/rtx/post/dlss/execMode", 4)  # 4 = Max Quality

    # 4. AGGRESSIVELY DISABLE VRS, Foveated Rendering, and Dynamic Res
    settings.set_bool("/rtx/vrs/enabled", False)
    settings.set_bool("/rtx/vrs/foveated/enabled", False)
    settings.set_bool("/rtx/foveatedRendering/enabled", False)
    settings.set_bool("/rtx/post/foveatedRendering/enabled", False)
    settings.set_bool("/rtx/dynamicRes/enabled", False)

    # 5. Disable other heavy features
    settings.set_bool("/rtx/reflections/enabled", False)


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
_enable_first(["isaacsim.robot.policy.examples"])
# if ON_JETSON:
#     _enable_first(["omni.kit.compatibility_mode"])

simulation_app.update()

# if ON_JETSON:
#     # Call this AFTER simulation_app.update() or initialization
#     optimize_headless_render_for_orin()

optimize_headless_render()

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
        # self._buf = io.BytesIO() # No longer needed for cv2

    def publish_rgb(self, rgb_u8: np.ndarray):
        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self._frame_id
        msg.format = "jpeg"

        # OPTIMIZATION: Use OpenCV for much faster encoding (C++ backend)
        # cv2 expects BGR, Isaac gives RGB. Convert or just encode (colors will be swapped if not converted)
        # For pure speed, we encode as is, but let's do it right:
        bgr_u8 = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2BGR)

        # cv2.imencode returns (success, encoded_image)
        success, encoded_img = cv2.imencode('.jpg', bgr_u8, [int(cv2.IMWRITE_JPEG_QUALITY), self._jpeg_quality])

        if success:
            msg.data = encoded_img.tobytes()
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
# WAREHOUSE_USD = assets_root + "/Isaac/Environments/Simple_Warehouse/default_environment.usd"
# WAREHOUSE_USD = assets_root + "/Isaac/Environments/Simple_Warehouse/warehouse_with_forklifts.usd"
WAREHOUSE_USD = assets_root + "/Isaac/Environments/Simple_Warehouse/full_warehouse.usd"

print(f"[isaac] loading warehouse: {WAREHOUSE_USD}")
add_reference_to_stage(WAREHOUSE_USD, "/World/Warehouse")

#HUMANOID_USD = assets_root + "/Isaac/Robots/IsaacSim/Humanoid/humanoid.usd"
H1_USD = assets_root + "/Isaac/Robots/Unitree/H1/h1.usd"
# HUMANOID_USD = assets_root + "/Isaac/Robots/NVIDIA/NovaCarter/nova_carter.usd"

# IMPORTANT: policy example uses a faster physics dt (matches the shipped example)
world = World(stage_units_in_meters=1.0, physics_dt=1/200, rendering_dt=8/200)

# Spawn H1 via the policy wrapper (this adds the robot USD and sets it up)
from isaacsim.robot.policy.examples.robots import H1FlatTerrainPolicy

robot_prim_path = "/World/H1_0"
h1 = H1FlatTerrainPolicy(
    prim_path=robot_prim_path,
    name="H1_0",
    usd_path=H1_USD,
    position=np.array([-5.0, -5.0, 1.05]),  # matches the example's z to avoid ground penetration
)

# Base command the policy consumes: [vx, vy, wz]
base_command = np.zeros(3, dtype=np.float32)

first_step = True
reset_needed = False

def on_physics_step(step_size: float):
    global first_step, reset_needed, base_command
    if first_step:
        h1.initialize()
        first_step = False
    elif reset_needed:
        world.reset(True)
        reset_needed = False
        first_step = True
    else:
        # Policy-controlled locomotion
        h1.forward(step_size, base_command)

world.reset()
world.add_physics_callback("policy_step", callback_fn=on_physics_step)

import omni.usd
from pxr import Usd, UsdGeom, Gf, Sdf  # IMPORTANT: import AFTER SimulationApp is running

# Camera mount: child prim under humanoid head so it follows humanoid head motion
stage = omni.usd.get_context().get_stage()

humanoid_root_path = robot_prim_path
humanoid_prim = stage.GetPrimAtPath(humanoid_root_path)

if not humanoid_prim or not humanoid_prim.IsValid():
    print(f"[error] Prim not found or invalid: {humanoid_root_path}")
else:
    print(f"[humanoid] root: {humanoid_prim.GetPath()}")
    # Traverse all prims under the humanoid root using Usd.PrimRange
    for prim in Usd.PrimRange(humanoid_prim):
        print(f"[humanoid] {prim.GetPath()}")

cam_mount_parent = f"{robot_prim_path}/d435_rgb_module_link"
cam_mount_path = f"{cam_mount_parent}/eye_mount"

existing = stage.GetPrimAtPath(cam_mount_path)
if existing and existing.IsValid():
    print(f"[isaac] reusing existing prim: {cam_mount_path}")
else:
    prim_utils.create_prim(cam_mount_path, "Xform")
    print(f"[isaac] created prim: {cam_mount_path}")

# Always (re)set the local transform so reruns are deterministic
prim = stage.GetPrimAtPath(cam_mount_path)
xform_api = UsdGeom.XformCommonAPI(prim)

# Safely remove existing xform ops: delete properties, then clear op order
xformable = UsdGeom.Xformable(prim)
for op in xformable.GetOrderedXformOps():
    # Each xform op is a property on the prim; remove it by name
    prim.RemoveProperty(op.GetOpName())
# Also clear the authored order to avoid "incompatible xformable" warnings
xformable.ClearXformOpOrder()

# Set a clean local transform (meters)
xform_api.SetTranslate(Gf.Vec3d(0.03, 0.0, 0.02))
xform_api.SetRotate(Gf.Vec3f(0.0, 0.0, 0.0))
xform_api.SetScale(Gf.Vec3f(1.0, 1.0, 1.0))

# Camera init remains the same...
camera = Camera(
    prim_path=cam_mount_path + "/rgb",
    resolution=(args.width, args.height),
    frequency=args.publish_hz*2,  # Run faster than publish rate for freshness
)
camera.initialize()
for _ in range(3):
    world.step(render=True)

q = np.array([0.5, -0.5, 0.5, -0.5], dtype=np.float32)
qw, qx, qy, qz = float(q[0]), float(q[1]), float(q[2]), float(q[3])
q_gf = Gf.Quatf(qw, Gf.Vec3f(float(qx), float(qy), float(qz)))

# +90° roll using Gf.Rotation with Vec3d; then convert Quatd -> Quatf
angle_deg = float(-90.0)
roll_quat_d = Gf.Rotation(Gf.Vec3d(1.0, 0.0, 0.0), angle_deg).GetQuat()  # Quatd
roll_quat_f = Gf.Quatf(
    float(roll_quat_d.GetReal()),
    Gf.Vec3f(
        float(roll_quat_d.GetImaginary()[0]),
        float(roll_quat_d.GetImaginary()[1]),
        float(roll_quat_d.GetImaginary()[2]),
    ),
)

# Compose (order matters; this applies roll after current orientation)
q_fixed_gf = q_gf * roll_quat_f

camera.set_local_pose(
    translation=[0.0, 0.0, 0.0],
    orientation=[
        float(q_fixed_gf.GetReal()),
        float(q_fixed_gf.GetImaginary()[0]),
        float(q_fixed_gf.GetImaginary()[1]),
        float(q_fixed_gf.GetImaginary()[2]),
    ],
    camera_axes="world",
)

import math
w, h = args.width, args.height

target_fov_deg = 130.0

# ----------------------------------------------------------------------------------
# CRITICAL FIX: Do NOT use set_opencv_pinhole_properties for a 0-distortion camera!
# It forces a ray-traced physical lens model which causes severe noise at the edges.
# Instead, set the native USD focal length and horizontal aperture.
# ----------------------------------------------------------------------------------

# Use a standard 36mm full-frame sensor width
horizontal_aperture_mm = 36.0

# Calculate focal length for 130 degree FOV
focal_length_mm = (horizontal_aperture_mm / 2.0) / math.tan(math.radians(target_fov_deg) / 2.0)

camera.set_horizontal_aperture(horizontal_aperture_mm)
camera.set_vertical_aperture(horizontal_aperture_mm * (h / w))
camera.set_focal_length(focal_length_mm)

# Disable default cinematic post-processing that artificially adds noise/blur to edges
camera_prim = stage.GetPrimAtPath(cam_mount_path + "/rgb")
if camera_prim.IsValid():
    camera_prim.CreateAttribute("postProcess:chromaticAberration:chromaticAberrationEnabled", Sdf.ValueTypeNames.Bool).Set(False)
    camera_prim.CreateAttribute("postProcess:vignette:enabled", Sdf.ValueTypeNames.Bool).Set(False)
    camera_prim.CreateAttribute("postProcess:filmGrain:enabled", Sdf.ValueTypeNames.Bool).Set(False)

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
        should_render = (sim_t - last_pub_t) >= publish_period

        world.step(render=should_render)

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

        # Map cmd_vel -> policy base_command: [vx, vy, wz]
        # Keep it conservative; you can raise limits after it behaves.
        vx = float(lin[0])
        vy = float(lin[1])
        wz = float(ang[2])

        base_command[:] = np.array([vx, vy, wz], dtype=np.float32)

        # Publish JPEG CompressedImage at throttled rate
        if should_render:
            # render just-in-time so camera has a fresh frame
            world.step(render=True)

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

                t0 = time.perf_counter()
                cam_pub.publish_rgb(rgb)
                t1 = time.perf_counter()
                print(f"[pub] t={sim_t:.2f}, encode={1000*(t1-t0):.1f}ms")

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