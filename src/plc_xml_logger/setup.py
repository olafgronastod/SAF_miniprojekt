from setuptools import find_packages, setup

package_name = 'plc_xml_logger'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='william',
    maintainer_email='wholm24@student.aau.dk',
    description='ROS2 node that subscribes to PLC XML topic and writes lines to a txt file',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'xml_logger = plc_xml_logger.xml_logger_node:main',
        ],
    },
)
