# network_simulator/core/node.py

from typing import List
from .packet import Packet

class Node:
    def __init__(self, node_id: str, buffer_size: int = 1000):
        self.node_id = node_id
        self.buffer_size = buffer_size
        self.current_buffer = 0
        self.queue: List[Packet] = []

    def can_accept_packet(self, packet: Packet) -> bool:
        return self.current_buffer < self.buffer_size

    def add_packet(self, packet: Packet) -> bool:
        if self.can_accept_packet(packet):
            self.queue.append(packet)
            self.current_buffer += 1
            return True
        return False
