import rclpy
from rclpy.node import Node
import socket
import time
import xml.etree.ElementTree as ET


class PlcTcpServer(Node):

    def __init__(self):
        super().__init__('plc_tcp_server')

        self.host = '172.20.66.196'
        self.port = 12381

        self.start_server()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(1)

        self.get_logger().info(f"Listening on {self.host}:{self.port}...")

        while True:
            client, addr = server.accept()
            self.get_logger().info(f"Connected from {addr}")

            try:
                payload = self.read_complete_xml(client)
                if payload is None:
                    self.get_logger().warn("Client disconnected before sending XML payload")
                    continue

                processing_time = self.process_xml(payload)

                response = f"{processing_time:.6f}"
                # Null-terminated ASCII is easier to consume into PLC STRING buffers.
                client.sendall((response + "\x00").encode("ascii"))
                self.get_logger().info(f"Sent processing time to PLC: {response} s")
            except Exception as e:
                self.get_logger().error(f"Request handling error: {e}")
            finally:
                self.close_client_session(client)

    def close_client_session(self, client, drain_timeout_s=0.5):
        """Perform orderly TCP shutdown so the PLC sees a clean connection end."""
        try:
            client.shutdown(socket.SHUT_WR)
        except OSError:
            # Peer may already have closed; proceed with close path.
            pass

        try:
            client.settimeout(drain_timeout_s)
            while True:
                if not client.recv(1024):
                    break
        except (socket.timeout, OSError):
            pass
        finally:
            client.close()

    def read_complete_xml(self, client, chunk_size=4096, idle_timeout_s=5.0, max_bytes=1048576):
        client.settimeout(idle_timeout_s)
        payload = bytearray()

        while len(payload) < max_bytes:
            try:
                chunk = client.recv(chunk_size)
            except socket.timeout:
                # PLC often connects early and sends later; keep waiting while no data arrived.
                if not payload:
                    continue
                break

            if not chunk:
                if not payload:
                    return None
                break

            payload.extend(chunk)

            # PLC STRING buffers can include trailing NUL bytes when full buffer size is sent.
            xml_candidate = bytes(payload).split(b'\x00', 1)[0].strip()
            if not xml_candidate:
                continue

            try:
                ET.fromstring(xml_candidate)
                return xml_candidate
            except ET.ParseError:
                continue

        if len(payload) >= max_bytes:
            self.get_logger().warn("Incoming XML exceeded max size and may be truncated")

        xml_candidate = bytes(payload).split(b'\x00', 1)[0].strip()
        return xml_candidate if xml_candidate else None

    def process_xml(self, xml_payload):
        start = time.perf_counter()

        try:
            root = ET.fromstring(xml_payload)

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


if __name__ == '__main__':
    main()