"""
Advanced Quantum Circuit Breaking Analysis Module

This module implements comprehensive mathematical formulas to determine what causes 
breaking of quantum circuits in real implementations, incorporating:
- Decoherence effects
- Gate fidelity
- NISQ device noise models
- Environmental factors
- Gate interaction effects
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional
from qiskit import QuantumCircuit
from qiskit.circuit.library import *
import pandas as pd
from dataclasses import dataclass


@dataclass
class NoiseProfile:
    """
    Noise characteristics for quantum devices based on real-world measurements.
    
    Default values represent typical IBM Quantum superconducting devices (2023-2025).
    These parameters are derived from published benchmarking data and device specifications.
    """
    # Decoherence times (microseconds) - based on IBM Quantum Network averages
    T1: float = 100.0         # Energy relaxation time (IBM avg: 80-150μs, Google: 60-120μs)
    T2: float = 75.0          # Phase coherence time (typically 0.5-0.8 × T1)
    
    # Gate error rates - from randomized benchmarking measurements  
    single_qubit_error: float = 0.001   # 0.1% (IBM: 0.05-0.2%, Google: 0.1-0.3%)
    cnot_error: float = 0.01           # 1.0% (IBM: 0.8-2%, Google: 0.4-1.5%)
    
    # Environmental factors
    temperature: float = 0.015         # 15 mK (dilution refrigerator base temp: 10-20mK)
    readout_error: float = 0.02        # 2% (measurement fidelity: 95-99%)
    
    # Device-specific noise sources
    crosstalk_factor: float = 0.05     # 5% neighbor interference (architecture dependent: 2-10%)
    frequency_drift: float = 0.001     # 0.1% long-term frequency stability


class QuantumCircuitBreakingAnalyzer:
    """
    Advanced analyzer for quantum circuit breaking points using comprehensive
    mathematical models of real quantum device limitations.
    """
    
    def __init__(self, noise_profile: Optional[NoiseProfile] = None):
        self.noise_profile = noise_profile or NoiseProfile()
        
        # Gate timing database (nanoseconds)
        self.gate_times = {
            'id': 0, 'x': 20, 'y': 20, 'z': 0, 'h': 20, 's': 0, 't': 0, 'sx': 20,
            'rx': 20, 'ry': 20, 'rz': 0, 'p': 0, 'u': 20, 'u1': 0, 'u2': 20, 'u3': 20,
            'cx': 320, 'cnot': 320, 'cz': 320, 'cy': 320, 'ch': 320, 'ccx': 640,
            'swap': 640, 'cswap': 960, 'iswap': 320, 'dcx': 640,
            'rzz': 320, 'rxx': 320, 'ryy': 320
        }
        
        # Quantum coherence factors
        self.coherence_sensitivity = {
            'single_qubit': 1.0,
            'two_qubit': 2.5,
            'three_qubit': 5.0,
            'parametric': 1.3
        }
    
    def calculate_comprehensive_breaking_probability(self, circuit: QuantumCircuit, 
                                                   survival_rate: float = 0.9) -> List[Dict]:
        """
        Calculate comprehensive breaking probability for each gate using advanced
        mathematical formulas that model real quantum device physics.
        
        Mathematical Model:
        P_break(gate_i) = 1 - P_survival(gate_i)
        
        Where P_survival incorporates:
        1. Decoherence: exp(-t_gate/T_φ)
        2. Gate fidelity: (1 - ε_gate)
        3. Crosstalk: (1 - α_crosstalk × N_neighbors)
        4. Environmental noise: exp(-β × T_env)
        5. Accumulated error: (1 - ε_acc)^depth
        """
        
        breaking_analysis = []
        accumulated_time = 0.0  # Track total circuit execution time
        qubit_states = {}  # Track each qubit's accumulated error
        
        # Initialize qubit error tracking
        for i in range(circuit.num_qubits):
            qubit_states[i] = {
                'accumulated_error': 0.0,
                'last_gate_time': 0.0,
                'gate_count': 0
            }
        
        for gate_idx, instruction in enumerate(circuit.data):
            # Handle different Qiskit versions
            if hasattr(instruction, 'operation'):
                gate = instruction.operation
                qubits = instruction.qubits
            else:
                gate, qubits, _ = instruction
            
            gate_name = gate.name
            gate_time = self.gate_times.get(gate_name, 50)  # Default 50ns
            
            # Get qubit indices
            qubit_indices = [circuit.qubits.index(q) for q in qubits]
            
            # Calculate multi-factor breaking probability
            break_prob = self._calculate_gate_breaking_probability(
                gate, gate_name, gate_time, qubit_indices, 
                accumulated_time, qubit_states, gate_idx, len(circuit.data)
            )
            
            # Update accumulated time and qubit states
            accumulated_time += gate_time / 1000.0  # Convert to microseconds
            for q_idx in qubit_indices:
                qubit_states[q_idx]['accumulated_error'] += break_prob * 0.1
                qubit_states[q_idx]['last_gate_time'] = accumulated_time
                qubit_states[q_idx]['gate_count'] += 1
            
            # Classify severity
            severity = self._classify_breaking_severity(break_prob)
            
            # Create comprehensive gate analysis
            gate_analysis = {
                'gate_index': gate_idx,
                'gate_name': gate_name,
                'qubits': qubit_indices,
                'break_probability': round(break_prob, 6),
                'severity': severity,
                'gate_time_ns': gate_time,
                'accumulated_time_us': round(accumulated_time, 3),
                'decoherence_factor': self._calculate_decoherence_factor(gate_time, len(qubit_indices)),
                'crosstalk_factor': self._calculate_crosstalk_factor(qubit_indices, circuit.num_qubits),
                'fidelity_loss': self._calculate_fidelity_loss(gate_name, gate),
                'environmental_noise': self._calculate_environmental_noise(accumulated_time),
                'quantum_volume_impact': self._calculate_quantum_volume_impact(gate_idx, len(circuit.data)),
                'mitigation_suggestions': self._generate_mitigation_suggestions(gate_name, break_prob)
            }
            
            # Add parameter-specific analysis for parametric gates
            if hasattr(gate, 'params') and gate.params:
                param_analysis = self._analyze_parametric_gate(gate, gate_name)
                gate_analysis.update(param_analysis)
            
            # Add topological analysis for multi-qubit gates
            if len(qubit_indices) > 1:
                topo_analysis = self._analyze_gate_topology(qubit_indices, circuit.num_qubits)
                gate_analysis.update(topo_analysis)
            
            breaking_analysis.append(gate_analysis)
        
        # Sort by breaking probability (highest risk first)
        breaking_analysis.sort(key=lambda x: x['break_probability'], reverse=True)
        
        return breaking_analysis
    
    def _calculate_gate_breaking_probability(self, gate, gate_name: str, gate_time: float,
                                           qubit_indices: List[int], accumulated_time: float,
                                           qubit_states: Dict, gate_idx: int, total_gates: int) -> float:
        """
        Core mathematical formula for gate breaking probability.
        
        Formula: P_break = 1 - P_coherence × P_fidelity × P_crosstalk × P_environment × P_accumulation
        """
        
        # 1. Decoherence probability (exponential decay)
        P_coherence = self._calculate_decoherence_survival(gate_time, len(qubit_indices))
        
        # 2. Gate fidelity (intrinsic gate errors)
        P_fidelity = self._calculate_gate_fidelity(gate_name, gate)
        
        # 3. Crosstalk effects (neighboring qubit interference)
        P_crosstalk = self._calculate_crosstalk_survival(qubit_indices, len(qubit_indices))
        
        # 4. Environmental noise (temperature, electromagnetic interference)
        P_environment = self._calculate_environment_survival(accumulated_time)
        
        # 5. Error accumulation (depth-dependent degradation)
        P_accumulation = self._calculate_accumulation_survival(gate_idx, total_gates, qubit_states, qubit_indices)
        
        # 6. Parametric gate sensitivity (for rotation gates)
        P_parametric = self._calculate_parametric_survival(gate) if hasattr(gate, 'params') else 1.0
        
        # Combined survival probability
        P_survival = P_coherence * P_fidelity * P_crosstalk * P_environment * P_accumulation * P_parametric
        
        # Breaking probability is complement of survival
        P_break = 1.0 - P_survival
        
        # Ensure probability bounds [0, 1]
        return max(0.0, min(1.0, P_break))
    
    def _calculate_decoherence_survival(self, gate_time: float, num_qubits: int) -> float:
        """
        Decoherence survival probability using T1 and T2 times.
        
        Formula: P_coherence = exp(-t_gate/T_φ) where T_φ = (1/T1 + 1/T2)^(-1)
        """
        gate_time_us = gate_time / 1000.0  # Convert ns to μs
        
        # Effective decoherence time (Ramsey dephasing time)
        T_phi = 1.0 / (1.0/self.noise_profile.T1 + 1.0/self.noise_profile.T2)
        
        # Multi-qubit gates experience amplified decoherence
        effective_T_phi = T_phi / self.coherence_sensitivity.get(
            'two_qubit' if num_qubits == 2 else 'three_qubit' if num_qubits >= 3 else 'single_qubit', 1.0
        )
        
        return math.exp(-gate_time_us / effective_T_phi)
    
    def _calculate_gate_fidelity(self, gate_name: str, gate) -> float:
        """
        Gate fidelity based on intrinsic gate errors.
        
        Formula: P_fidelity = 1 - ε_gate
        """
        if gate_name in ['cx', 'cnot', 'cz', 'cy', 'ch']:
            return 1.0 - self.noise_profile.cnot_error
        elif gate_name in ['ccx', 'cswap']:
            return 1.0 - (self.noise_profile.cnot_error * 2.5)  # Three-qubit gates
        elif gate_name in ['swap', 'iswap']:
            return 1.0 - (self.noise_profile.cnot_error * 1.5)  # Composite gates
        else:
            return 1.0 - self.noise_profile.single_qubit_error
    
    def _calculate_crosstalk_survival(self, qubit_indices: List[int], num_gate_qubits: int) -> float:
        """
        Crosstalk survival probability.
        
        Formula: P_crosstalk = 1 - α_crosstalk × N_active_neighbors
        """
        if len(qubit_indices) <= 1:
            return 1.0 - (self.noise_profile.crosstalk_factor * 0.5)  # Minimal crosstalk
        
        # Estimate neighboring qubits (assuming nearest-neighbor topology)
        neighbor_count = len(qubit_indices) * 2  # Approximate neighbors
        crosstalk_error = self.noise_profile.crosstalk_factor * neighbor_count * 0.1
        
        return max(0.5, 1.0 - crosstalk_error)  # Don't let crosstalk dominate completely
    
    def _calculate_environment_survival(self, accumulated_time: float) -> float:
        """
        Environmental noise survival probability.
        
        Formula: P_environment = exp(-β × T_env × t_acc)
        """
        # Temperature-dependent noise coefficient
        beta = self.noise_profile.temperature * 0.01
        
        # Frequency drift contribution
        drift_factor = self.noise_profile.frequency_drift * accumulated_time
        
        environmental_factor = beta * accumulated_time + drift_factor
        
        return math.exp(-environmental_factor)
    
    def _calculate_accumulation_survival(self, gate_idx: int, total_gates: int, 
                                       qubit_states: Dict, qubit_indices: List[int]) -> float:
        """
        Error accumulation survival probability.
        
        Formula: P_accumulation = (1 - ε_acc)^depth_effective
        """
        # Circuit depth factor
        depth_factor = gate_idx / total_gates
        
        # Per-qubit accumulated error
        max_qubit_error = max([qubit_states[q]['accumulated_error'] for q in qubit_indices], default=0.0)
        
        # Effective accumulated error rate
        accumulated_error_rate = 0.001 * depth_factor + max_qubit_error
        
        # Exponential error accumulation
        return math.exp(-accumulated_error_rate * gate_idx)
    
    def _calculate_parametric_survival(self, gate) -> float:
        """
        Parametric gate sensitivity.
        
        Formula: P_parametric = exp(-|θ|/π × sensitivity_factor)
        """
        if not (hasattr(gate, 'params') and gate.params):
            return 1.0
        
        # Get rotation angle
        angle = abs(float(gate.params[0]))
        
        # Normalize angle and apply sensitivity
        normalized_angle = angle / math.pi
        sensitivity = self.coherence_sensitivity.get('parametric', 1.3)
        
        parametric_error = normalized_angle * sensitivity * 0.1
        
        return max(0.1, 1.0 - parametric_error)
    
    def _calculate_decoherence_factor(self, gate_time: float, num_qubits: int) -> float:
        """Calculate pure decoherence contribution."""
        return 1.0 - self._calculate_decoherence_survival(gate_time, num_qubits)
    
    def _calculate_crosstalk_factor(self, qubit_indices: List[int], total_qubits: int) -> float:
        """Calculate crosstalk contribution."""
        return 1.0 - self._calculate_crosstalk_survival(qubit_indices, len(qubit_indices))
    
    def _calculate_fidelity_loss(self, gate_name: str, gate) -> float:
        """Calculate fidelity loss contribution."""
        return 1.0 - self._calculate_gate_fidelity(gate_name, gate)
    
    def _calculate_environmental_noise(self, accumulated_time: float) -> float:
        """Calculate environmental noise contribution."""
        return 1.0 - self._calculate_environment_survival(accumulated_time)
    
    def _calculate_quantum_volume_impact(self, gate_idx: int, total_gates: int) -> float:
        """
        Calculate impact on quantum volume.
        
        Quantum Volume degradation: QV ∝ exp(-error_rate × depth)
        """
        depth_ratio = gate_idx / total_gates
        return 1.0 - math.exp(-0.1 * depth_ratio)
    
    def _analyze_parametric_gate(self, gate, gate_name: str) -> Dict:
        """Analyze parametric gates (rotation gates) for angle-dependent errors."""
        if not (hasattr(gate, 'params') and gate.params):
            return {}
        
        angle = float(gate.params[0])
        angle_degrees = angle * 180.0 / math.pi
        
        # Calculate angle-dependent error contributions
        angle_sensitivity = abs(angle) / (2 * math.pi)  # Normalized [0, 1]
        calibration_error = angle_sensitivity * 0.02    # 2% max calibration error
        
        return {
            'params': [float(p) for p in gate.params],
            'angle_degrees': round(angle_degrees, 2),
            'angle_radians': round(angle, 4),
            'angle_sensitivity': round(angle_sensitivity, 4),
            'calibration_error': round(calibration_error, 4),
            'optimal_angle_range': self._get_optimal_angle_range(gate_name)
        }
    
    def _analyze_gate_topology(self, qubit_indices: List[int], total_qubits: int) -> Dict:
        """Analyze multi-qubit gate topology effects."""
        qubit_separation = max(qubit_indices) - min(qubit_indices) if len(qubit_indices) > 1 else 0
        
        return {
            'topology_complexity': len(qubit_indices),
            'qubit_separation': qubit_separation,
            'connectivity_cost': qubit_separation * 0.01,  # Cost increases with separation
            'parallelization_potential': self._calculate_parallelization_potential(qubit_indices, total_qubits)
        }
    
    def _get_optimal_angle_range(self, gate_name: str) -> Tuple[float, float]:
        """Get optimal angle range for rotation gates."""
        if gate_name in ['rx', 'ry']:
            return (-math.pi/2, math.pi/2)  # ±90 degrees is often most robust
        elif gate_name == 'rz':
            return (-math.pi/4, math.pi/4)  # ±45 degrees for Z rotations
        else:
            return (-math.pi, math.pi)      # Full range for general rotations
    
    def _calculate_parallelization_potential(self, qubit_indices: List[int], total_qubits: int) -> float:
        """Calculate how much this gate can be parallelized."""
        used_qubits = len(qubit_indices)
        available_qubits = total_qubits - used_qubits
        return available_qubits / total_qubits if total_qubits > 0 else 0.0
    
    def _classify_breaking_severity(self, break_prob: float) -> str:
        """Classify breaking probability into severity levels."""
        if break_prob >= 0.7:
            return 'critical'
        elif break_prob >= 0.5:
            return 'high'
        elif break_prob >= 0.3:
            return 'medium'
        elif break_prob >= 0.1:
            return 'low'
        else:
            return 'minimal'
    
    def _generate_mitigation_suggestions(self, gate_name: str, break_prob: float) -> List[str]:
        """Generate specific mitigation suggestions based on gate type and breaking probability."""
        suggestions = []
        
        if break_prob > 0.5:  # High risk gates
            if gate_name in ['cx', 'cnot']:
                suggestions.extend([
                    "Use error mitigation: Add dynamical decoupling sequences",
                    "Consider gate decomposition into native gates",
                    "Apply readout error mitigation",
                    "Use symmetry verification for error detection"
                ])
            elif gate_name in ['rx', 'ry', 'rz']:
                suggestions.extend([
                    "Optimize rotation angles to ±π/2 multiples when possible",
                    "Use composite pulse sequences for robustness",
                    "Apply randomized compiling to average gate errors"
                ])
            else:
                suggestions.append("Consider replacing with lower-fidelity equivalent gates")
        
        if break_prob > 0.3:  # Medium risk gates
            suggestions.extend([
                "Apply zero-noise extrapolation (ZNE)",
                "Use error correction codes if available",
                "Optimize gate scheduling to minimize crosstalk"
            ])
        
        if not suggestions:  # Low risk but still provide general advice
            suggestions.append("Gate within acceptable error bounds - monitor for drift")
        
        return suggestions
    
    def generate_breaking_report(self, circuit: QuantumCircuit, survival_rate: float = 0.9) -> Dict:
        """Generate comprehensive breaking analysis report."""
        analysis = self.calculate_comprehensive_breaking_probability(circuit, survival_rate)
        
        if not analysis:
            return {"error": "No breaking points identified"}
        
        # Calculate summary statistics
        break_probs = [item['break_probability'] for item in analysis]
        
        report = {
            'circuit_summary': {
                'total_gates': len(circuit.data),
                'num_qubits': circuit.num_qubits,
                'circuit_depth': circuit.depth(),
                'estimated_execution_time_us': sum([self.gate_times.get(gate.operation.name if hasattr(gate, 'operation') else gate[0].name, 50) for gate in circuit.data]) / 1000.0
            },
            'breaking_analysis': {
                'total_breaking_points': len(analysis),
                'critical_gates': len([x for x in analysis if x['severity'] == 'critical']),
                'high_risk_gates': len([x for x in analysis if x['severity'] == 'high']),
                'medium_risk_gates': len([x for x in analysis if x['severity'] == 'medium']),
                'average_break_probability': round(np.mean(break_probs), 4),
                'max_break_probability': round(max(break_probs), 4),
                'std_break_probability': round(np.std(break_probs), 4)
            },
            'top_risk_gates': analysis[:5],  # Top 5 highest risk gates
            'mitigation_priority': self._generate_circuit_mitigation_priority(analysis),
            'device_recommendations': self._generate_device_recommendations(analysis, circuit),
            'mathematical_model': {
                'formula': "P_break = 1 - P_coherence × P_fidelity × P_crosstalk × P_environment × P_accumulation × P_parametric",
                'components': {
                    'P_coherence': "exp(-t_gate/T_φ) - Decoherence effects",
                    'P_fidelity': "(1 - ε_gate) - Intrinsic gate errors",
                    'P_crosstalk': "(1 - α × N_neighbors) - Qubit crosstalk",
                    'P_environment': "exp(-β × T × t) - Environmental noise",
                    'P_accumulation': "(1 - ε_acc)^depth - Error accumulation",
                    'P_parametric': "exp(-|θ|/π × α) - Parameter sensitivity"
                }
            }
        }
        
        return report
    
    def _generate_circuit_mitigation_priority(self, analysis: List[Dict]) -> List[Dict]:
        """Generate prioritized mitigation strategies for the entire circuit."""
        priority_gates = [gate for gate in analysis if gate['break_probability'] > 0.3]
        
        priorities = []
        for gate in priority_gates[:10]:  # Top 10 priority gates
            priorities.append({
                'gate_index': gate['gate_index'],
                'gate_name': gate['gate_name'],
                'priority_score': gate['break_probability'],
                'primary_issue': self._identify_primary_issue(gate),
                'recommended_action': gate['mitigation_suggestions'][0] if gate['mitigation_suggestions'] else "Monitor gate performance"
            })
        
        return priorities
    
    def _identify_primary_issue(self, gate_analysis: Dict) -> str:
        """Identify the primary cause of gate breaking."""
        factors = {
            'decoherence': gate_analysis.get('decoherence_factor', 0),
            'crosstalk': gate_analysis.get('crosstalk_factor', 0),
            'fidelity': gate_analysis.get('fidelity_loss', 0),
            'environment': gate_analysis.get('environmental_noise', 0)
        }
        
        primary_factor = max(factors, key=factors.get)
        return primary_factor
    
    def _generate_device_recommendations(self, analysis: List[Dict], circuit: QuantumCircuit) -> Dict:
        """Generate device-specific recommendations."""
        avg_break_prob = np.mean([x['break_probability'] for x in analysis])
        
        recommendations = {
            'device_requirements': {
                'min_T1_required': f"{self.noise_profile.T1 * 1.5:.1f} μs",
                'min_T2_required': f"{self.noise_profile.T2 * 1.5:.1f} μs",
                'max_cnot_error': f"{self.noise_profile.cnot_error * 0.5:.4f}",
                'recommended_qubits': max(circuit.num_qubits + 2, 20)  # Add error correction overhead
            },
            'execution_strategy': self._recommend_execution_strategy(avg_break_prob),
            'error_mitigation': self._recommend_error_mitigation(analysis)
        }
        
        return recommendations
    
    def _recommend_execution_strategy(self, avg_break_prob: float) -> str:
        """Recommend execution strategy based on average breaking probability."""
        if avg_break_prob > 0.6:
            return "Circuit requires significant error correction - consider algorithmic modifications"
        elif avg_break_prob > 0.4:
            return "Apply aggressive error mitigation - use error correction codes"
        elif avg_break_prob > 0.2:
            return "Standard error mitigation sufficient - use ZNE and readout correction"
        else:
            return "Circuit suitable for NISQ execution with basic error mitigation"
    
    def _recommend_error_mitigation(self, analysis: List[Dict]) -> List[str]:
        """Recommend specific error mitigation techniques."""
        techniques = set()
        
        for gate in analysis:
            if gate['break_probability'] > 0.4:
                if gate['gate_name'] in ['cx', 'cnot']:
                    techniques.add("Dynamical decoupling on idle qubits")
                    techniques.add("Gate error mitigation via Pauli twirling")
                elif 'r' in gate['gate_name']:  # Rotation gates
                    techniques.add("Randomized compiling for rotation gates")
                    techniques.add("Composite pulse sequences")
        
        techniques.add("Zero-noise extrapolation (ZNE)")
        techniques.add("Readout error mitigation")
        
        return list(techniques)


def integrate_advanced_breaking_analysis():
    """
    Integration function to add advanced breaking analysis to existing system.
    """
    print("🧮 Advanced Quantum Circuit Breaking Analysis Integration")
    print("=" * 60)
    print("📐 Mathematical Model Components:")
    print("  • Decoherence: P_coherence = exp(-t_gate/T_φ)")
    print("  • Gate Fidelity: P_fidelity = (1 - ε_gate)")
    print("  • Crosstalk: P_crosstalk = (1 - α × N_neighbors)")
    print("  • Environment: P_environment = exp(-β × T × t)")
    print("  • Accumulation: P_accumulation = (1 - ε_acc)^depth")
    print("  • Parametric: P_parametric = exp(-|θ|/π × α)")
    print()
    print("🔬 Physics-Based Analysis:")
    print("  • T1/T2 decoherence modeling")
    print("  • NISQ device noise profiles")
    print("  • Gate-dependent error rates")
    print("  • Environmental factor integration")
    print("  • Crosstalk and topology effects")
    print()
    print("✅ Integration Complete - Advanced analysis ready!")
    
    return QuantumCircuitBreakingAnalyzer()


if __name__ == "__main__":
    # Demonstration of advanced breaking analysis
    analyzer = integrate_advanced_breaking_analysis()
    
    # Create a sample circuit for testing
    from qiskit import QuantumCircuit
    
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.ry(np.pi/3, 1)
    qc.cx(0, 1)
    qc.rz(np.pi/4, 2)
    qc.cx(1, 2)
    qc.ccx(0, 1, 2)
    
    print("\n🔍 Sample Analysis Results:")
    print("-" * 40)
    
    report = analyzer.generate_breaking_report(qc)
    
    print(f"Circuit: {report['circuit_summary']['total_gates']} gates, {report['circuit_summary']['num_qubits']} qubits")
    print(f"Average break probability: {report['breaking_analysis']['average_break_probability']}")
    print(f"Critical gates: {report['breaking_analysis']['critical_gates']}")
    print(f"Execution strategy: {report['device_recommendations']['execution_strategy']}")