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
        self.packet_position = None

    def setup_canvas(self):
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_display(self, highlight_edges=None):
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

        # Draw nodes
        nx.draw_networkx_nodes(
            self.network.graph,
            pos,
            ax=self.ax,
            node_color='lightblue',
            node_size=500
        )

        # Draw labels
        nx.draw_networkx_labels(self.network.graph, pos, ax=self.ax)

        # Draw edge weights
        edge_labels = nx.get_edge_attributes(self.network.graph, 'weight')
        nx.draw_networkx_edge_labels(self.network.graph, pos, edge_labels=edge_labels)

        # Draw packet if it exists
        if self.packet_position is not None:
            self.ax.plot(self.packet_position[0], self.packet_position[1], 'ro', markersize=10)

        self.ax.set_axis_off()
        self.canvas.draw()

    def animate_path(self, path):
        self.highlighted_path = path
        self.current_path_index = 0
        self.is_animating = True
        self.edge_colors = {}  # Reset colors
        self.highlight_next_edge()

    def highlight_next_edge(self):
        if not self.is_animating:
            return

        if self.current_path_index < len(self.highlighted_path) - 1:
            # Get current edge
            current_node = self.highlighted_path[self.current_path_index]
            next_node = self.highlighted_path[self.current_path_index + 1]

            # Color the edge green
            self.edge_colors[(current_node, next_node)] = 'green'
            self.edge_colors[(next_node, current_node)] = 'green'  # For undirected graph

            self.current_path_index += 1
            self.update_display()

            # Schedule next highlight
            self.after(self.animation_speed, self.highlight_next_edge)
        else:
            self.is_animating = False

    def stop_animation(self):
        self.is_animating = False
        self.edge_colors = {}  # Reset colors
        self.packet_position = None
        self.update_display()

    def highlight_mst(self, mst_edges):
        """Highlight Minimum Spanning Tree edges"""
        self.edge_colors = {}
        for edge in mst_edges:
            self.edge_colors[edge] = 'green'
            self.edge_colors[(edge[1], edge[0])] = 'green'  # For undirected graph
        self.update_display()