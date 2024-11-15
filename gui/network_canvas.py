# network_simulator/gui/network_canvas.py

import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.network import Network
import time

class NetworkCanvas(ttk.Frame):
    def __init__(self, parent, network: Network):
        super().__init__(parent)
        self.network = network
        self.setup_canvas()
        self.highlighted_path = None
        self.current_path_index = 0
        self.animation_speed = 1000  # 1 second between steps
        self.is_animating = False
        self.edge_colors = {}
        self.node_colors = {}
        self.node_distances = {}
        self.packet_position = None
        self.algorithm_steps = []
        self.current_step = 0

    def setup_canvas(self):
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_display(self):
        """Updates the display with current colors and states"""
        self.ax.clear()
        pos = nx.spring_layout(self.network.graph, seed=42)  # Fixed seed for consistent layout

        # Draw edges with current colors
        edge_colors = []
        edge_widths = []
        for edge in self.network.graph.edges():
            if edge in self.edge_colors:
                edge_colors.append(self.edge_colors[edge])
                edge_widths.append(2.0)
            else:
                edge_colors.append('black')
                edge_widths.append(1.0)

        # Draw edges
        nx.draw_networkx_edges(
            self.network.graph,
            pos,
            ax=self.ax,
            edge_color=edge_colors,
            width=edge_widths
        )

        # Draw nodes with colors
        node_colors = []
        for node in self.network.graph.nodes():
            if node in self.node_colors:
                node_colors.append(self.node_colors[node])
            else:
                node_colors.append('lightblue')

        nx.draw_networkx_nodes(
            self.network.graph,
            pos,
            ax=self.ax,
            node_color=node_colors,
            node_size=500
        )

        # Draw labels with distances
        labels = {}
        for node in self.network.graph.nodes():
            if node in self.node_distances:
                dist = self.node_distances[node]
                if dist == float('infinity'):
                    labels[node] = f"{node}\n(∞)"
                else:
                    labels[node] = f"{node}\n({dist})"
            else:
                labels[node] = node

        nx.draw_networkx_labels(self.network.graph, pos, labels=labels, ax=self.ax)

        # Draw edge weights
        edge_labels = nx.get_edge_attributes(self.network.graph, 'weight')
        nx.draw_networkx_edge_labels(self.network.graph, pos, edge_labels=edge_labels)

        # Draw packet if it exists
        if self.packet_position is not None:
            self.ax.plot(self.packet_position[0], self.packet_position[1], 'ro', markersize=10)

        self.ax.set_axis_off()
        self.canvas.draw()

    def animate_shortest_path(self, path):
        """Animates the final shortest path"""
        self.reset_visualization()
        self.highlighted_path = path
        self.current_path_index = 0
        self.is_animating = True
        self.animate_path_step()

    def animate_path_step(self):
        """Animates one step of the shortest path"""
        if not self.is_animating:
            return

        if self.current_path_index < len(self.highlighted_path) - 1:
            current = self.highlighted_path[self.current_path_index]
            next_node = self.highlighted_path[self.current_path_index + 1]

            # Highlight the edge in green
            self.edge_colors[(current, next_node)] = 'green'
            self.edge_colors[(next_node, current)] = 'green'

            self.current_path_index += 1
            self.update_display()
            self.after(500, self.animate_path_step)
        else:
            self.is_animating = False

    def animate_pathfinding_process(self, steps, algorithm):
        """Animates the algorithm's step-by-step process"""
        self.reset_visualization()
        self.algorithm_steps = steps
        self.current_step = 0
        self.is_animating = True
        self.algorithm_type = algorithm
        self.process_next_step()

    def process_next_step(self):
            """Processes the next step of the algorithm animation"""
            if not self.is_animating or self.current_step >= len(self.algorithm_steps):
                self.is_animating = False
                return
            step = self.algorithm_steps[self.current_step]
            try:
                if self.algorithm_type in ["Dijkstra", "Bellman-Ford"]:
                    if step[0] == 'visit':
                        # Node being visited
                        node = step[1]
                        distance = step[2]
                        # Mark current node as being visited (yellow)
                        self.node_colors[node] = 'yellow'
                        self.node_distances[node] = distance
                        # Mark previously visited nodes in a different color (lightgreen)
                        for n in list(self.node_colors.keys()):
                            if n != node and self.node_colors[n] == 'yellow':
                                self.node_colors[n] = 'lightgreen'
                        # Color edges to unvisited neighbors
                        for neighbor in self.network.graph.neighbors(node):
                            if neighbor not in self.node_colors or self.node_colors[neighbor] not in ['yellow', 'lightgreen']:
                                self.edge_colors[(node, neighbor)] = 'blue'
                                self.edge_colors[(neighbor, node)] = 'blue'
                    elif step[0] == 'update':
                        # Edge relaxation
                        node = step[1]
                        distance = step[2]
                        # If there's a previous node specified in the step
                        if len(step) > 3:
                            prev_node = step[3]
                            # Mark the edge being used for relaxation
                            self.edge_colors[(node, prev_node)] = 'green'
                            self.edge_colors[(prev_node, node)] = 'green'
                        self.node_distances[node] = distance

                elif self.algorithm_type == "Floyd-Warshall":
                    if step[0] == 'update':
                        self.reset_visualization()
                        # Get current k-i-j values and distance
                        i, j, k = step[1], step[2], step[3]

                        # Color the nodes based on their role
                        self.node_colors[i] = 'yellow'      # Source node
                        self.node_colors[j] = 'orange'      # Destination node
                        self.node_colors[k] = 'red'         # Intermediate node

                        # Show the current distance if provided
                        if len(step) > 4:
                            dist = step[4]
                            self.node_distances[j] = dist

                        # Show the path being considered
                        if (i, k) in self.network.graph.edges():
                            self.edge_colors[(i, k)] = 'purple'  # First hop
                            self.edge_colors[(k, i)] = 'purple'
                        if (k, j) in self.network.graph.edges():
                            self.edge_colors[(k, j)] = 'purple'  # Second hop
                            self.edge_colors[(j, k)] = 'purple'

                        # Show direct edge if it exists
                        if (i, j) in self.network.graph.edges():
                            self.edge_colors[(i, j)] = 'blue'    # Direct edge
                            self.edge_colors[(j, i)] = 'blue'

                        # If a better path is found
                        if len(step) > 4 and step[4] < float('infinity'):
                            if (i, k) in self.network.graph.edges() and (k, j) in self.network.graph.edges():
                                self.edge_colors[(i, k)] = 'green'
                                self.edge_colors[(k, i)] = 'green'
                                self.edge_colors[(k, j)] = 'green'
                                self.edge_colors[(j, k)] = 'green'

                elif self.algorithm_type in ["Prim's MST", "Kruskal's MST"]:
                    if step[0] == 'add_edge':
                        # Add edge to MST
                        u, v = step[1], step[2]
                        self.edge_colors[(u, v)] = 'green'
                        self.edge_colors[(v, u)] = 'green'
                        self.node_colors[u] = 'lightgreen'
                        self.node_colors[v] = 'lightgreen'

            except Exception as e:
                print(f"Error processing step {self.current_step}: {e}")
                print(f"Step data: {step}")
                self.is_animating = False
                return

            self.current_step += 1
            self.update_display()
            self.after(1000, self.process_next_step)

    def reset_visualization(self):
        """Resets all visual elements to default state"""
        self.edge_colors = {}
        self.node_colors = {}
        self.node_distances = {}
        self.packet_position = None
        self.update_display()

    def stop_animation(self):
        """Stops any ongoing animation and resets the visualization"""
        self.is_animating = False
        self.reset_visualization()

    def animate_mst_process(self, steps):
        """Animates the MST construction process"""
        self.reset_visualization()
        self.algorithm_steps = steps
        self.current_step = 0
        self.is_animating = True
        self.algorithm_type = "MST"
        self.process_mst_steps()

    def process_mst_steps(self):
        """Processes next step of MST animation"""
        if not self.is_animating or self.current_step >= len(self.algorithm_steps):
            self.is_animating = False
            return

        step = self.algorithm_steps[self.current_step]

        if step[0] == 'add_edge':
            # Add edge to MST
            u, v = step[1], step[2]
            # Highlight edge in green
            self.edge_colors[(u, v)] = 'green'
            self.edge_colors[(v, u)] = 'green'
            # Highlight connected nodes in lightgreen
            self.node_colors[u] = 'lightgreen'
            self.node_colors[v] = 'lightgreen'

        self.current_step += 1
        self.update_display()
        self.after(1000, self.process_mst_steps)

    def highlight_mst(self, mst_edges):
        """Highlights the edges of the Minimum Spanning Tree"""
        self.reset_visualization()
        for edge in mst_edges:
            self.edge_colors[edge] = 'green'
            self.edge_colors[(edge[1], edge[0])] = 'green'
        self.update_display()