import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('my_maze_robot')
    urdf_file = os.path.join(pkg_dir, 'urdf', 'my_robot.urdf')

    return LaunchDescription([
        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': open(urdf_file).read()}]
        ),

        # Flood fill maze solver node
        Node(
            package='my_maze_robot',
            executable='maze_floodfill_node.py',
            name='maze_floodfill_node',
            output='screen'
        ),
    ])

