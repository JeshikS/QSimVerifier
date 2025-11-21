#!/usr/bin/env python3
"""
Test script for advanced quantum circuit breaking analysis with fresh session
"""

import sys
sys.path.append('/home/jeshik_1/jeshik/QSimVerifier/CircuitAnimation')

from quantum_animator import QuantumCircuitAnimator
from qiskit import QuantumCircuit
import asyncio
import uuid

def create_test_vqe_circuit():
    """Create a test VQE circuit for advanced breaking analysis"""
    circuit = QuantumCircuit(4)
    
    # Initial state preparation
    circuit.h(0)
    circuit.h(1)
    
    # Entangling layer
    circuit.cx(0, 1)
    circuit.cx(1, 2)
    circuit.cx(2, 3)
    
    # Rotation layer (parameterized gates)
    circuit.ry(0.5, 0)
    circuit.ry(0.8, 1)
    circuit.ry(1.2, 2)
    circuit.ry(0.3, 3)
    
    # More entangling
    circuit.cx(0, 2)
    circuit.cx(1, 3)
    
    # Final rotation layer
    circuit.rz(0.7, 0)
    circuit.rz(1.1, 1)
    circuit.rz(0.4, 2)
    circuit.rz(0.9, 3)
    
    return circuit

async def test_advanced_breaking_analysis():
    """Test advanced breaking analysis with QASM file generation"""
    print("🧮 Testing Advanced Breaking Analysis with QASM Generation")
    
    # Create test circuit
    circuit = create_test_vqe_circuit()
    print(f"   Circuit: {circuit.num_qubits} qubits, {len(circuit.data)} gates")
    
    # Create animator with fresh session
    fresh_session_id = str(uuid.uuid4())[:8]
    animator = QuantumCircuitAnimator()
    animator.session_id = fresh_session_id
    
    print(f"   Session ID: {fresh_session_id}")
    
    # Run advanced breaking analysis
    try:
        result = await animator.animate_advanced_circuit_breaking(
            circuit, 
            survival_rate=0.9, 
            filename="test_vqe_circuit"
        )
        
        if result and len(result) == 2:
            animation_path, breaking_report = result
            print(f"✅ Advanced breaking analysis completed!")
            print(f"   Animation: {animation_path}")
            print(f"   Critical gates: {breaking_report['breaking_analysis']['critical_gates']}")
            print(f"   Session: {fresh_session_id}")
            
            # Check if QASM files were generated
            import os
            qasm_dir = f"/home/jeshik_1/jeshik/QSimVerifier/CircuitAnimation/outputs/session_{fresh_session_id}/qasm"
            if os.path.exists(qasm_dir):
                files = os.listdir(qasm_dir)
                print(f"   QASM files generated: {len(files)}")
                for file in files:
                    print(f"     - {file}")
            else:
                print(f"   ❌ QASM directory not found: {qasm_dir}")
                
            # Test slideshow generation
            from enhanced_slideshow import generate_enhanced_qasm_slideshow
            
            slideshow_path = f"/home/jeshik_1/jeshik/QSimVerifier/CircuitAnimation/outputs/session_{fresh_session_id}/slideshow.html"
            try:
                session_dir = f"/home/jeshik_1/jeshik/QSimVerifier/CircuitAnimation/outputs/session_{fresh_session_id}"
                config = {'session_id': fresh_session_id}
                
                # Call with await since it's async
                await generate_enhanced_qasm_slideshow(breaking_report, session_dir, config)
                
                if os.path.exists(slideshow_path):
                    file_size = os.path.getsize(slideshow_path)
                    print(f"✅ Slideshow generated successfully!")
                    print(f"   Path: {slideshow_path}")
                    print(f"   Size: {file_size} bytes")
                else:
                    print(f"❌ Slideshow file not found: {slideshow_path}")
                    
            except Exception as e:
                print(f"❌ Slideshow generation failed: {e}")
                import traceback
                traceback.print_exc()
            
        else:
            print("❌ Advanced breaking analysis failed")
            
    except Exception as e:
        print(f"❌ Error in advanced breaking analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_advanced_breaking_analysis())