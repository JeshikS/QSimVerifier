def get_gate_counts(circuit):
    """Returns a dict of gate counts used in the circuit."""
    gate_counts = {}
    for instr, _, _ in circuit.data:
        name = instr.name
        gate_counts[name] = gate_counts.get(name, 0) + 1
    return gate_counts

def compute_depth(circuit):
    """Compute the depth of a circuit."""
    return circuit.depth()

def count_entangling_gates(circuit):
    """Rough count of entangling gates (e.g., CX, CZ, etc.)."""
    entangling = ["cx", "cz", "swap"]
    return sum(1 for instr, _, _ in circuit.data if instr.name in entangling)
