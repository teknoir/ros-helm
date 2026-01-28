# python
from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'tb3_headless_launch'

def package_path(*parts):
    return os.path.join(package_name, *parts)

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        (os.path.join('share', package_name, 'models'), glob('models/**/*', recursive=True)),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tekn0ir',
    maintainer_email='anders.aslund@teknoir.ai',
    description='Headless launch files for TurtleBot3 Gazebo Sim',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={'console_scripts': []},
)