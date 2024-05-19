from abc import ABC, abstractmethod

from gate_tools import GATE_SYMBOLS
import pauli_tools

class Instruction(ABC):

    @abstractmethod
    def is_gate(self):
        raise NotImplementedError("is_gate not implemented")

    @abstractmethod
    def get_qubits(self):
        raise NotImplementedError("get_qubits not implemented")

class Gate(Instruction):

    def __init__(self, name, qubits):
        if name in GATE_SYMBOLS.keys():
            self.name = name
            self.qubits = qubits
        else:
            raise RuntimeError(f"Unknown gate {name}")

    def get_qubits(self):
        return self.qubits

    def get_name(self):
        return self.name

    def get_symbol(self):
        return GATE_SYMBOLS[self.get_name()]

    def is_gate(self):
        return True

class Measuremt(Instruction):
    def __init__(self, qubits : list, operator : str, phase = 1):
        assert(len(qubits) == len(operator))

        self.qubits = qubits
        self.operator = operator
        self.phase = phase

    def get_qubits(self):
        return self.qubits
    
    def get_operator(self):
        return self.operator
    
    def get_phase(self):
        return self.phase

    def is_gate(self):
        return False

class Circuit:
    def __init__(self, n_qubits):
        self.instructions = []
        self.n_qubits = n_qubits

    def validate_qubit_number(self, qubit_no):
        if(qubit_no >= self.n_qubits):
            raise RuntimeError(f"Qubit number {qubit_no} exceeds number of n_qubits {self.n_qubits}")
        
        if(qubit_no < 0):
            raise RuntimeError(f"Invalied qubit number {qubit_no}")

    def h(self, qubit_no:int):
        self.validate_qubit_number(qubit_no)
        self.instructions.append(Gate("H", [qubit_no]))

    def s(self, qubit_no:int):
        self.validate_qubit_number(qubit_no)
        self.instructions.append(Gate("S", [qubit_no]))
    
    def x(self, qubit_no:int):
        self.validate_qubit_number(qubit_no)
        self.instructions.append(Gate("X", [qubit_no]))
    
    def y(self, qubit_no:int):
        self.validate_qubit_number(qubit_no)
        self.instructions.append(Gate("Y", [qubit_no]))
    
    def z(self, qubit_no:int):
        self.validate_qubit_number(qubit_no)
        self.instructions.append(Gate("Z", [qubit_no]))

    def cx(self, control_qubit:int, target_qubit:int):
        self.validate_qubit_number(control_qubit)
        self.validate_qubit_number(target_qubit)
        self.instructions.append(Gate("CX", [control_qubit, target_qubit]))
    
    def measure(self, qubits:list, operator:str, phase = 1):
        for qubit_no in qubits:
            self.validate_qubit_number(qubit_no)
        
        self.instructions.append(Measuremt(qubits, operator, phase))
    
    def measure_all(self):
        self.instructions.append(Measuremt(qubits = [i for i in range(self.n_qubits)],
                                           operator = "Z" * self.n_qubits,
                                           phase = 1))

    def get_instructions(self):
        return self.instructions
    
    def show(self):
        # TODO: Add measurement

        for qubit in range(self.n_qubits + 1):

            print(f"{qubit}: |0> ", end = "")
            
            for gate in self.instructions:

                if(qubit in gate.get_qubits()):
                    index = gate.get_qubits().index(qubit)
                    print(gate.get_symbol()[index], end = "")

                else:
                    print("---", end = "")
            
            print()
            

def tests():
    circuit = Circuit()
    circuit.h(0)
    circuit.h(1)
    circuit.show()

    print("========")

    circuit = Circuit()
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.show()

    print("========")

    circuit = Circuit()
    circuit.x(0)
    circuit.y(0)
    circuit.z(0)
    circuit.s(0)
    circuit.cx(0, 1)
    circuit.h(3)
    circuit.show()

if __name__ == "__main__":
    tests()