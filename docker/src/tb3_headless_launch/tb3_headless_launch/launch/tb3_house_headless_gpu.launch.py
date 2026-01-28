# python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    launch_file_dir = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')

    world = os.path.join(
        get_package_share_directory('tb3_headless_launch'),
        'worlds',
        'turtlebot3_house_lite.world'
    )

    # Prefer GPU rendering (Ogre2) and headless server
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            # -r: run, -s: server-only, -v0: minimal logs; enforce ogre2 to use GPU
            'gz_args': ['--headless-rendering -r -s -v0 --render-engine ogre2 ', world],
            'on_exit_shutdown': 'true'
        }.items()
    )

    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    spawn_turtlebot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, 'spawn_turtlebot3.launch.py')
        ),
        launch_arguments={'x_pose': x_pose, 'y_pose': y_pose}.items()
    )

    # Resource path for models
    set_env_vars_local_resources = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(get_package_share_directory('tb3_headless_launch'), 'models'))
    set_env_vars_resources = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'models'))


    # Force GPU rendering and avoid software fallbacks on macOS
    set_env_render_engine = AppendEnvironmentVariable('GZ_RENDER_ENGINE', 'ogre2')
    set_env_disable_software = AppendEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '0')

    ld = LaunchDescription()
    ld.add_action(gzserver_cmd)
    ld.add_action(spawn_turtlebot_cmd)
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(set_env_vars_local_resources)
    ld.add_action(set_env_vars_resources)
    ld.add_action(set_env_render_engine)
    ld.add_action(set_env_disable_software)
    return ld
