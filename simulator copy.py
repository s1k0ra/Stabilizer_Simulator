import itertools
import numpy as np

from circuit import Circuit, Gate
from gate_tools import GATE_MATRICES, get_pauli_from_matrix, get_matrix_from_pauli, PAULIS


class StabilizerTransform:

    def __init__(self, gates = ["H", "S", "I", "X", "Y", "Z", "CX"]):
        self.lookup_table = StabilizerTransform.create_lookup_table(gates)
    
    def get_transformed_stabilizer(self, gate, stab):
        if((gate, stab) in self.lookup_table.keys()):
            return self.lookup_table[(gate, stab)]
        else:
            raise RuntimeError("No result available")

    def create_lookup_table(self, gates):
        table = {}

        for gate in gates:
            gate_matrix = GATE_MATRICES[gate]
            
            # One Qubit Gate
            if (gate_matrix.shape == (2, 2)):

                for stab in PAULIS:
                    # TODO: Is conjugate transpose neccesarry (all Hermitian)
                    new_stab_matrix = gate_matrix @ GATE_MATRICES[stab] @ gate_matrix.conj().T
                    new_stab, sign = get_pauli_from_matrix(new_stab_matrix)
                    table[(gate, stab)] = (new_stab, sign)

            # Two Qubit Gate
            elif(gate_matrix.shape == (4,4)):
                for (stab_qubit_0, stab_qubit_1) in itertools.product(PAULIS, repeat=2):
                    # TODO: Is conjugate transpose neccesarry (all Hermitian)
                    stab_matrix = np.kron(GATE_MATRICES[stab_qubit_0], GATE_MATRICES[stab_qubit_1])
                    new_stab_matrix = gate_matrix @ stab_matrix  @ gate_matrix.conj().T
                    new_stab, sign = get_pauli_from_matrix(new_stab_matrix, 2)
                    table[(gate, stab_qubit_0 + stab_qubit_1)] = (new_stab, sign)
            
            else:
                raise RuntimeError(f"Unsupported gate matrix size {gate_matrix.shape}")


class CheckMatrixState:
    def __init__(self, n_qubits:int, gates = []):
        
        # [x_1 x_2 .. x_n | z_1 z_2 ... z_n ]
        self.check_matrix = np.zeros(n_qubits, 2 * n_qubits, dtype = bool)
        self.signs = np.ones(n_qubits, 1, dtype = np.complex64)
        self.state_transform = StabilizerTransform()
        self.n_qubits = n_qubits

    def init_basis_state(self):

        # Initialize to |0..0> -> Z..Z state
        for i in range(self.n_qubits):
            for j in range(self.n_qubits):
                self.check_matrix[i, self.n_qubits + j] = True
    
    def getPauli(self, stab_no:int, qubit_no:int):
        if(self.check_matrix[stab_no, qubit_no] == True and self.check_matrix[stab_no, self.n_qubits + qubit_no] == True):
            return "Y"
        elif(self.check_matrix[stab_no, qubit_no] == False):
            return "X"
        elif(self.check_matrix[stab_no, self.n_qubits + qubit_no] == False):
            return "Z"
        else:
           return "I"
    
    def setPauli(self, new_stab, stab_no:int, qubit_no:int):
        if(new_stab == "I"):
            self.check_matrix[stab_no, qubit_no] = False
            self.check_matrix[stab_no, self.n_qubits + qubit_no] = False
        
        elif(new_stab == "X"):
            self.check_matrix[stab_no, qubit_no] = True
            self.check_matrix[stab_no, self.n_qubits + qubit_no] = False
        
        elif(new_stab == "Z"):
            self.check_matrix[stab_no, qubit_no] = False
            self.check_matrix[stab_no, self.n_qubits + qubit_no] = True
        
        elif(new_stab == "Y"):
            self.check_matrix[stab_no, qubit_no] = True
            self.check_matrix[stab_no, self.n_qubits + qubit_no] = True

        else:
            raise RuntimeError(f"Unknown stabilizer: {new_stab}")


    def get_stabilizer_matrix(self, row:int):
        
        stabilizer = ""
        for i in range(self.n_qubits):
            stabilizer += self.getPauli(row, i)

        return self.signs[row, 1] * get_matrix_from_pauli(stabilizer)

    def apply_gate(self, gate:Gate):
        # transforms stabliizer g with gate U: g -> UgU^†
        
        qubits = gate.get_qubits()

        for stab_no in range(self.n_qubits):
            
            for qubit_no in qubits:
                sign, transformed_entry = transform(gate, stab_entry)

    
    def apply_gate(self, gate:Gate):
        # transforms stabliizer g with gate U: g -> UgU^†
        
        qubits = gate.get_qubits()

        for stab_no in range(self.n_qubits):

            stabilizer = ""
            
            for qubit_no in qubits:
                stabilizer += self.getPauli(stab_no, qubit_no)

            # Set sign
            trans_stabilizer, sign = self.state_transform.get_transformed_stabilizer(gate, stabilizer)
            self.signs[stab_no, 0] = sign * self.signs[stab_no, 0]

            for qubit_no, new_stab in zip(qubits, list(trans_stabilizer)):
                self.setPauli(new_stab, stab_no, qubit_no)

    
    def apply_measurement(self, measurement):

        qubits = measurement.get_qubits()
        parital_measurement_base = measurement.get_measurement_base()

        measurement_base = ""
        for i in self.n_qubits:
            if i in qubits:
                measurement_base += parital_measurement_base[0]
                parital_measurement_base = parital_measurement_base[1:]
            else:
                measurement_base += "I"

        sign = measurement.get_sign()
        measurement_matrix = sign * get_matrix_from_pauli(measurement_base)

        for stab_no in self.n_qubits:
            stab_matrix = self.get_stabilizer_matrix(stab_no, qubits)
            if(measurement_matrix @ stab_matrix != stab_matrix @ measurement_matrix):
                pass
                
    def show(self):
        for row in self.n_qubits:
            stabilizer = str(self.signs[row])
            for qubit_no in self.n_qubits:
                stabilizer += self.getPauli(row, qubit_no)
            print(f"{row} : {stabilizer}")


class MatirxSimulator:
    def execute(circuit: Circuit):
        state = CheckMatrixState(circuit.n_qubits)

        for instruction in circuit.get_instructions():
            if(instruction.is_gate()):
                state = state.apply_gate(instruction)
            else:
                state = state.apply_measurement(instruction)

        state.show()


# clifford tableau simulation

def test():
    circuit = Circuit()
    circuit.h(0)
    circuit.h(1)
    circuit.show()

    simulator = MatirxSimulator()
    state = simulator.execute(circuit)

    print(state)


if "__main__" == __name__ :
    test()