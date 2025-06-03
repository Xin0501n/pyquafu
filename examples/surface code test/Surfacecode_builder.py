from quafu import QuantumCircuit, simulate
from quafu.elements import Reset

from GKSimu import GKSimulator
import copy

class SurfaceCodeCircuitBuilder:
    def __init__(self, distance: int, initial_state: str = "0", rounds: int = 1, sim_mode: str = "full"):
        """
        sim_mode: 'full' or 'gk' ..... 加解释
        """
        self.distance = distance
        self.initial_state = initial_state
        self.rounds = rounds
        self.sim_mode = sim_mode  # 'full' or 'Clifford' clifford part need to be done

        if self.distance == 2:
            self.num_data = 4
            self.num_ancilla = 3
        elif self.distance == 3:
            self.num_data = 9
            self.num_ancilla = 8
        else:
            raise ValueError("Unsupported code distance - Now")

        self.total_qubits = self.num_data + self.num_ancilla
        self.qc = QuantumCircuit(self.total_qubits, self.total_qubits)
        self._initialize_logical_state()

    def _initialize_logical_state(self):
        if self.initial_state == "+":
            for q in range(self.num_data):
                self.qc.h(q)
        elif self.initial_state == "-":
            for q in range(self.num_data):
                self.qc.x(q)
                self.qc.h(q)
        elif self.initial_state == "1":
            for q in range(self.num_data):
                self.qc.x(q)
        elif self.initial_state == "0":
            pass
        else:
            raise ValueError(f"Unsupported initial_state: {self.initial_state}")

    def _x_stabilizer(self, data_qubits, ancilla):
        Reset(ancilla)
        self.qc.h(ancilla)
        for dq in data_qubits:
            self.qc.cnot(ancilla, dq)
        self.qc.h(ancilla)

    def _z_stabilizer(self, data_qubits, ancilla):
        Reset(ancilla)
        for dq in data_qubits:
            self.qc.cnot(dq, ancilla)

    def _apply_stabilizers(self):
        if self.distance == 2:
            self._x_stabilizer([0, 1, 2, 3], 5)
            self._z_stabilizer([0, 2], 4)
            self._z_stabilizer([1, 3], 6)
        elif self.distance == 3:
            self._x_stabilizer([0, 1], 9)        # A1
            self._z_stabilizer([0, 1, 3, 4], 10) # A2
            self._x_stabilizer([1, 2, 4, 5], 11) # A3
            self._z_stabilizer([2, 5], 12)       # A4
            self._x_stabilizer([3, 4, 6, 7], 13) # A5
            self._z_stabilizer([3, 6], 14)       # A6
            self._x_stabilizer([7, 8], 15)       # A7
            self._z_stabilizer([4, 5, 7, 8], 16) # A8

    def build(self):
        # 多轮次稳定子测量
        for _ in range(self.rounds):
            self._apply_stabilizers()

        # syndrome测量（测量所有辅助量子比特）
        self.qc_syndrome = copy.deepcopy(self.qc)
        ancilla_qubits = list(range(self.num_data, self.total_qubits))
        classical_indices = list(range(len(ancilla_qubits)))
        self.qc_syndrome.measure(ancilla_qubits, classical_indices)

        # 测逻辑X或Z ----------- Z TODO
        self.qc_logical_x = copy.deepcopy(self.qc)
        if self.distance == 2:
            logical_x_qubits = [0, 2] 
        elif self.distance == 3:
            logical_x_qubits = [1, 4, 7]
        for q in logical_x_qubits:
            self.qc_logical_x.h(q)
        self.qc_logical_x.measure(logical_x_qubits, list(range(len(logical_x_qubits))))

        self.qc_logical_z = copy.deepcopy(self.qc)
        if self.distance == 2:
            logical_z_qubits = [0, 2] 
        elif self.distance == 3:
            logical_z_qubits = [1, 4, 7]
        self.qc_logical_z.measure(logical_z_qubits, list(range(len(logical_z_qubits))))

    def run(self):
        if self.sim_mode == "full":
            syndrome_result = simulate(self.qc_syndrome, shots=1, simulator="statevector")
            logical_x_result = simulate(self.qc_logical_x, shots=1, simulator="statevector")
            logical_z_result = simulate(self.qc_logical_z, shots=1, simulator="statevector")
            return syndrome_result.counts, logical_x_result.counts, logical_z_result.counts

        elif self.sim_mode == "clifford":
            # not finished
            return self._run_gottesman_knill()

        else:
            raise ValueError(f"Unsupported sim_mode: {self.sim_mode}")
        

## can be deleted -------------------------------------

    def _run_gottesman_knill(self):
        '''need to be done'''

        sim = GKSimulator(self.total_qubits)

        # 用 self.qc.gates 追踪逻辑门
        for gate in self.qc.gates:
            name = gate.name
            if name == 'h':
                sim.apply_gate("H", gate.targets[0])
            elif name == 's':
                sim.apply_gate("S", gate.targets[0])
            elif name == 'cx':
                sim.apply_gate("CNOT", gate.controls[0], gate.targets[0])

        # syndrome measurement
        syndrome = [sim.measure(q) for q in range(self.num_data, self.total_qubits)]

        # logical measurement: e.g., X_L = [1,4,7] (need apply H before measuring Z)
        logical_qubits = [1, 4, 7] if self.distance == 3 else [0, 2]
        for q in logical_qubits:
            sim.apply_gate("H", q)
        logical_bits = [sim.measure(q) for q in logical_qubits]

        return syndrome, logical_bits
        
