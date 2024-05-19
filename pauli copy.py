import itertools
import numpy as np

from gate_tools import GATE_MATRICES

PAULIS = ["I", "X", "Y", "Z"]

def valid_pauli(pauli):
    for i,p in enumerate(pauli):
        if(p in PAULIS):
            continue
        if(p == "-" or p == "i" and i < len(pauli) - 1):
            continue
        return False
    return True

def split_phase(pauli_string):
    phase = 1

    i_count = pauli_string.count('i')
    sign_count = pauli_string.count('-') + i_count // 2

    if(sign_count % 2 == 1):
        phase = -1

    if(i_count % 2 == 1):
        phase *= 1j
    
    return pauli_string.replace('-','').replace('i', ''), phase
        

def commute(pauli1, pauli2) -> bool:

    pauli1, _ = split_phase(pauli1)
    pauli2, _ = split_phase(pauli2)

    z_count = 0
    for p1, p2 in zip(pauli1, pauli2):
        if(p1 != "I" and p2 != "I"):
            if(p1 != p2):
                z_count += 1
    
    return z_count % 2 == 0

def single_product(pauli1:str, pauli2:str) -> str:
    if(pauli1 == "X" and pauli2 == "Y"):
        return "iZ"
    if(pauli1 == "Y" and pauli2 == "Z"):
        return "iX"
    if(pauli1 == "Z" and pauli2 == "X"):
        return "iY"
    
    if(pauli1 == "Y" and pauli2 == "X"):
        return "-iZ"
    if(pauli1 == "Z" and pauli2 == "Y"):
        return "-iX"
    if(pauli1 == "X" and pauli2 == "Z"):
        return "-iY"
    
    if(pauli1 == "I"):
        return pauli2
    if(pauli2 == "I"):
        return pauli1
    
    raise RuntimeError(f"Invlaid single paulis {pauli1}, {pauli2}")        

def multiply(pauli1, pauli2):

    pass

def pauli_product(pauli1, pauli2) -> bool:
    pass

def get_matrix(pauli_string: str):
    # TODO check if all characters are paulis

    matrix = GATE_MATRICES[pauli_string[0]]

    for pauli in pauli_string[1:]:
        matrix = np.kron(matrix, GATE_MATRICES[pauli])
    
    return matrix

def get_pauli_from_matrix(matrix:np.array, length = 1):
    
    pauli_string = ""
    sign = 1

    for paulis in itertools.product(PAULIS, repeat=length):

        pauli_matrix = get_matrix_from_pauli(paulis)

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
    
    return pauli_string, sign

def test():
    #print("X", get_pauli_from_matrix(GATE_MATRICES["X"]))
    #print("-X", get_pauli_from_matrix(-GATE_MATRICES["X"]))

    #print("XX", get_pauli_from_matrix(np.kron(GATE_MATRICES["X"], GATE_MATRICES["X"]), 2))
    #print("-XX", get_pauli_from_matrix(-np.kron(GATE_MATRICES["X"], GATE_MATRICES["X"]), 2))

    #print('-X',split_phase("-X"))
    #print('-X-Y-X-iZ-iX-Z-iX', split_phase('-X-Y-X-iZ-iX-Z-iX'))

    print(commute("X", "Y"))
    print(commute("XXYYX", "XXXXX"))

if __name__ == "__main__":
    test()