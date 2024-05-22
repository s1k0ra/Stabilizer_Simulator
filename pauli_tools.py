import itertools
import numpy as np

from gate_tools import GATE_MATRICES

PAULIS = ["I", "X", "Y", "Z"]

def commute(pauli1, pauli2) -> bool:

    z_count = 0
    for p1, p2 in zip(pauli1, pauli2):
        if(p1 != "I" and p2 != "I"):
            if(p1 != p2):
                z_count += 1 
    
    return z_count % 2 == 0 and z_count % 4 == 0

def single_pauli_product(pauli1:str, pauli2:str) -> str:

    if(pauli1 == pauli2):
        return 1, "I"

    if(pauli1 == "X" and pauli2 == "Y"):
        return 1j, "Z"
    if(pauli1 == "Y" and pauli2 == "Z"):
        return 1j, "X"
    if(pauli1 == "Z" and pauli2 == "X"):
        return 1j, "Y"
    
    if(pauli1 == "Y" and pauli2 == "X"):
        return -1j, "Z"
    if(pauli1 == "Z" and pauli2 == "Y"):
        return -1j, "X"
    if(pauli1 == "X" and pauli2 == "Z"):
        return -1j, "Y"
    
    if(pauli1 == "I"):
        return pauli2
    if(pauli2 == "I"):
        return pauli1
    
    raise RuntimeError(f"Invlaid single paulis {pauli1}, {pauli2}")        

def multiply(pauli1, pauli2, phase1 = 1, phase2 = 1):

    result_pauli = ""
    result_phase = phase1 * phase2

    for p1, p2 in zip(pauli1, pauli2):
        phase, pauli = single_pauli_product(p1, p2)

        result_pauli += pauli
        result_phase *= phase
    
    return result_phase, result_pauli
         

def to_matrix(pauli_string: str):
    # TODO check if all characters are paulis

    matrix = GATE_MATRICES[pauli_string[0]]

    for pauli in pauli_string[1:]:
        matrix = np.kron(matrix, GATE_MATRICES[pauli])
    
    return matrix

def to_pauli_string(matrix:np.array, length = 1):
    
    pauli_string = ""
    sign = 1

    matrix = np.round(matrix, 10)

    for paulis in itertools.product(PAULIS, repeat=length):

        pauli_matrix = to_matrix(paulis)

        if((matrix == pauli_matrix).all()):
            pauli_string = ''.join(paulis)
            break
        
        elif((matrix == -1 * pauli_matrix).all()):
            pauli_string = ''.join(paulis)
            sign = -1
            break
        
        elif((matrix == 1j * pauli_matrix).all()):
            pauli_string = ''.join(paulis)
            sign = 1j
            break

        elif((matrix == -1j * pauli_matrix).all()):
            pauli_string = ''.join(paulis)
            sign = -1j
            break
    
    if(pauli_string == ""):
        raise RuntimeError(f"No matching pauli for matrix {matrix}")
    
    return sign, pauli_string
