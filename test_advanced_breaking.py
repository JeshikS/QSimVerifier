#!/usr/bin/env python3
"""
Demonstration script for the Advanced Quantum Circuit Breaking Analysis

This script demonstrates the mathematical formulas and integration with the 
existing QSimVerifier platform.
"""

import sys
import os
sys.path.append('/home/jeshik_1/jeshik/QSimVerifier/CircuitAnimation')

from quantum_breaking_analysis import QuantumCircuitBreakingAnalyzer, NoiseProfile
from quantum_animator import QuantumCircuitAnimator
from qiskit import QuantumCircuit
import numpy as np
import asyncio
import json

def create_demo_circuits():
    """Create various quantum circuits for demonstration"""
    circuits = {}
    
    # 1. Simple Bell State Circuit
    bell_circuit = QuantumCircuit(2)
    bell_circuit.h(0)
    bell_circuit.cx(0, 1)
    circuits['bell_state'] = bell_circuit
    
    # 2. Grover's Algorithm (3 qubits)
    grover_circuit = QuantumCircuit(3)
    # Initialize superposition
    grover_circuit.h([0, 1, 2])
    # Oracle (mark |101⟩)
    grover_circuit.cz(0, 2)
    grover_circuit.cz(1, 2)
    # Diffusion operator
    grover_circuit.h([0, 1, 2])
    grover_circuit.x([0, 1, 2])
    grover_circuit.ccx(0, 1, 2)
    grover_circuit.x([0, 1, 2])
    grover_circuit.h([0, 1, 2])
    circuits['grover_3qubit'] = grover_circuit
    
    # 3. Parametric Circuit with Rotation Gates
    param_circuit = QuantumCircuit(3)
    param_circuit.h(0)
    param_circuit.ry(np.pi/3, 1)  # 60-degree rotation
    param_circuit.rz(np.pi/2, 2)  # 90-degree rotation
    param_circuit.cx(0, 1)
    param_circuit.cx(1, 2)
    param_circuit.rx(3*np.pi/4, 0)  # Large angle rotation
    circuits['parametric'] = param_circuit
    
    # 4. Deep Circuit (many gates)
    deep_circuit = QuantumCircuit(4)
    for i in range(10):  # 10 layers
        for q in range(4):
            deep_circuit.ry(np.pi/4 * (i+1), q)
        for q in range(3):
            deep_circuit.cx(q, q+1)
    circuits['deep_circuit'] = deep_circuit
    
    return circuits

def demonstrate_noise_profiles():
    """Demonstrate different noise profiles"""
    print("🔬 Quantum Device Noise Profiles")
    print("=" * 50)
    
    # IBM Quantum Device (typical)
    ibm_profile = NoiseProfile(
        T1=100.0,      # 100 μs
        T2=75.0,       # 75 μs
        single_qubit_error=0.001,  # 0.1%
        cnot_error=0.01,           # 1%
        temperature=0.015,         # 15 mK
        readout_error=0.02,        # 2%
        crosstalk_factor=0.05,     # 5%
        frequency_drift=0.001      # 0.1%
    )
    
    # High-quality superconducting device
    high_quality_profile = NoiseProfile(
        T1=200.0,      # 200 μs (better coherence)
        T2=150.0,      # 150 μs
        single_qubit_error=0.0005, # 0.05%
        cnot_error=0.005,          # 0.5%
        temperature=0.010,         # 10 mK (colder)
        readout_error=0.01,        # 1%
        crosstalk_factor=0.02,     # 2%
        frequency_drift=0.0005     # 0.05%
    )
    
    # NISQ-era device (noisier)
    nisq_profile = NoiseProfile(
        T1=50.0,       # 50 μs (shorter coherence)
        T2=30.0,       # 30 μs
        single_qubit_error=0.002,  # 0.2%
        cnot_error=0.02,           # 2%
        temperature=0.020,         # 20 mK
        readout_error=0.05,        # 5%
        crosstalk_factor=0.1,      # 10%
        frequency_drift=0.002      # 0.2%
    )
    
    profiles = {
        'IBM Quantum (Typical)': ibm_profile,
        'High-Quality Device': high_quality_profile,
        'NISQ-Era Device': nisq_profile
    }
    
    for name, profile in profiles.items():
        print(f"\n📊 {name}:")
        print(f"   T1: {profile.T1} μs, T2: {profile.T2} μs")
        print(f"   Single-qubit error: {profile.single_qubit_error*100:.2f}%")
        print(f"   CNOT error: {profile.cnot_error*100:.1f}%")
        print(f"   Temperature: {profile.temperature*1000:.0f} mK")
        print(f"   Crosstalk: {profile.crosstalk_factor*100:.0f}%")
    
    return profiles

async def analyze_circuit_comprehensive(circuit_name, circuit, noise_profile):
    """Perform comprehensive breaking analysis on a circuit"""
    print(f"\n🧮 Comprehensive Analysis: {circuit_name}")
    print("-" * 40)
    print(f"Circuit: {circuit.num_qubits} qubits, {len(circuit.data)} gates, depth {circuit.depth()}")
    
    # Create analyzer
    analyzer = QuantumCircuitBreakingAnalyzer(noise_profile)
    
    # Generate breaking report
    report = analyzer.generate_breaking_report(circuit, survival_rate=0.9)
    
    if 'error' in report:
        print(f"❌ Analysis failed: {report['error']}")
        return
    
    # Display summary
    summary = report['breaking_analysis']
    print(f"📊 Breaking Analysis Summary:")
    print(f"   Total gates analyzed: {summary['total_breaking_points']}")
    print(f"   Critical risk gates: {summary['critical_gates']}")
    print(f"   High risk gates: {summary['high_risk_gates']}")
    print(f"   Medium risk gates: {summary['medium_risk_gates']}")
    print(f"   Average break probability: {summary['average_break_probability']:.4f}")
    print(f"   Maximum break probability: {summary['max_break_probability']:.4f}")
    
    # Display top risk gates
    print(f"\n🎯 Top 3 Risk Gates:")
    for i, gate in enumerate(report['top_risk_gates'][:3]):
        print(f"   {i+1}. Gate {gate['gate_index']+1} ({gate['gate_name']}): "
              f"{gate['break_probability']:.4f} ({gate['severity']})")
        if 'decoherence_factor' in gate:
            print(f"      Decoherence: {gate['decoherence_factor']:.3f}, "
                  f"Crosstalk: {gate['crosstalk_factor']:.3f}")
        if gate.get('mitigation_suggestions'):
            print(f"      Suggestion: {gate['mitigation_suggestions'][0]}")
    
    # Display execution strategy
    print(f"\n💡 Recommended Strategy:")
    print(f"   {report['device_recommendations']['execution_strategy']}")
    
    # Display mathematical model
    print(f"\n🧮 Mathematical Model:")
    print(f"   Formula: {report['mathematical_model']['formula']}")
    
    return report

async def demonstrate_integration():
    """Demonstrate integration with quantum animator"""
    print(f"\n🎬 Integration with Quantum Animator")
    print("=" * 50)
    
    # Create a sample circuit
    circuit = QuantumCircuit(3)
    circuit.h(0)
    circuit.ry(np.pi/3, 1)
    circuit.cx(0, 1)
    circuit.rz(np.pi/4, 2)
    circuit.cx(1, 2)
    circuit.ccx(0, 1, 2)
    
    # Create animator with advanced breaking analysis
    noise_profile = NoiseProfile(T1=80.0, T2=60.0, cnot_error=0.015)
    animator = QuantumCircuitAnimator(session_id="demo", noise_profile=noise_profile)
    
    print(f"Created circuit: {circuit.num_qubits} qubits, {len(circuit.data)} gates")
    print(f"Noise profile: T1={noise_profile.T1}μs, T2={noise_profile.T2}μs")
    
    # Generate advanced breaking animation
    try:
        animation_path, breaking_report = await animator.animate_advanced_circuit_breaking(
            circuit, survival_rate=0.85, filename="demo_circuit"
        )
        
        if animation_path and breaking_report:
            print(f"✅ Advanced breaking animation generated!")
            print(f"   Animation: {animation_path}")
            print(f"   Critical gates: {breaking_report['breaking_analysis']['critical_gates']}")
            print(f"   Max break probability: {breaking_report['breaking_analysis']['max_break_probability']}")
            
            # Save demo report
            with open('demo_breaking_report.json', 'w') as f:
                json.dump(breaking_report, f, indent=2)
            print(f"   Report saved: demo_breaking_report.json")
        else:
            print(f"❌ Animation generation failed")
            
    except Exception as e:
        print(f"❌ Error during integration demo: {e}")

def demonstrate_mathematical_formulas():
    """Demonstrate the mathematical formulas used"""
    print(f"\n🧮 Mathematical Breaking Analysis Formulas")
    print("=" * 60)
    
    print("📐 Core Breaking Probability Formula:")
    print("   P_break = 1 - P_survival")
    print("   P_survival = P_coherence × P_fidelity × P_crosstalk × P_environment × P_accumulation × P_parametric")
    print()
    
    print("🔬 Component Formulas:")
    print("   1. Decoherence: P_coherence = exp(-t_gate/T_φ)")
    print("      where T_φ = (1/T1 + 1/T2)^(-1)")
    print()
    print("   2. Gate Fidelity: P_fidelity = (1 - ε_gate)")
    print("      ε_gate depends on gate type and device characteristics")
    print()
    print("   3. Crosstalk: P_crosstalk = (1 - α_crosstalk × N_neighbors)")
    print("      α_crosstalk is device-dependent, N_neighbors is topology-dependent")
    print()
    print("   4. Environment: P_environment = exp(-β × T_env × t_accumulated)")
    print("      β depends on temperature and frequency drift")
    print()
    print("   5. Accumulation: P_accumulation = exp(-ε_acc × depth_factor)")
    print("      ε_acc increases with circuit depth and qubit usage")
    print()
    print("   6. Parametric: P_parametric = exp(-|θ|/π × sensitivity_factor)")
    print("      For rotation gates, larger angles → higher sensitivity")
    print()
    
    print("⚙️  Device Parameters Used:")
    print("   • T1, T2: Qubit coherence times (typically 50-200 μs)")
    print("   • Gate errors: Single-qubit ~0.1%, CNOT ~1%")
    print("   • Temperature: Dilution refrigerator ~10-20 mK")
    print("   • Crosstalk: Neighbor interference ~2-10%")
    print("   • Frequency drift: Long-term stability ~0.1%")

async def main():
    """Main demonstration function"""
    print("🚀 Advanced Quantum Circuit Breaking Analysis Demonstration")
    print("=" * 70)
    print("This demonstrates the mathematical formulas and integration")
    print("with the existing QSimVerifier platform.")
    print()
    
    # 1. Demonstrate noise profiles
    noise_profiles = demonstrate_noise_profiles()
    
    # 2. Demonstrate mathematical formulas
    demonstrate_mathematical_formulas()
    
    # 3. Create and analyze demo circuits
    circuits = create_demo_circuits()
    
    # Analyze each circuit with different noise profiles
    for circuit_name, circuit in list(circuits.items())[:2]:  # First 2 circuits
        for profile_name, profile in list(noise_profiles.items())[:2]:  # First 2 profiles
            print(f"\n{'='*60}")
            print(f"🔍 Analysis: {circuit_name} on {profile_name}")
            await analyze_circuit_comprehensive(circuit_name, circuit, profile)
    
    # 4. Demonstrate integration
    await demonstrate_integration()
    
    print(f"\n✅ Demonstration Complete!")
    print("=" * 70)
    print("🧮 Mathematical Breaking Analysis Features:")
    print("   ✓ Physics-based decoherence modeling (T1/T2)")
    print("   ✓ Gate fidelity analysis")
    print("   ✓ Crosstalk and topology effects")
    print("   ✓ Environmental noise factors")
    print("   ✓ Error accumulation tracking")
    print("   ✓ Parametric gate sensitivity")
    print("   ✓ Device-specific recommendations")
    print("   ✓ Mitigation strategy suggestions")
    print()
    print("🔗 Integration Features:")
    print("   ✓ Web interface with custom noise profiles")
    print("   ✓ Advanced animation generation")
    print("   ✓ Comprehensive JSON reports")
    print("   ✓ Compatible with existing QSimVerifier workflow")
    print()
    print("🎯 Mathematical Formula Integration:")
    print("   ✓ Real quantum device physics")
    print("   ✓ NISQ-era noise modeling") 
    print("   ✓ Gate-specific error analysis")
    print("   ✓ Comprehensive breaking probability calculation")

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())