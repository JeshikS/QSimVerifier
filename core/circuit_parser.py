# circuit_parser.py

from qiskit import QuantumCircuit
import re

ENTANGLING_GATES = {"cx", "cz", "swap"}


def load_qasm_circuit(qasm_path: str) -> QuantumCircuit:
    """Load a QASM file, normalizing reg/c naming issues and adding missing creg if needed."""
    with open(qasm_path, 'r') as f:
        qasm_code = f.read()

    # Replace 'reg' with 'q' for Qiskit compatibility
    qasm_code = qasm_code.replace('qreg reg[', 'qreg q[').replace('reg[', 'q[')

    # Check if classical register is referenced (e.g., c[0])
    references_c = 'c[' in qasm_code

    # Check if creg is declared
    has_creg = any(line.startswith('creg ') for line in qasm_code.splitlines())

    # Inject a default creg if needed
    if references_c and not has_creg:
        qreg_line = next(line for line in qasm_code.splitlines() if line.startswith('qreg '))
        num_qubits = int(qreg_line.split('[')[1].split(']')[0])
        qasm_code = qasm_code.replace(qreg_line, f"{qreg_line}\ncreg c[{num_qubits}];")

    return QuantumCircuit.from_qasm_str(qasm_code)


def parse_qasm_file(qasm_path):
    """Parse QASM file and extract structural and gate-level details."""
    circuit = load_qasm_circuit(qasm_path)

    with open(qasm_path, 'r') as f:
        raw_lines = f.readlines()

    raw_instructions = [
        line.strip().split('//')[0].strip()  # Remove comments
        for line in raw_lines
        if line.strip() and not line.strip().startswith(('OPENQASM', 'include', 'qreg', 'creg'))
    ]

    gate_counts = {}
    cregs = set()

    for instruction in raw_instructions:
        tokens = instruction.split()
        if not tokens:
            continue
        op = tokens[0]
        gate_counts[op] = gate_counts.get(op, 0) + 1

        # Collect creg names if present
        match = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\[\d+\]', instruction)
        for m in match:
            if m != 'q':  # assume q is the only qreg name
                cregs.add(m)

    entangling_count = sum(gate_counts.get(g, 0) for g in ENTANGLING_GATES)

    return {
        'num_qubits': circuit.num_qubits,
        'num_clbits': circuit.num_clbits,
        'depth': circuit.depth(),
        'total_gates': sum(gate_counts.values()),
        'entangling_gates': entangling_count,
        'gate_counts': gate_counts,
        'cregs': cregs,
        'raw_instructions': raw_instructions
    }
