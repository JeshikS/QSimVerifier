from qiskit import QuantumCircuit
import random

def mutate_hadamard_random(circuit: QuantumCircuit):
    mutated = QuantumCircuit(circuit.num_qubits)
    mutation_type = None

    for instr, qargs, cargs in circuit.data:
        if instr.name == "h" and mutation_type is None:
            if random.random() < 0.5:
                mutation_type = "remove_h"
                continue
            else:
                mutation_type = "replace_h_with_x"
                qubit_idx = circuit.find_bit(qargs[0]).index
                mutated.x(qubit_idx)
                continue
        mutated.append(instr, qargs, cargs)

    if mutation_type is None:
        for i, (instr, qargs, cargs) in enumerate(circuit.data):
            if instr.name == "h":
                mutated = QuantumCircuit(circuit.num_qubits)
                for j, (op, qargs2, cargs2) in enumerate(circuit.data):
                    if j == i:
                        qubit_idx = circuit.find_bit(qargs2[0]).index
                        mutated.x(qubit_idx)
                        mutation_type = "replace_h_with_x_fallback"
                    else:
                        mutated.append(op, qargs2, cargs2)
                break

    return mutated, mutation_type
