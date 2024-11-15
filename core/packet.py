# network_simulator/core/packet.py

from enum import Enum
from typing import List, Optional
from time import time

class PacketStatus(Enum):
    CREATED = "Created"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    DROPPED = "Dropped"

class Packet:
    def __init__(self, packet_id: int, source: str, destination: str):
        self.packet_id = packet_id
        self.source = source
        self.destination = destination
        self.status = PacketStatus.CREATED
        self.current_node = source
        self.path: List[str] = []
        self.creation_time = time()
        self.delivery_time: Optional[float] = None