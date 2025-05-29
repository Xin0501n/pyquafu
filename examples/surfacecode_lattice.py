import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines

class SurfaceCodeVisualizer:
    def __init__(self, grid_size=(7, 7)):
        self.grid_size = grid_size  # canvas
        self.qubits = {}  # key: (x, y), value: {'idx': int, 'type': str}
        self.gates_by_time = {}  # key: time step, value: list of gates

    def add_qubit(self, x, y, qtype="data", idx=None):
        self.qubits[(x, y)] = {'type': qtype, 'idx': idx}

    def add_gate(self, gate_type, qubit_positions, time_step=1):
        if time_step not in self.gates_by_time:
            self.gates_by_time[time_step] = []
        self.gates_by_time[time_step].append({'type': gate_type.upper(), 'qubits': qubit_positions})

    def draw(self, time_step=0):
        fig, ax = plt.subplots(figsize=(8, 8))

        # 网格
        for x in range(self.grid_size[0]):
            ax.axvline(x, color='lightgray', linestyle='--', linewidth=0.5)
        for y in range(self.grid_size[1]):
            ax.axhline(y, color='lightgray', linestyle='--', linewidth=0.5)

        # qubits
        for (x, y), props in self.qubits.items():
            if props['type'] == 'data':
                ax.add_patch(patches.Circle((x, y), 0.1, color='blue'))
            elif props['type'] == 'x_ancilla':
                ax.add_patch(patches.Rectangle((x - 0.2, y - 0.2), 0.4, 0.4, color='green'))
            elif props['type'] == 'z_ancilla':
                ax.add_patch(patches.RegularPolygon(xy=(x, y), numVertices=6, radius=0.2, orientation=0, color='red'))
            if props['idx'] is not None:
                ax.text(x, y + 0.25, f"{props['idx']}", ha='center', fontsize=8)

        # gates only up to time_step
        for t in sorted(self.gates_by_time.keys()):
            if t > time_step:
                continue
            for gate in self.gates_by_time[t]:
                if gate['type'] == 'CX' and len(gate['qubits']) == 2:
                    (x1, y1), (x2, y2) = gate['qubits']
                    # control
                    ax.plot(x1, y1, 'ko', markersize=10)
                    # target
                    ax.plot(x2, y2, 'wo', markersize=15, markeredgecolor='black')
                    ax.plot([x2, x2], [y2 - 0.15, y2 + 0.15], 'k-')
                    ax.plot([x2 - 0.15, x2 + 0.15], [y2, y2], 'k-')
                    # line between
                    ax.add_line(lines.Line2D([x1, x2], [y1, y2], color='black'))

                # Add more gate types ---------- TODO

        ax.set_xlim(-1, self.grid_size[0])
        ax.set_ylim(-1, self.grid_size[1])
        ax.set_aspect('equal')
        ax.set_xticks(range(self.grid_size[0]))
        ax.set_yticks(range(self.grid_size[1]))
        ax.grid(False)
        plt.show()

    def load_standard_distance_3(self):
        # D: data, A: ancilla
        self.add_qubit(2, 6, "x_ancilla", "A1")

        self.add_qubit(1, 5, "data", "D1")
        self.add_qubit(3, 5, "data", "D2")
        self.add_qubit(5, 5, "data", "D3")

        self.add_qubit(6, 4, "z_ancilla", "A4")
        self.add_qubit(2, 4, "z_ancilla", "A2")
        self.add_qubit(4, 4, "x_ancilla", "A3")

        self.add_qubit(1, 3, "data", "D4")
        self.add_qubit(3, 3, "data", "D5")
        self.add_qubit(5, 3, "data", "D6")

        self.add_qubit(0, 2, "z_ancilla", "A5")
        self.add_qubit(2, 2, "x_ancilla", "A6")
        self.add_qubit(4, 2, "z_ancilla", "A7")

        self.add_qubit(1, 1, "data", "D7")
        self.add_qubit(3, 1, "data", "D8")
        self.add_qubit(5, 1, "data", "D9")

        self.add_qubit(4, 0, "x_ancilla", "A8")
