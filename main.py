import unittest

from circuit import Circuit
from simulator import MatrixSimulator

class TestMatrixSimulator(unittest.TestCase):

    def test_state_preperation(self):
        simulator = MatrixSimulator()
        circuit = Circuit(n_qubits=2)

        # Initial state preparation
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "ZI")
        self.assertEqual(stabs[1], "IZ")

        print("State preperation tests - passed")
    
    def test_hadamard_gate(self):
        simulator = MatrixSimulator()

        # Z -> X
        circuit = Circuit(n_qubits=1)
        circuit.h(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "X")

        # X -> Z
        circuit = Circuit(n_qubits=1)
        circuit.h(0)
        circuit.h(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "Z")

        # ZI, IZ -> XI, IX
        circuit = Circuit(n_qubits=2)
        circuit.h(0)
        circuit.h(1)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "XI")
        self.assertEqual(stabs[1], "IX")

        print("Hadamard gate tests - passed")

    def test_s_gate(self):
        simulator = MatrixSimulator()

        # X -> Y
        circuit = Circuit(n_qubits=1)
        circuit.h(0)
        circuit.s(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "Y")

        # Z -> Z 
        circuit = Circuit(n_qubits=1)
        circuit.s(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "Z")
        
        print("S gate tests - passed")

    def test_x_gate(self):
        simulator = MatrixSimulator()

        # X -> X
        circuit = Circuit(n_qubits=1)
        circuit.h(0)
        circuit.x(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "X")


        # Z -> -Z
        circuit = Circuit(n_qubits=1)
        circuit.x(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "-Z")

        print("X gate tests - passed")
    
    def test_y_gate(self):

        simulator = MatrixSimulator()

        # X -> -X
        circuit = Circuit(n_qubits=1)
        circuit.h(0)
        circuit.y(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "-X")

        # Z -> -Z
        circuit = Circuit(n_qubits=1)
        circuit.y(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "-Z")

        print("Y gate tests - passed")


    def test_z_gate(self):
        simulator = MatrixSimulator()

        # X -> -X
        circuit = Circuit(n_qubits=1)
        circuit.h(0)
        circuit.z(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "-X")

        # Z -> Z 
        circuit = Circuit(n_qubits=1)
        circuit.z(0)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "Z")

        print("Z gate tests - passed")
        

    def test_cnot_gate(self):
        simulator = MatrixSimulator()

        # ZI, IZ -> ZI, ZZ
        circuit = Circuit(n_qubits=2)
        circuit.cx(0, 1)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "ZI")
        self.assertEqual(stabs[1], "ZZ")        

        # XI, IX -> XX
        circuit = Circuit(n_qubits=2)
        circuit.h(0)
        circuit.h(1)
        circuit.cx(0, 1)
        stabs = simulator.execute(circuit).get_pauli_strings()
        self.assertEqual(stabs[0], "XX")
        self.assertEqual(stabs[1], "IX")

        print("CNOT tests - passed")


    def test_measurement(self):
        # Measuring Basis State |0>
        simulator = MatrixSimulator()
        circuit = Circuit(n_qubits=2)
        circuit.measure_all()

        stabs = simulator.execute(circuit).get_pauli_strings()
        
        self.assertEqual(stabs[0], "ZI")
        self.assertEqual(stabs[1], "IZ")

        # Measuring Basis State |1>
        simulator = MatrixSimulator()
        circuit = Circuit(n_qubits=2)

        circuit.x(0)
        circuit.x(1)
        
        circuit.measure_all()
        stabs = simulator.execute(circuit).get_pauli_strings()
        
        self.assertEqual(stabs[0], "-ZI")
        self.assertEqual(stabs[1], "-IZ")

        # Measuring superposition (|0> + |1>) / sqrt(2)
        simulator = MatrixSimulator()
        circuit = Circuit(n_qubits=2)

        circuit.h(0)
        circuit.h(1)
        
        circuit.measure_all()
        stabs = simulator.execute(circuit).get_pauli_strings()
        
        self.assertIn(stabs[0], ["ZI", "-ZI"])
        self.assertIn(stabs[1], ["IZ", "-IZ"])

        print("Measurement tests - passed")


if __name__ == '__main__':
    unittest.main()

