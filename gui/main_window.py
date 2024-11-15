# network_simulator/gui/main_window.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui.network_canvas import NetworkCanvas
from core.network import Network
from algorithms.routing import RoutingAlgorithms
from gui.edge_dialog import EdgeDialog

class MainWindow:
    def __init__(self, root=None):
        # Use passed root or create new one
        self.root = root if root else tk.Tk()
        self.root.title("Network Simulator")
        self.root.geometry("1200x800")
        self.network = Network()

        # Bind quit event to 'q' key
        self.root.bind('<q>', self.quit_program)
        self.root.bind('<Q>', self.quit_program)  # Also bind capital Q

        # Add window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.quit_program)

        self.setup_gui()
        self.selected_nodes = []  # To store nodes selected for edge creation

    def setup_gui(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left control panel
        self.control_frame = ttk.LabelFrame(main_container, text="Controls", padding="5")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Network visualization
        self.canvas_frame = ttk.LabelFrame(main_container, text="Network Topology", padding="5")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.network_canvas = NetworkCanvas(self.canvas_frame, self.network)
        self.network_canvas.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Press 'q' to quit", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Withdraw the extra window if it exists
        for window in tk.Tk.winfo_children(tk._default_root):
            if isinstance(window, tk.Toplevel):
                window.withdraw()

        # Control panel contents
        self.setup_controls()

    def setup_controls(self):
        # File Operations
        file_frame = ttk.LabelFrame(self.control_frame, text="File Operations", padding="5")
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(file_frame, text="Load Graph from File",
                  command=self.load_graph).pack(fill=tk.X, pady=2)

        # Node Management
        node_frame = ttk.LabelFrame(self.control_frame, text="Node Management", padding="5")
        node_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(node_frame, text="Add Node",
                  command=self.add_node).pack(fill=tk.X, pady=2)

        # Edge Management
        edge_frame = ttk.LabelFrame(self.control_frame, text="Edge Management", padding="5")
        edge_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(edge_frame, text="Add Edge",
                  command=self.add_edge).pack(fill=tk.X, pady=2)

        # Algorithm Selection
        algo_frame = ttk.LabelFrame(self.control_frame, text="Routing Algorithm", padding="5")
        algo_frame.pack(fill=tk.X, padx=5, pady=5)

        algorithms = ["Dijkstra", "Bellman-Ford", "Floyd-Warshall",
                     "Prim's MST", "Kruskal's MST"]
        self.algorithm_var = tk.StringVar(value=algorithms[0])
        ttk.OptionMenu(algo_frame, self.algorithm_var,
                      algorithms[0], *algorithms).pack(fill=tk.X, pady=2)

        # Simulation Controls
        sim_frame = ttk.LabelFrame(self.control_frame, text="Simulation", padding="5")
        sim_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(sim_frame, text="Send Packet",
                  command=self.send_packet).pack(fill=tk.X, pady=2)
        ttk.Button(sim_frame, text="Start Simulation",
                  command=self.start_simulation).pack(fill=tk.X, pady=2)
        ttk.Button(sim_frame, text="Stop Simulation",
                  command=self.stop_simulation).pack(fill=tk.X, pady=2)

        # Quit Button (at the bottom of control panel)
        quit_frame = ttk.Frame(self.control_frame)
        quit_frame.pack(fill=tk.X, padx=5, pady=20)
        ttk.Button(quit_frame, text="Quit",
                  command=self.quit_program,
                  style="Accent.TButton").pack(fill=tk.X)

    def load_graph(self):
        """Load graph from a file"""
        filename = filedialog.askopenfilename(
            title="Select Graph File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Clear existing graph
                self.network = Network()

                with open(filename, 'r') as f:
                    # Read first line containing number of vertices and edges
                    n, m = map(int, f.readline().split())

                    # Create nodes
                    for i in range(n):
                        self.network.add_node(str(i))

                    # Read edges
                    for _ in range(m):
                        u, v, w = map(int, f.readline().split())
                        self.network.add_edge(str(u), str(v), weight=w)

                self.network_canvas.network = self.network
                self.network_canvas.update_display()
                messagebox.showinfo("Success", "Graph loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load graph: {str(e)}")

    def quit_program(self, event=None):
        """Gracefully quit the program"""
        if hasattr(self, 'simulation_running') and self.simulation_running:
            self.stop_simulation()

        if messagebox.askokcancel("Quit", "Do you want to quit the Network Simulator?"):
            self.root.quit()
            self.root.destroy()

    def add_node(self):
        node_id = f"N{len(self.network.nodes)}"
        self.network.add_node(node_id)
        self.network_canvas.update_display()

    def add_edge(self):
        nodes = list(self.network.nodes.keys())
        if len(nodes) < 2:
            messagebox.showwarning("Warning", "Need at least 2 nodes to create an edge")
            return

        dialog = EdgeDialog(self.root, nodes)
        self.root.wait_window(dialog)

        if dialog.result:
            source, target, weight = dialog.result
            if (source, target) not in self.network.graph.edges():
                self.network.add_edge(source, target, weight=weight)
                self.network_canvas.update_display()
            else:
                messagebox.showinfo("Info", f"Edge between {source} and {target} already exists")

    def send_packet(self):
        """Shows the final shortest path for the selected algorithm"""
        nodes = list(self.network.nodes.keys())
        if len(nodes) >= 2:
            source = nodes[0]
            destination = nodes[-1]
            algorithm = self.algorithm_var.get()

            try:
                path = None
                # Get shortest path based on selected algorithm
                if algorithm == "Dijkstra":
                    path, _, _ = RoutingAlgorithms.dijkstra(self.network.graph, source, destination)
                elif algorithm == "Bellman-Ford":
                    path, _, _ = RoutingAlgorithms.bellman_ford(self.network.graph, source, destination)
                elif algorithm == "Floyd-Warshall":
                    dist, next_hop, _ = RoutingAlgorithms.floyd_warshall(self.network.graph)
                    path = self.reconstruct_path(source, destination, next_hop)
                elif algorithm in ["Prim's MST", "Kruskal's MST"]:
                    messagebox.showinfo("Info", "Packet sending is only available for path-finding algorithms")
                    return

                if path:
                    # Animate the final path
                    self.network_canvas.animate_shortest_path(path)
                    self.status_bar.config(text=f"Shortest path from {source} to {destination} using {algorithm}")
                else:
                    messagebox.showwarning("Warning", "No path found between selected nodes")
            except Exception as e:
                messagebox.showerror("Error", f"Algorithm failed: {str(e)}")

    def reconstruct_path(self, source, destination, next_hop):
        """Reconstruct path from Floyd-Warshall next_hop matrix"""
        path = [source]
        while source != destination:
            source = next_hop[(source, destination)]
            if source is None:
                return None
            path.append(source)
        return path

    def start_simulation(self):
        """Shows the step-by-step process of the selected algorithm"""
        algorithm = self.algorithm_var.get()
        nodes = list(self.network.nodes.keys())

        if not nodes:
            messagebox.showwarning("Warning", "No nodes in the network")
            return

        if algorithm in ["Prim's MST", "Kruskal's MST"]:
            # For MST algorithms
            try:
                if algorithm == "Prim's MST":
                    _, steps = RoutingAlgorithms.prim_mst(self.network.graph)
                else:
                    _, steps = RoutingAlgorithms.kruskal_mst(self.network.graph)

                self.network_canvas.animate_mst_process(steps)
                self.status_bar.config(text=f"Showing {algorithm} construction process")
            except Exception as e:
                messagebox.showerror("Error", f"Algorithm failed: {str(e)}")
        else:
            # For path-finding algorithms
            if len(nodes) >= 2:
                source = nodes[0]
                destination = nodes[-1]

                try:
                    # Get algorithm steps
                    steps = None
                    if algorithm == "Dijkstra":
                        _, _, steps = RoutingAlgorithms.dijkstra(self.network.graph, source, destination)
                    elif algorithm == "Bellman-Ford":
                        _, _, steps = RoutingAlgorithms.bellman_ford(self.network.graph, source, destination)
                    elif algorithm == "Floyd-Warshall":
                        _, _, steps = RoutingAlgorithms.floyd_warshall(self.network.graph)

                    if steps:
                        self.network_canvas.animate_pathfinding_process(steps, algorithm)
                        self.status_bar.config(text=f"Showing {algorithm} algorithm process")
                    else:
                        messagebox.showwarning("Warning", "No steps generated")
                except Exception as e:
                    messagebox.showerror("Error", f"Algorithm failed: {str(e)}")

    def stop_simulation(self):
        """Stop simulation and reset visualization"""
        self.network_canvas.stop_animation()
        self.status_bar.config(text="Simulation stopped")

    def run(self):
        # Create custom style for quit button
        style = ttk.Style()
        style.configure("Accent.TButton",
                       foreground="red",
                       padding=5)

        self.root.mainloop()