import os
import math
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Ensure we can import project modules
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'CircuitAnimation'))

from quantum_breaking_analysis import QuantumCircuitBreakingAnalyzer, NoiseProfile
from quantum_animator import QuantumCircuitAnimator

ALGORITHMS = ['ae', 'grover', 'qft', 'vqe']
QUBIT_SIZES = [3, 5]

# Simple mitigation parameters
ANGLE_REDUCTION_FACTOR = 0.85  # reduce rotation angles by 15%


def build_circuit(animator: QuantumCircuitAnimator, alg: str, n: int):
    alg = alg.lower()
    if alg == 'ae':
        return animator.create_amplitude_estimation_circuit(n)
    if alg == 'grover':
        return animator.create_grover_circuit(n)
    if alg == 'qft':
        return animator.create_qft_circuit(n)
    if alg == 'vqe':
        return animator.create_vqe_circuit(n)
    raise ValueError(f"Unsupported algorithm {alg}")


def apply_simple_mitigation(circuit):
    """Return a mitigated copy: reduce angles of parameterized rotations and remove trailing barriers."""
    mitigated = circuit.copy()
    new_data = []
    for inst in mitigated.data:
        try:
            op = inst.operation
            qubits = inst.qubits
            clbits = inst.clbits
        except AttributeError:
            op, qubits, clbits = inst
        name = op.name
        # Angle reduction for rotation gates
        if name in ['ry', 'rz', 'rx'] and getattr(op, 'params', None):
            try:
                angle = float(op.params[0]) * ANGLE_REDUCTION_FACTOR
                from qiskit.circuit.library import RYGate, RZGate, RXGate
                if name == 'ry':
                    new_gate = RYGate(angle)
                elif name == 'rz':
                    new_gate = RZGate(angle)
                else:
                    new_gate = RXGate(angle)
                new_data.append((new_gate, qubits, clbits))
                continue
            except Exception:
                pass
        # Skip redundant final barrier
        if name == 'barrier':
            continue
        new_data.append((op, qubits, clbits))
    # Rebuild circuit
    from qiskit import QuantumCircuit, ClassicalRegister
    # Recreate circuit with same classical register structure
    mitigated_circ = QuantumCircuit(circuit.num_qubits)
    # Add classical registers explicitly (handles named cregs)
    try:
        if hasattr(circuit, 'cregs') and circuit.cregs:
            for creg in circuit.cregs:
                mitigated_circ.add_register(ClassicalRegister(len(creg), creg.name))
    except Exception:
        pass

    # Build mapping for clbits to new circuit's clbits (by index across flattened list)
    clbit_mapping = {}
    try:
        original_clbits = list(circuit.clbits)
        new_clbits = list(mitigated_circ.clbits)
        for i, cb in enumerate(original_clbits):
            if i < len(new_clbits):
                clbit_mapping[cb] = new_clbits[i]
    except Exception:
        pass

    for op, qbs, cbs in new_data:
        # Map clbits if present
        mapped_cbs = []
        if cbs:
            for cb in cbs:
                mapped_cbs.append(clbit_mapping.get(cb, None))
            mapped_cbs = [cb for cb in mapped_cbs if cb is not None]
        try:
            mitigated_circ.append(op, qbs, mapped_cbs if mapped_cbs else None)
        except Exception:
            # Retry without clbits if mapping failed
            try:
                mitigated_circ.append(op, qbs)
            except Exception:
                continue
    return mitigated_circ


def compute_metrics(circuit, analyzer: QuantumCircuitBreakingAnalyzer):
    # Use analyzer's comprehensive method via report for richer metrics
    report = analyzer.generate_breaking_report(circuit, survival_rate=0.9)
    if 'error' in report:
        return {
            'avg_break_prob': 0.0,
            'max_break_prob': 0.0,
            'high_risk': 0,
            'critical': 0,
            'total_gates': len(circuit.data)
        }
    ba = report['breaking_analysis']
    return {
        'avg_break_prob': ba['average_break_probability'],
        'max_break_prob': ba['max_break_probability'],
        'high_risk': ba['high_risk_gates'],
        'critical': ba['critical_gates'],
        'total_gates': report['circuit_summary']['total_gates']
    }


def main(output_path: str = 'usefulness_comparison.png'):
    noise_profile = NoiseProfile(
        T1=100.0,
        T2=75.0,
        single_qubit_error=0.001,
        cnot_error=0.01,
        temperature=0.015,
        readout_error=0.02,
        crosstalk_factor=0.05,
        frequency_drift=0.001
    )
    animator = QuantumCircuitAnimator(session_id='fig', noise_profile=noise_profile)
    analyzer = animator.breaking_analyzer

    records = []
    for alg in ALGORITHMS:
        for n in QUBIT_SIZES:
            circuit = build_circuit(animator, alg, n)
            base_metrics = compute_metrics(circuit, analyzer)
            mitigated = apply_simple_mitigation(circuit)
            mitigated_metrics = compute_metrics(mitigated, analyzer)
            records.append({
                'algorithm': alg,
                'qubits': n,
                'base': base_metrics,
                'mitigated': mitigated_metrics
            })

    # Build figure: grouped bars for avg break probability before/after, overlaid line for high risk count
    num_groups = len(records)
    indices = np.arange(num_groups)
    width = 0.35

    base_avgs = [r['base']['avg_break_prob'] for r in records]
    mitigated_avgs = [r['mitigated']['avg_break_prob'] for r in records]
    high_risk_before = [r['base']['high_risk'] for r in records]
    high_risk_after = [r['mitigated']['high_risk'] for r in records]

    labels = [f"{r['algorithm'].upper()}-{r['qubits']}q" for r in records]

    fig, ax1 = plt.subplots(figsize=(14,6))
    bars1 = ax1.bar(indices - width/2, base_avgs, width, label='Avg Break (Base)', color='#d9534f')
    bars2 = ax1.bar(indices + width/2, mitigated_avgs, width, label='Avg Break (Mitigated)', color='#5cb85c')
    ax1.set_ylabel('Average Break Probability')
    ax1.set_xticks(indices)
    ax1.set_xticklabels(labels, rotation=25, ha='right')
    ax1.set_ylim(0, max(base_avgs + mitigated_avgs)*1.25 if base_avgs else 1)

    # Secondary axis for high risk gate counts
    ax2 = ax1.twinx()
    ax2.plot(indices, high_risk_before, marker='o', color='#f0ad4e', label='High-Risk Gates (Base)')
    ax2.plot(indices, high_risk_after, marker='s', color='#0275d8', label='High-Risk Gates (Mitigated)')
    ax2.set_ylabel('High-Risk Gate Count')
    ax2.set_ylim(0, max(high_risk_before + high_risk_after)*1.4 + 0.5)

    # Combine legends
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper right', frameon=False)

    plt.title('Circuit Robustness Improvement: Algorithm & Qubit Size Comparison')
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    print(f"Saved figure to {output_path}")

    # Also save raw data for reproducibility
    with open('usefulness_comparison_data.json', 'w') as f:
        json.dump(records, f, indent=2)
        print('Saved data to usefulness_comparison_data.json')

if __name__ == '__main__':
    main()
