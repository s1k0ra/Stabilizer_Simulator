import numpy as np

H_MATRIX = 1 / np.sqrt(2) * np.array([[1, 1],
                                      [1, -1]])
S_MATRIX = np.array([[1, 0],
                     [0, 1j]])
X_MATRIX = np.array([[0, 1],
                     [1, 0]])
Y_MATRIX = np.array([[0, -1j],
                     [1j, 0]])
Z_MATRIX = np.array([[1, 0],
                     [0, -1]])
CX_MATRIX = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 0, 1],
                      [0, 0, 1, 0]])

GATE_MATRICES = {"H" : H_MATRIX,
                  "S" : S_MATRIX,
                  "X" : X_MATRIX,
                  "Y" : Y_MATRIX,
                  "Z" : Z_MATRIX,
                  "CX": CX_MATRIX}

GATE_SYMBOLS = {"H" : ["[H]"],
                  "S" : ["[S]"],
                  "X" : ["[X]"],
                  "Y" : ["[Y]"],
                  "Z" : ["[Z]"],
                  "CX": ["[o]", "[+]"]}
