# network_simulator/gui/edge_dialog.py
from tkinter import ttk
import tkinter as tk

class EdgeDialog(tk.Toplevel):
    def __init__(self, parent, nodes):
        super().__init__(parent)
        self.title("Add Edge")
        self.result = None

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Create and pack widgets
        frame = ttk.Frame(self, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Source node selection
        ttk.Label(frame, text="Source Node:").grid(row=0, column=0, pady=5)
        self.source_var = tk.StringVar()
        self.source_combo = ttk.Combobox(frame, textvariable=self.source_var, values=nodes)
        self.source_combo.grid(row=0, column=1, pady=5)

        # Target node selection
        ttk.Label(frame, text="Target Node:").grid(row=1, column=0, pady=5)
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(frame, textvariable=self.target_var, values=nodes)
        self.target_combo.grid(row=1, column=1, pady=5)

        # Weight input
        ttk.Label(frame, text="Weight:").grid(row=2, column=0, pady=5)
        self.weight_var = tk.StringVar(value="1")
        weight_entry = ttk.Entry(frame, textvariable=self.weight_var)
        weight_entry.grid(row=2, column=1, pady=5)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add", command=self.on_add).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        # Center the dialog on parent window
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")

    def on_add(self):
        source = self.source_var.get()
        target = self.target_var.get()
        try:
            weight = int(self.weight_var.get())
            if source and target and source != target:
                self.result = (source, target, weight)
                self.destroy()
            else:
                tk.messagebox.showerror("Error", "Please select different source and target nodes")
        except ValueError:
            tk.messagebox.showerror("Error", "Weight must be a number")

    def on_cancel(self):
        self.destroy()

# Update the add_edge method in MainWindow class (main_window.py)
def add_edge(self):
    nodes = list(self.network.nodes.keys())
    if len(nodes) < 2:
        tk.messagebox.showwarning("Warning", "Need at least 2 nodes to create an edge")
        return

    dialog = EdgeDialog(self.root, nodes)
    self.root.wait_window(dialog)

    if dialog.result:
        source, target, weight = dialog.result
        if (source, target) not in self.network.graph.edges():
            self.network.add_edge(source, target, weight=weight)
            self.network_canvas.update_display()
        else:
            tk.messagebox.showinfo("Info", f"Edge between {source} and {target} already exists")