import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_maze'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    (os.path.join('share', package_name, 'launch'), glob('launch/*')),
    (os.path.join('share', package_name, 'models', 'my_maze'),
        ['models/my_maze/model.sdf', 'models/my_maze/model.config']),
    (os.path.join('share', package_name, 'worlds'),
    ['worlds/my_maze_world.world']),
],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='beckham',
    maintainer_email='beckham@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
