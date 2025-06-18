import os
import json
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity
from mutation_operators.hadamard_mutator import mutate_hadamard_random
from qiskit.qasm3 import dumps as qasm3_dumps
from tqdm import trange

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize modern AerSimulator for statevector simulation
sim = AerSimulator(method="statevector")

def simulate_statevector(circuit: QuantumCircuit) -> Statevector:
    circuit = transpile(circuit, sim)
    circuit.save_statevector()
    result = sim.run(circuit).result()
    return result.get_statevector()

def generate_dataset(num_samples=1000):
    dataset = []
    for i in trange(num_samples):
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

        mutated_qc, mutation_type = mutate_hadamard_random(qc.copy())
        sv_orig = simulate_statevector(qc)
        sv_mut = simulate_statevector(mutated_qc)
        fidelity = state_fidelity(sv_orig, sv_mut)

        dataset.append({
            "id": i,
            "original_qasm": qasm3_dumps(qc),
            "mutated_qasm": qasm3_dumps(mutated_qc),
            "mutation_type": mutation_type,
            "fidelity": round(float(fidelity), 6)
        })

    with open(os.path.join(DATA_DIR, "hadamard_mutations.json"), "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"[✓] Dataset generated: {DATA_DIR}/hadamard_mutations.json")

if __name__ == "__main__":
    generate_dataset()
