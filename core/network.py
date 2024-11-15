# network_simulator/core/network.py

from typing import Dict, List, Optional, Tuple
import networkx as nx
from core.node import Node
from core.packet import Packet, PacketStatus
from algorithms.routing import RoutingAlgorithms
import time



class Network:
    """
    Core network simulation class implementing packet routing and network management.
    Demonstrates understanding of network protocols and packet transmission.
    """

    def __init__(self):
        self.graph = nx.Graph()
        self.nodes: Dict[str, Node] = {}
        self.packets: List[Packet] = []
        self.current_time = 0
        self.metrics = {
            'packets_sent': 0,
            'packets_delivered': 0,
            'packets_dropped': 0,
            'average_latency': 0,
            'congestion_points': set()
        }

    def simulate_step(self) -> List[Dict]:
        """
        Simulates one time step of network operation.
        Handles packet movement and updates metrics.
        """
        events = []
        self.current_time += 1

        # Process packets at each node
        for node_id, node in self.nodes.items():
            # Process outgoing packets
            packets_to_remove = []
            for packet in node.queue:
                if packet.current_node == packet.destination:
                    # Packet arrived at destination
                    packet.status = PacketStatus.DELIVERED
                    packet.delivery_time = self.current_time
                    self.metrics['packets_delivered'] += 1
                    packets_to_remove.append(packet)
                    events.append({
                        'type': 'delivery',
                        'packet_id': packet.packet_id,
                        'node': node_id,
                        'time': self.current_time
                    })
                else:
                    # Forward packet to next hop
                    next_hop = self.get_next_hop(packet)
                    if next_hop and self.nodes[next_hop].can_accept_packet(packet):
                        self.nodes[next_hop].add_packet(packet)
                        packet.current_node = next_hop
                        packets_to_remove.append(packet)
                        events.append({
                            'type': 'forward',
                            'packet_id': packet.packet_id,
                            'from': node_id,
                            'to': next_hop,
                            'time': self.current_time
                        })
                    else:
                        # Congestion detected
                        self.metrics['congestion_points'].add(next_hop)
                        if len(node.queue) > node.buffer_size:
                            # Drop packet if buffer full
                            packet.status = PacketStatus.DROPPED
                            self.metrics['packets_dropped'] += 1
                            packets_to_remove.append(packet)
                            events.append({
                                'type': 'drop',
                                'packet_id': packet.packet_id,
                                'node': node_id,
                                'time': self.current_time
                            })

            # Remove processed packets
            for packet in packets_to_remove:
                node.queue.remove(packet)
                node.current_buffer -= 1

        return events

    def create_packet(self, source: str, destination: str) -> Optional[Packet]:
        """Creates and initializes a new packet in the network."""
        if source in self.nodes and destination in self.nodes:
            packet_id = len(self.packets)
            packet = Packet(packet_id, source, destination)
            packet.creation_time = self.current_time

            # Calculate initial path
            path = self.get_path(source, destination)
            if path:
                packet.path = path
                if self.nodes[source].add_packet(packet):
                    self.packets.append(packet)
                    self.metrics['packets_sent'] += 1
                    return packet
        return None

    def get_next_hop(self, packet: Packet) -> Optional[str]:
        """Determines next hop for packet based on routing algorithm."""
        current_index = packet.path.index(packet.current_node)
        if current_index < len(packet.path) - 1:
            return packet.path[current_index + 1]
        return None

    def get_metrics(self) -> Dict:
        """Returns current network performance metrics."""
        delivered_packets = [p for p in self.packets if p.status == PacketStatus.DELIVERED]
        if delivered_packets:
            avg_latency = sum(p.delivery_time - p.creation_time for p in delivered_packets) / len(delivered_packets)
            self.metrics['average_latency'] = avg_latency

        return self.metrics

    def get_link_utilization(self) -> Dict[Tuple[str, str], float]:
        """Calculates link utilization rates."""
        utilization = {}
        for u, v in self.graph.edges():
            packets_on_link = sum(1 for p in self.packets
                                if p.status == PacketStatus.IN_TRANSIT and
                                (u, v) in zip(p.path, p.path[1:]))
            utilization[(u, v)] = packets_on_link
        return utilization

    def add_node(self, node_id: str, buffer_size: int = 1000) -> None:
        """Adds a new node to the network."""
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, buffer_size)
            self.graph.add_node(node_id)

    def add_edge(self, source: str, target: str, weight: int = 1, capacity: int = 100) -> None:
        """Adds a new edge with weight and capacity."""
        if source in self.nodes and target in self.nodes:
            self.graph.add_edge(source, target, weight=weight, capacity=capacity)

    def get_path(self, source: str, target: str, algorithm: str = "dijkstra") -> Optional[List[str]]:
        """Calculates path using specified routing algorithm."""
        if not nx.has_path(self.graph, source, target):
            return None

        if algorithm == "dijkstra":
            path, _, _ = RoutingAlgorithms.dijkstra(self.graph, source, target)
        elif algorithm == "bellman_ford":
            path, _, _ = RoutingAlgorithms.bellman_ford(self.graph, source, target)
        else:
            path = nx.shortest_path(self.graph, source, target, weight="weight")

        return path