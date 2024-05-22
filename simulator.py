import itertools
import numpy as np
import itertools

import gate_tools
import pauli_tools
from circuit import Circuit, Gate

def has_sign(complex_number: np.complex64) -> bool:

    real = np.real(complex_number)
    imag = np.imag(complex_number)

    if(real != 0 and imag != 0):
        raise RuntimeError(f"Sign can't be determined of number {complex_number}")
    
    if(real < 0 or imag < 0):
        return True
    
    return False

def phase_to_string(complex_number: np.complex64) -> str:

    real = np.real(complex_number)
    imag = np.imag(complex_number)

    if(real == 1 and imag == 0):
        return ""
    if(real == -1 and imag == 0):
        return "-"
    if(real == 0 and imag == 1):
        return "i"
    if(real == 0 and imag == -1):
        return "-i"
    
    raise RuntimeError(f"Invalid phase {complex_number}")


class CheckMatrixState:
    def __init__(self, n_qubits: int):
        # [x_1 x_2 .. x_n | z_1 z_2 ... z_n ]

        self.check_matrix = np.zeros((n_qubits, 2 * n_qubits), dtype = bool)
        self.phase = np.ones((n_qubits,), dtype = np.complex64)
        self.n_qubits = n_qubits
        
    def init_basis_state(self):
        # Initialize to |0..0> -> Z1,..,Zn state

        for i in range(self.n_qubits):
            for j in range(self.n_qubits):
                if(i == j):
                    self.check_matrix[i, self.n_qubits + j] = True
    

    def apply_gate(self, qubits: list, pauli_gate_map: dict):
        # transforms stablizer g with gate U: g -> UgU^†

        for stab_no in range(self.n_qubits):
            
            current_phase = self.phase[stab_no]
            current_stab = self.get_stabilizer(stab_no, qubits)
            
            phase, transformed_stab = pauli_gate_map[current_stab]
            phase *= current_phase

            self.phase[stab_no] = phase
            self.set_stabilizer(new_stab=transformed_stab, stab_no=stab_no, qubits=qubits)

    
    def apply_measurement(self, qubits: list, operator: str, phase: np.complex64) -> int:

        anti_cummotors = []

        for stab_no in range(self.n_qubits):
            stab = self.get_stabilizer(stab_no=stab_no, qubits=qubits)

            if not (pauli_tools.commute(pauli1=stab, pauli2=operator)):
                anti_cummotors.append(stab_no)

        # Case 1
        if(len(anti_cummotors) == 0):

            op_sign = -1 if has_sign(phase) else 1

            for stab_no in range(self.n_qubits):

                stab = self.get_stabilizer(stab_no=stab_no, qubits=qubits)
                stab_sign = -1 if has_sign(self.phase[stab_no]) else 1

                if(stab == operator):
                    
                    if(op_sign == stab_sign):
                        return 1
                    
                    else:
                        return -1
            
            raise RuntimeError("Measurement operator should be part of Stabilizers")

        # Case 2
        else:
            anti_stab_no = anti_cummotors[0]
            anti_stabilizer = self.get_stabilizer(stab_no = anti_stab_no, qubits=qubits)

            anti_cummotors = anti_cummotors[1:]
            while(len(anti_cummotors) > 0):
                stab_no = anti_cummotors.pop()

                anti_stabilizer_two = self.get_stabilizer(stab_no=stab_no, qubits=qubits)
                new_phase, com_stabilizer = pauli_tools.multiply(pauli1=anti_stabilizer, 
                                                            pauli2=anti_stabilizer_two,
                                                            phase1=self.phase[anti_stab_no],
                                                            phase2=self.phase[stab_no])

                self.set_stabilizer(com_stabilizer, stab_no=stab_no, qubits=qubits)
                self.phase[stab_no] = new_phase
            
            # +1 Measurement Pr[+1] = 1/2
            if(np.random.choice([True, False])):
                self.set_stabilizer(new_stab=operator, stab_no=anti_stab_no, qubits=qubits)
                self.phase[anti_stab_no] *= phase
                return 1

            # -1 Measurement Pr[-1] = 1/2
            else:
                self.set_stabilizer(new_stab=operator, stab_no=anti_stab_no, qubits=qubits)
                self.phase[anti_stab_no] *= -1 * phase
                return -1

    def getPauli(self, stab_no:int, qubit_no:int) -> str:
        if(self.check_matrix[stab_no, qubit_no] == True and self.check_matrix[stab_no, self.n_qubits + qubit_no] == True):
            return "Y"
        elif(self.check_matrix[stab_no, qubit_no] == True):
            return "X"
        elif(self.check_matrix[stab_no, self.n_qubits + qubit_no] == True):
            return "Z"
        else:
           return "I"
    
    def get_stabilizer(self, stab_no: int, qubits: list = None) -> str:
        
        if(qubits is None):
            qubits = [qubit_no for qubit_no in range(self.n_qubits)]

        stabilizer = ""

        for qubit_no in qubits:
            stabilizer += self.getPauli(stab_no=stab_no, qubit_no=qubit_no)

        return stabilizer

    def set_stabilizer(self, new_stab: str, stab_no: int, qubits: list):

        for qubit_no, pauli in zip(qubits, new_stab):
            self.setPauli(new_stab=pauli, stab_no=stab_no, qubit_no=qubit_no)


    def setPauli(self, new_stab: str, stab_no: int, qubit_no: int):
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

    def get_pauli_strings(self) -> list:
        stabilizers = []

        for row in range(self.n_qubits):
            stabilizer = str(phase_to_string(self.phase[row]))

            for qubit_no in range(self.n_qubits):
                stabilizer += self.getPauli(row, qubit_no)
            stabilizers.append(stabilizer)

        return stabilizers

    def show(self):
        for row in range(self.n_qubits):
            stabilizer = str(self.phase[row])
            for qubit_no in range(self.n_qubits):
                stabilizer += self.getPauli(row, qubit_no)
            print(f"{row} : {stabilizer}")
    


class MatrixSimulator:

    def __init__(self, gates = ["H", "S", "I", "X", "Y", "Z", "CX"]):
        self.lookup_table = self.create_lookup_table(gates)

    def create_lookup_table(self, gates: list) -> dict:
        table = {}
        
        for gate_name in gates:
            
            table[gate_name] = {}
            n_qubit_gate = gate_tools.get_num_qubits(gate_name = gate_name)
            
            for pauli_string in itertools.product(["I", "X", "Y", "Z"], repeat = n_qubit_gate):
                # transform pauli p with clifford gate U: p -> UpU^†

                pauli_string = "".join(pauli_string)

                gate_matrix = gate_tools.to_matrix(gate_name)
                pauli_matrix = pauli_tools.to_matrix(pauli_string)

                conjugated_pauli = gate_matrix @ pauli_matrix @ gate_matrix.conj().T
                phase, conjugated_pauli_string = pauli_tools.to_pauli_string(conjugated_pauli, n_qubit_gate)

                table[gate_name][pauli_string] = (phase, conjugated_pauli_string)
            
        return table


    def execute(self, circuit: Circuit) -> CheckMatrixState:
        
        state = CheckMatrixState(circuit.n_qubits)
        state.init_basis_state()

        for instruction in circuit.get_instructions():
            if(instruction.is_gate()):
                state.apply_gate(qubits = instruction.get_qubits(),
                                         pauli_gate_map = self.lookup_table[instruction.get_name()])
            else:
                res = state.apply_measurement(qubits = instruction.get_qubits(), 
                                              operator = instruction.get_operator(), 
                                              phase = instruction.get_phase())
                print(f"M: qubit {instruction.get_qubits()} measured {res} for operator {instruction.get_operator()}")

        return state

