from abc import ABC, abstractmethod
import numpy as np

from gate_tools import GATE_SYMBOLS
import pauli_tools

class Instruction(ABC):

    @abstractmethod
    def is_gate(self) -> bool:
        raise NotImplementedError("is_gate not implemented")

    @abstractmethod
    def get_qubits(self) -> list:
        raise NotImplementedError("get_qubits not implemented")

class Gate(Instruction):

    def __init__(self, name:str, qubits:list):
        if name in GATE_SYMBOLS.keys():
            self.name = name
            self.qubits = qubits
        else:
            raise RuntimeError(f"Unknown gate {name}")

    def get_qubits(self) -> list:
        return self.qubits

    def get_name(self) -> str:
        return self.name

    def get_symbol(self) -> str:
        return GATE_SYMBOLS[self.get_name()]

    def is_gate(self) -> bool:
        return True

class Measuremt(Instruction):
    def __init__(self, qubits : list, operator : str, phase : np.complex64 = 1):
        assert(len(qubits) == len(operator))

        self.qubits = qubits
        self.operator = operator
        self.phase = phase

    def get_qubits(self) -> list:
        return self.qubits
    
    def get_operator(self) -> str:
        return self.operator
    
    def get_phase(self) -> np.complex64:
        return self.phase

    def is_gate(self) -> bool:
        return False

class Circuit:
    def __init__(self, n_qubits:int):
        self.instructions = []
        self.n_qubits = n_qubits

    def validate_qubit_number(self, qubit_no:int):
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
    
    def measure(self, qubits:list, operator:str, phase : np.complex64 = 1):
        for qubit_no in qubits:
            self.validate_qubit_number(qubit_no)
        
        self.instructions.append(Measuremt(qubits, operator, phase))
    
    def measure_all(self):
        self.instructions.append(Measuremt(qubits = [i for i in range(self.n_qubits)],
                                           operator = "Z" * self.n_qubits,
                                           phase = 1))

    def get_instructions(self) -> list:
        return self.instructions
    
    def show(self):
        # TODO: Add measurement

        for qubit in range(self.n_qubits + 1):

            print(f"{qubit}: |0> ", end = "")
            
            for instruction in self.instructions:

                if(qubit in instruction.get_qubits()):
                    if(instruction.is_gate()):
                        index = instruction.get_qubits().index(qubit)
                        print(instruction.get_symbol()[index], end = "")
                    else:
                        print("[M]", end = "")

                else:
                    print("---", end = "")
            
            print()
            

def tests():
    circuit = Circuit(n_qubits = 2)
    circuit.h(0)
    circuit.h(1)
    circuit.measure_all()
    
    circuit.show()

    print("========")

    circuit = Circuit(n_qubits = 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0], "Z")

    circuit.show()

    print("========")

    circuit = Circuit(n_qubits = 3)
    circuit.x(0)
    circuit.y(0)
    circuit.z(0)
    circuit.s(0)
    circuit.cx(0, 1)
    circuit.h(2)
    circuit.measure_all()

    circuit.show()

if __name__ == "__main__":
    tests()