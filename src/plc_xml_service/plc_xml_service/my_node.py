import rclpy
from rclpy.node import Node
import socket
import time
import xml.etree.ElementTree as ET


class PlcTcpServer(Node):

    def __init__(self):
        super().__init__('plc_tcp_server')

        self.host = '172.20.66.187'
        self.port = 12381

        self.start_server()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(1)

        self.get_logger().info(f"Listening on port {self.port}...")

        while True:
            client, addr = server.accept()
            self.get_logger().info(f"Connected from {addr}")

            data = client.recv(4096).decode()

            processing_time = self.process_xml(data)

            response = f"{processing_time:.6f}"
            client.send(response.encode())

            client.close()

    def process_xml(self, xml_string):
        start = time.perf_counter()

        try:
            root = ET.fromstring(xml_string)

            # Eksempel: læs data
            for child in root:
                self.get_logger().info(f"{child.tag}: {child.text}")

        except Exception as e:
            self.get_logger().error(f"XML error: {e}")

        end = time.perf_counter()
        return end - start


def main():
    rclpy.init()
    node = PlcTcpServer()
    rclpy.spin(node)
    rclpy.shutdown()