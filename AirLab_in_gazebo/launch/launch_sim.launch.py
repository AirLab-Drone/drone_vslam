import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition

from launch_ros.actions import Node



def generate_launch_description():

    robot_name = LaunchConfiguration('robot_name')
    height = LaunchConfiguration('height')

    package_name='AirLab_in_gazebo'

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), 
                launch_arguments = {'use_sim_time': 'true',
                                    'use_ros2_control': 'true'}.items()
    )

    gazebo_params_file = os.path.join(get_package_share_directory(package_name),'configs','gazebo_params.yaml')

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
                    launch_arguments={'extra_gazebo_args': '--ros-args --params-file ' + gazebo_params_file
                    }.items()
             )

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', robot_name,
                                   '-z', height],
                        output='screen')

    # rviz2
    rviz =  Node(
        package='rviz2',
        namespace='',
        executable='rviz2',
        name='rviz2',
        condition=IfCondition(LaunchConfiguration("rviz")),
        arguments=['-d' + os.path.join(get_package_share_directory(package_name), 'configs', 'sim.rviz')]
        )



    # Launch them all!
    return LaunchDescription([

        # Launch arguments
        DeclareLaunchArgument(
            'robot_name', default_value='airlab_drone',
            description='The name of robot'),

        DeclareLaunchArgument(
            'height', default_value='0.13',
            description='The height of robot generate'),

        DeclareLaunchArgument(
            'rviz', default_value='false', 
            description='Launch RVIZ (optional).'),


        rsp,
        gazebo,
        spawn_entity,
        rviz,

    ])