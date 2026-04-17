import os
import json
from datetime import datetime

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class PlcXmlLogger(Node):
    def __init__(self):
        super().__init__('plc_xml_logger')

        self.declare_parameter('output_file', '/tmp/plc_xml_data.txt')
        self.output_file = self.get_parameter('output_file').get_parameter_value().string_value

        self.subscription = self.create_subscription(
            String,
            'plc_xml_data',
            self.handle_message,
            10,
        )

        self.ensure_parent_directory()
        self.get_logger().info(f'Writing incoming PLC XML to {self.output_file}')

    def ensure_parent_directory(self):
        parent = os.path.dirname(self.output_file)
        if parent:
            os.makedirs(parent, exist_ok=True)

    def handle_message(self, msg):
        timestamp = datetime.now().isoformat(timespec='milliseconds')
        xml_payload = msg.data
        processing_time = None

        try:
            parsed = json.loads(msg.data)
            if isinstance(parsed, dict):
                xml_payload = parsed.get('xml_payload', msg.data)
                processing_time = parsed.get('processing_time_s')
        except json.JSONDecodeError:
            pass

        if processing_time is None:
            line = f'[{timestamp}] processing_time_s=unknown xml={xml_payload}\n'
        else:
            line = f'[{timestamp}] processing_time_s={processing_time:.6f} xml={xml_payload}\n'

        try:
            with open(self.output_file, 'a', encoding='utf-8') as txt_file:
                txt_file.write(line)
            self.get_logger().info('Wrote one message to txt file')
        except OSError as exc:
            self.get_logger().error(f'Failed to write to {self.output_file}: {exc}')


def main(args=None):
    rclpy.init(args=args)
    node = PlcXmlLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
