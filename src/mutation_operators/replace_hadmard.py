from qiskit import QuantumCircuit
from qiskit_aer.primitives import Sampler
from qiskit.visualization import plot_histogram

# Build the Bell circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Use Sampler primitive (new style)
sampler = Sampler()
job = sampler.run(qc)
result = job.result()

# Extract and display probabilities
prob_dict = result.quasi_dists[0]
print("Result:", prob_dict)
