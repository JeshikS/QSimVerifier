# feature_extractor.py

import os
import re
import numpy as np
import pandas as pd

from core.circuit_parser import parse_qasm_file

def extract_advanced_features(qasm_path):
    parsed_data = parse_qasm_file(qasm_path)

    num_qubits = parsed_data['num_qubits']
    num_clbits = parsed_data['num_clbits']
    depth = parsed_data['depth']
    total_gates = parsed_data['total_gates']
    entangling_gates = parsed_data['entangling_gates']
    gate_counts = parsed_data['gate_counts']
    cregs = parsed_data['cregs']
    instructions = parsed_data['raw_instructions']

    # Basic gates
    gate_rz = gate_counts.get('rz', 0)
    gate_sx = gate_counts.get('sx', 0)
    gate_cx = gate_counts.get('cx', 0)
    gate_measure = gate_counts.get('measure', 0)
    gate_x = gate_counts.get('x', 0)
    gate_barrier = gate_counts.get('barrier', 0)

    # Advanced features
    has_parametric_rz = int(any(re.search(r'rz\(([^)]+)\)', line) for line in instructions))
    num_param_rz_angles = sum(1 for line in instructions if re.search(r'rz\(([^)]+)\)', line))
    uses_multiple_cregs = int(len(cregs) > 1)
    has_cx_rz_cx_pattern = int(any('cx' in instructions[i] and 'rz' in instructions[i+1] and 'cx' in instructions[i+2]
                                   for i in range(len(instructions)-2)))

    # Return feature vector
    return {
        'filename': os.path.basename(qasm_path),
        'num_qubits': num_qubits,
        'num_clbits': num_clbits,
        'depth': depth,
        'total_gates': total_gates,
        'entangling_gates': entangling_gates,
        'gate_rz': gate_rz,
        'gate_sx': gate_sx,
        'gate_cx': gate_cx,
        'gate_measure': gate_measure,
        'gate_x': gate_x,
        'gate_barrier': gate_barrier,
        'has_parametric_rz': has_parametric_rz,
        'num_param_rz_angles': num_param_rz_angles,
        'uses_multiple_cregs': uses_multiple_cregs,
        'has_cx_rz_cx_pattern': has_cx_rz_cx_pattern
    }

def extract_features_for_directory(qasm_dir):
    data = []
    for filename in os.listdir(qasm_dir):
        if filename.endswith('.qasm'):
            path = os.path.join(qasm_dir, filename)
            features = extract_advanced_features(path)
            data.append(features)
    return pd.DataFrame(data)

if __name__ == '__main__':
    qasm_folder = 'data/sample_qasm/'
    output_csv = 'data/processed_features.csv'

    df = extract_features_for_directory(qasm_folder)
    df.to_csv(output_csv, index=False)
    print(f"Extracted features saved to {output_csv}")