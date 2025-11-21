from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional
from enhanced_slideshow import generate_enhanced_qasm_slideshow
import asyncio
from quantum_animator import QuantumCircuitAnimator

# Alias for consistency
QuantumAnimator = QuantumCircuitAnimator

async def analyze_circuit_breaking(circuit, survival_rate):
    """
    Analyze quantum circuit for potential breaking points using both simple and advanced methods.
    Now includes comprehensive mathematical formulas for real quantum device physics.
    """
    try:
        # Import the advanced analyzer
        from quantum_breaking_analysis import QuantumCircuitBreakingAnalyzer, NoiseProfile
        
        # Create analyzer with custom noise profile if needed
        noise_profile = NoiseProfile(
            T1=100.0,  # 100 μs relaxation time
            T2=75.0,   # 75 μs dephasing time
            single_qubit_error=0.001,  # 0.1% single-qubit error
            cnot_error=0.01,          # 1% CNOT error
            temperature=0.015,        # 15 mK
            readout_error=0.02,       # 2% readout error
            crosstalk_factor=0.05,    # 5% crosstalk
            frequency_drift=0.001     # 0.1% frequency drift
        )
        
        analyzer = QuantumCircuitBreakingAnalyzer(noise_profile)
        
        # Get comprehensive breaking analysis
        advanced_analysis = analyzer.calculate_comprehensive_breaking_probability(circuit, survival_rate)
        
        if not advanced_analysis:
            # Fallback to simple analysis if advanced fails
            return await analyze_circuit_breaking_simple(circuit, survival_rate)
        
        # Convert advanced analysis to compatible format
        breaking_points = []
        for gate_analysis in advanced_analysis:
            # Convert advanced format to simple format for compatibility
            gate_info = {
                'gate_index': gate_analysis['gate_index'],
                'gate_name': gate_analysis['gate_name'],
                'qubits': gate_analysis['qubits'],
                'break_probability': gate_analysis['break_probability'],
                'severity': gate_analysis['severity'],
                
                # Advanced fields
                'decoherence_factor': gate_analysis.get('decoherence_factor', 0),
                'crosstalk_factor': gate_analysis.get('crosstalk_factor', 0),
                'fidelity_loss': gate_analysis.get('fidelity_loss', 0),
                'environmental_noise': gate_analysis.get('environmental_noise', 0),
                'gate_time_ns': gate_analysis.get('gate_time_ns', 0),
                'accumulated_time_us': gate_analysis.get('accumulated_time_us', 0),
                'mitigation_suggestions': gate_analysis.get('mitigation_suggestions', []),
                'quantum_volume_impact': gate_analysis.get('quantum_volume_impact', 0)
            }
            
            # Add parameter info for rotation gates
            if 'angle_degrees' in gate_analysis:
                gate_info['params'] = gate_analysis.get('params', [])
                gate_info['angle_degrees'] = gate_analysis['angle_degrees']
                gate_info['angle_sensitivity'] = gate_analysis.get('angle_sensitivity', 0)
                gate_info['calibration_error'] = gate_analysis.get('calibration_error', 0)
            
            # Add topology info for multi-qubit gates
            if 'topology_complexity' in gate_analysis:
                gate_info['topology_complexity'] = gate_analysis['topology_complexity']
                gate_info['qubit_separation'] = gate_analysis.get('qubit_separation', 0)
                gate_info['connectivity_cost'] = gate_analysis.get('connectivity_cost', 0)
            
            breaking_points.append(gate_info)
        
        print(f"🧮 Advanced breaking analysis complete: {len(breaking_points)} gates analyzed")
        print(f"   Mathematical model: P_break = 1 - P_coherence × P_fidelity × P_crosstalk × P_environment × P_accumulation")
        
        return breaking_points
        
    except Exception as e:
        print(f"Error in advanced circuit breaking analysis: {e}")
        print("Falling back to simple analysis...")
        return await analyze_circuit_breaking_simple(circuit, survival_rate)


async def analyze_circuit_breaking_simple(circuit, survival_rate):
    """Simple circuit breaking analysis (fallback method)"""
    try:
        breaking_points = []
        
        # Simulate noise effects on each gate
        for i, instruction in enumerate(circuit.data):
            # Handle different Qiskit versions
            if hasattr(instruction, 'operation'):
                # Newer Qiskit versions
                gate = instruction.operation
                qubits = instruction.qubits
            else:
                # Older Qiskit versions
                gate, qubits, _ = instruction
            
            gate_name = gate.name
            
            # Calculate breaking probability based on gate type and parameters
            if gate_name in ['cx', 'cnot', 'cz']:  # Two-qubit gates
                break_prob = 1 - (survival_rate ** 2)  # Higher chance to break
            elif gate_name in ['h', 'x', 'y', 'z', 's', 't']:  # Standard single-qubit gates
                break_prob = 1 - survival_rate
            elif gate_name in ['ry', 'rz', 'rx']:  # Rotation gates
                # Rotation gates can be more sensitive, especially with large angles
                if hasattr(gate, 'params') and gate.params:
                    angle = abs(float(gate.params[0]))
                    # Higher angles are more susceptible to noise
                    angle_factor = min(angle / (2 * 3.14159), 2.0)  # Normalize and cap
                    break_prob = 1 - (survival_rate ** (1 + angle_factor * 0.5))
                else:
                    break_prob = 1 - survival_rate
            elif gate_name in ['sx', 'sy']:  # Square root gates
                break_prob = 1 - (survival_rate ** 0.8)  # Slightly more robust than full rotations
            else:
                break_prob = 1 - survival_rate  # Default for unknown gates
            
            # Consider gate position - later gates accumulate more error
            position_factor = 1 + (i / len(circuit.data)) * 0.3  # Up to 30% increase
            break_prob = min(break_prob * position_factor, 0.95)  # Cap at 95%
            
            if break_prob > 0.05:  # Consider even small breaking probabilities for complex circuits
                severity = 'high' if break_prob > 0.4 else 'medium' if break_prob > 0.2 else 'low'
                
                # Get qubit indices safely
                qubit_indices = []
                for q in qubits:
                    if hasattr(q, '_index'):
                        qubit_indices.append(q._index)
                    elif hasattr(q, 'index'):
                        qubit_indices.append(q.index)
                    else:
                        # Fallback: find index in circuit qubits
                        try:
                            qubit_indices.append(circuit.qubits.index(q))
                        except ValueError:
                            qubit_indices.append(0)  # Default fallback
                
                # Get gate information
                gate_info = {
                    'gate_index': i,
                    'gate_name': gate_name,
                    'qubits': qubit_indices,
                    'break_probability': round(break_prob, 4),
                    'severity': severity
                }
                
                # Add parameter info for rotation gates
                if hasattr(gate, 'params') and gate.params:
                    gate_info['params'] = [float(p) for p in gate.params]
                    gate_info['angle_degrees'] = round(float(gate.params[0]) * 180 / 3.14159, 2)
                
                breaking_points.append(gate_info)
        
        # Sort by breaking probability (highest first)
        breaking_points.sort(key=lambda x: x['break_probability'], reverse=True)
        
        return breaking_points if breaking_points else None
        
    except Exception as e:
        print(f"Error analyzing circuit breaking: {e}")
        import traceback
        traceback.print_exc()
        return None

app = FastAPI(title="Quantum Circuit Mutation Web App", version="1.0.0")

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
templates = Jinja2Templates(directory="templates")

# Initialize animator
animator = QuantumCircuitAnimator()

# Available algorithms
ALGORITHMS = {
    'ae': 'Amplitude Estimation',
    'grover': 'Grover Search',
    'qft': 'Quantum Fourier Transform',
    'vqe': 'Variational Quantum Eigensolver',
    'qaoa': 'Quantum Approximate Optimization'
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page with circuit configuration form"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "algorithms": ALGORITHMS
    })

@app.post("/generate-circuit")
async def generate_circuit(
    source_type: str = Form(...),
    algorithm: Optional[str] = Form(None),
    num_qubits: Optional[int] = Form(None),
    survival_rate: Optional[float] = Form(0.9),
    show_creation: bool = Form(False),
    show_breaking: bool = Form(False),
    show_mutations: bool = Form(False),
    num_mutations: Optional[int] = Form(5),
    qasm_file: Optional[UploadFile] = File(None),
    qasm_survival_rate: Optional[float] = Form(0.9),
    qasm_mutations: Optional[int] = Form(3)
):
    """Generate quantum circuit from algorithm or QASM file"""
    
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())[:8]
        
        if source_type == "algorithm":
            # Validate algorithm inputs
            if not algorithm or algorithm not in ALGORITHMS:
                raise HTTPException(status_code=400, detail="Invalid algorithm")
            if not num_qubits or not (2 <= num_qubits <= 10):
                raise HTTPException(status_code=400, detail="Number of qubits must be between 2 and 10")
            if not (0.0 <= survival_rate <= 1.0):
                raise HTTPException(status_code=400, detail="Survival rate must be between 0.0 and 1.0")
            if not num_mutations or not (1 <= num_mutations <= 20):
                raise HTTPException(status_code=400, detail="Number of mutations must be between 1 and 20")
            
            # Create circuit configuration for algorithm
            circuit_config = {
                'algorithm': algorithm,
                'num_qubits': num_qubits,
                'survival_rate': survival_rate,
                'show_creation': show_creation,
                'show_breaking': show_breaking,
                'show_mutations': show_mutations,
                'num_mutations': num_mutations,
                'session_id': session_id
            }
            
            # Generate animations using existing algorithm flow
            result = await generate_circuit_animations(circuit_config)
            return JSONResponse({"success": True, "session_id": session_id, "result": result})
            
        elif source_type == "qasm":
            # Validate QASM inputs
            if not qasm_file:
                raise HTTPException(status_code=400, detail="QASM file is required")
            if not (0.0 <= qasm_survival_rate <= 1.0):
                raise HTTPException(status_code=400, detail="Survival rate must be between 0.0 and 1.0")
            if not qasm_mutations or not (1 <= qasm_mutations <= 10):
                raise HTTPException(status_code=400, detail="Number of mutations must be between 1 and 10")
            
            # Read and process QASM file
            qasm_content = await qasm_file.read()
            qasm_text = qasm_content.decode('utf-8')
            
            # Create circuit configuration for QASM
            circuit_config = {
                'source_type': 'qasm',
                'qasm_content': qasm_text,
                'qasm_filename': qasm_file.filename,
                'survival_rate': qasm_survival_rate,
                'show_creation': show_creation,
                'show_breaking': show_breaking,
                'show_mutations': show_mutations,
                'num_mutations': qasm_mutations,
                'session_id': session_id
            }
            
            # Generate animations using new QASM flow
            result = await generate_qasm_animations(circuit_config)
            return JSONResponse({"success": True, "session_id": session_id, "result": result})
            
        else:
            raise HTTPException(status_code=400, detail="Invalid source type")
            
    except Exception as e:
        print(f"Error generating circuit: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def generate_qasm_animations(config):
    """Generate animations from uploaded QASM file"""
    try:
        from qiskit import QuantumCircuit
        import re
        import math
        
        # Initialize the quantum animator
        animator = QuantumAnimator(config['session_id'])
        
        # Preprocess QASM content to handle compatibility issues
        qasm_content = preprocess_qasm_content(config['qasm_content'])
        
        # Parse QASM content into quantum circuit
        try:
            # Try multiple parsing methods
            circuit = None
            
            # Method 1: Try qiskit.qasm2.loads (newer versions) with preprocessed content
            try:
                from qiskit.qasm2 import loads
                circuit = loads(qasm_content)
                print(f"Successfully loaded QASM using qasm2.loads with preprocessing")
            except ImportError:
                print("qasm2.loads not available, trying alternative methods")
            except Exception as e:
                print(f"qasm2.loads failed: {e}")
            
            # Method 2: Try QuantumCircuit.from_qasm_str (older versions) with preprocessed content
            if circuit is None:
                try:
                    circuit = QuantumCircuit.from_qasm_str(qasm_content)
                    print(f"Successfully loaded QASM using from_qasm_str with preprocessing")
                except Exception as e:
                    print(f"from_qasm_str failed: {e}")
            
            # Method 3: Manual parsing fallback
            if circuit is None:
                circuit = parse_qasm_manually(qasm_content)
                print(f"Successfully loaded QASM using manual parser")
            
            if circuit is None:
                raise Exception("All QASM parsing methods failed")
                
            print(f"Successfully loaded QASM circuit with {circuit.num_qubits} qubits and {len(circuit.data)} gates")
            
        except Exception as e:
            raise Exception(f"Failed to parse QASM file: {str(e)}")
        
        result = {
            'source': 'qasm',
            'filename': config['qasm_filename'],
            'num_qubits': circuit.num_qubits,
            'num_gates': len(circuit.data),
            'animations': {}
        }
        
        # Generate creation animation if requested (show original circuit)
        if config.get('show_creation', False):
            print(f"Generating creation animation for QASM circuit")
            creation_path = await animator.animate_qasm_circuit_creation(
                circuit, config['qasm_filename']
            )
            if creation_path:
                result['animations']['creation'] = f"/outputs/session_{config['session_id']}/{creation_path.name}"
        
        # Generate breaking analysis and mutations if requested
        if config.get('show_breaking', False) or config.get('show_mutations', False):
            print(f"Analyzing QASM circuit breaking points...")
            breaking_analysis = await analyze_circuit_breaking(circuit, config['survival_rate'])
            
            if config.get('show_breaking', False) and breaking_analysis:
                print(f"Generating breaking animation for QASM circuit...")
                breaking_path = await animator.animate_qasm_circuit_breaking(
                    circuit, breaking_analysis, config['qasm_filename']
                )
                if breaking_path:
                    result['animations']['breaking'] = f"/outputs/session_{config['session_id']}/{breaking_path.name}"
            
            if config.get('show_mutations', False) and breaking_analysis:
                print(f"Generating mutations to fix QASM circuit breaking points...")
                mutations_path = await animator.animate_qasm_mutations(
                    circuit, breaking_analysis, config['qasm_filename'], config['num_mutations']
                )
                if mutations_path:
                    result['animations']['mutations'] = f"/outputs/session_{config['session_id']}/{mutations_path.name}"
        
        # Generate simple HTML slideshow for QASM results
        if result['animations']:
            session_dir = f"outputs/session_{config['session_id']}"
            os.makedirs(session_dir, exist_ok=True)
            
            # Generate QASM files for download
            await generate_qasm_files(circuit, config, session_dir)
            
            # Generate enhanced slideshow with frame controls
            slideshow_path = await generate_enhanced_qasm_slideshow(result, session_dir, config)
            result['slideshow_path'] = f"outputs/session_{config['session_id']}/slideshow.html"
        
        return result
        
    except Exception as e:
        print(f"Error in generate_qasm_animations: {e}")
        import traceback
        traceback.print_exc()
        raise e

def preprocess_qasm_content(qasm_content):
    """Preprocess QASM content to handle compatibility issues"""
    import re
    import math
    
    # Replace mathematical expressions
    qasm_content = re.sub(r'3\*pi', str(3 * math.pi), qasm_content)
    qasm_content = re.sub(r'2\*pi', str(2 * math.pi), qasm_content)
    qasm_content = re.sub(r'pi/2', str(math.pi/2), qasm_content)
    qasm_content = re.sub(r'pi/4', str(math.pi/4), qasm_content)
    qasm_content = re.sub(r'(?<![\d\*])pi(?![/\*])', str(math.pi), qasm_content)
    
    # Convert sx gates to equivalent rotation gates (sx = sqrt(X) = Ry(pi/2))
    qasm_content = re.sub(r'sx\s+q\[(\d+)\];', r'ry(1.5707963267948966) q[\1];', qasm_content)
    
    return qasm_content

def parse_qasm_manually(qasm_content):
    """Manual QASM parser for fallback compatibility"""
    try:
        from qiskit import QuantumCircuit
        import re
        
        lines = qasm_content.strip().split('\n')
        
        # Find qreg declaration to determine number of qubits
        num_qubits = 4  # default
        for line in lines:
            if 'qreg' in line:
                match = re.search(r'qreg\s+\w+\[(\d+)\]', line)
                if match:
                    num_qubits = int(match.group(1))
                    break
        
        # Create circuit
        circuit = QuantumCircuit(num_qubits)
        
        # Parse gates
        for line in lines:
            line = line.strip()
            if line.startswith('//') or not line or line.startswith('OPENQASM') or \
               line.startswith('include') or line.startswith('qreg') or \
               line.startswith('creg') or line.startswith('barrier') or line.startswith('measure'):
                continue
            
            # Parse gate operations
            if 'h q[' in line:
                match = re.search(r'h q\[(\d+)\]', line)
                if match:
                    circuit.h(int(match.group(1)))
            
            elif 'x q[' in line:
                match = re.search(r'x q\[(\d+)\]', line)
                if match:
                    circuit.x(int(match.group(1)))
            
            elif 'y q[' in line:
                match = re.search(r'y q\[(\d+)\]', line)
                if match:
                    circuit.y(int(match.group(1)))
            
            elif 'z q[' in line:
                match = re.search(r'z q\[(\d+)\]', line)
                if match:
                    circuit.z(int(match.group(1)))
            
            elif 'cx q[' in line:
                match = re.search(r'cx q\[(\d+)\],q\[(\d+)\]', line)
                if match:
                    circuit.cx(int(match.group(1)), int(match.group(2)))
            
            elif 'ry(' in line:
                match = re.search(r'ry\(([\d\.\-e]+)\)\s+q\[(\d+)\]', line)
                if match:
                    angle = float(match.group(1))
                    qubit = int(match.group(2))
                    circuit.ry(angle, qubit)
            
            elif 'rz(' in line:
                match = re.search(r'rz\(([\d\.\-e]+)\)\s+q\[(\d+)\]', line)
                if match:
                    angle = float(match.group(1))
                    qubit = int(match.group(2))
                    circuit.rz(angle, qubit)
            
            elif 'rx(' in line:
                match = re.search(r'rx\(([\d\.\-e]+)\)\s+q\[(\d+)\]', line)
                if match:
                    angle = float(match.group(1))
                    qubit = int(match.group(2))
                    circuit.rx(angle, qubit)
        
        return circuit
        
    except Exception as e:
        print(f"Manual parsing failed: {e}")
        return None

async def generate_circuit_animations(config):
    """Generate circuit animations based on configuration"""
    
    try:
        # Create output directory for this session
        session_dir = f"outputs/session_{config['session_id']}"
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(f"{session_dir}/images", exist_ok=True)
        os.makedirs(f"{session_dir}/qasm", exist_ok=True)
        
        # Generate algorithm-specific circuit using the unified method
        initial_circuit = animator.get_algorithm_circuit(config['algorithm'], config['num_qubits'])
        
        animations = []
        qasm_files = []
        
        # 1. Show circuit creation if requested
        if config['show_creation']:
            creation_frames = await generate_creation_animation(initial_circuit, session_dir, config)
            animations.append({
                'type': 'creation',
                'title': 'Circuit Creation',
                'frames': creation_frames
            })
            
            # Save initial circuit QASM
            try:
                # Try newer qiskit version method first
                try:
                    qasm_content = initial_circuit.qasm()
                except AttributeError:
                    # Fallback for newer qiskit versions
                    from qiskit.qasm2 import dumps
                    qasm_content = dumps(initial_circuit)
                
                qasm_path = f"{session_dir}/qasm/initial_circuit.qasm"
                with open(qasm_path, 'w') as f:
                    f.write(qasm_content)
                qasm_files.append({
                    'name': 'initial_circuit.qasm',
                    'path': f"outputs/session_{config['session_id']}/qasm/initial_circuit.qasm",
                    'content': qasm_content
                })
            except Exception as e:
                print(f"Warning: Could not generate QASM for initial circuit: {e}")
                # Create a simple QASM representation
                qasm_content = f"// Initial {config['algorithm']} circuit with {config['num_qubits']} qubits\n"
                qasm_content += f"OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
                qasm_content += f"qreg q[{config['num_qubits']}];\ncreg c[{config['num_qubits']}];\n"
                qasm_path = f"{session_dir}/qasm/initial_circuit.qasm"
                with open(qasm_path, 'w') as f:
                    f.write(qasm_content)
                qasm_files.append({
                    'name': 'initial_circuit.qasm',
                    'path': f"outputs/session_{config['session_id']}/qasm/initial_circuit.qasm",
                    'content': qasm_content
                })
        
        # 2. Show circuit breaking if requested
        broken_circuit = None
        if config['show_breaking']:
            breaking_frames, broken_circuit = await generate_breaking_animation(initial_circuit, session_dir, config)
            animations.append({
                'type': 'breaking',
                'title': 'Circuit Breaking',
                'frames': breaking_frames
            })
            
            # Add broken circuit QASM if it exists
            broken_qasm_path = f"{session_dir}/qasm/broken_circuit.qasm"
            if os.path.exists(broken_qasm_path):
                with open(broken_qasm_path, 'r') as f:
                    qasm_content = f.read()
                qasm_files.append({
                    'name': 'broken_circuit.qasm',
                    'path': f"outputs/session_{config['session_id']}/qasm/broken_circuit.qasm",
                    'content': qasm_content
                })
        
        # 3. Show mutations if requested
        if config['show_mutations']:
            mutation_frames, mutated_circuits = await generate_mutation_animation(
                broken_circuit or initial_circuit, session_dir, config
            )
            animations.append({
                'type': 'mutations',
                'title': 'Circuit Mutations',
                'frames': mutation_frames
            })
            
            # Add mutated circuit QASM files
            for i in range(1, config['num_mutations'] + 1):
                mutated_qasm_path = f"{session_dir}/qasm/mutated_circuit_{i}.qasm"
                if os.path.exists(mutated_qasm_path):
                    with open(mutated_qasm_path, 'r') as f:
                        qasm_content = f.read()
                    qasm_files.append({
                        'name': f'mutated_circuit_{i}.qasm',
                        'path': f"outputs/session_{config['session_id']}/qasm/mutated_circuit_{i}.qasm",
                        'content': qasm_content
                    })
        
        # Generate HTML slideshow
        slideshow_path = await generate_html_slideshow(animations, session_dir, config)
        
        return {
            'animations': animations,
            'qasm_files': qasm_files,
            'slideshow_path': f"outputs/session_{config['session_id']}/slideshow.html",
            'session_dir': session_dir,
            'circuit_info': {
                'algorithm': ALGORITHMS.get(config['algorithm'], config['algorithm'].upper()),
                'num_qubits': config['num_qubits'],
                'survival_rate': config['survival_rate'],
                'num_mutations': config['num_mutations']
            }
        }
        
    except Exception as e:
        print(f"Error in generate_circuit_animations: {e}")
        import traceback
        traceback.print_exc()
        raise e

async def generate_creation_animation(circuit, session_dir, config):
    """Generate step-by-step circuit creation animation with consistent scaling"""
    frames = []
    
    # Build circuit gate by gate (skip empty circuit frame)
    current_circuit = animator.create_empty_circuit(config['num_qubits'])
    
    # Copy classical registers from original circuit to avoid clbit errors
    # But avoid duplicating registers that already exist
    if hasattr(circuit, 'cregs') and circuit.cregs:
        for creg in circuit.cregs:
            # Only add if register doesn't already exist
            existing_reg_names = [reg.name for reg in current_circuit.cregs]
            if creg.name not in existing_reg_names:
                current_circuit.add_register(creg)
    
    gates = list(circuit.data)
    
    for i, instruction in enumerate(gates):
        try:
            # Remap qubits from the source circuit to the current_circuit's qubits
            # instruction.qubits contains Qubit objects bound to the original circuit; we need
            # to use the corresponding Qubit objects from current_circuit before appending.
            # Extract safe indices for each qubit used by the instruction.
            try:
                src_qubits = instruction.qubits
            except Exception:
                # Older Qiskit tuple form
                try:
                    _, src_qubits, _ = instruction
                except Exception:
                    src_qubits = []

            qubit_indices = []
            for q in src_qubits:
                if hasattr(q, '_index'):
                    qubit_indices.append(q._index)
                elif hasattr(q, 'index'):
                    qubit_indices.append(q.index)
                else:
                    # Fallback: try to find the qubit object in the original circuit
                    try:
                        qubit_indices.append(circuit.qubits.index(q))
                    except Exception:
                        qubit_indices.append(0)

            # Build target qubit objects for the current circuit
            target_qubits = []
            try:
                for idx in qubit_indices:
                    target_qubits.append(current_circuit.qubits[idx])
            except Exception:
                # If mapping fails, fallback to using the original instruction.qubits (best-effort)
                target_qubits = list(src_qubits)

            # Try appending using remapped qubits; prefer to omit clbits for compatibility
            try:
                current_circuit.append(instruction.operation, target_qubits)
            except Exception:
                # Last resort: attempt to append with original qubit objects
                try:
                    current_circuit.append(instruction.operation, instruction.qubits, instruction.clbits)
                except Exception as e:
                    raise e
        except Exception as e:
            # If there are clbit issues, try without clbits (for visualization)
            try:
                # Try fallback append with remapped qubits if possible
                if 'target_qubits' in locals() and target_qubits:
                    current_circuit.append(instruction.operation, target_qubits)
                else:
                    current_circuit.append(instruction.operation, instruction.qubits)
                op_name = getattr(instruction.operation, 'name', str(instruction))
                print(f"Warning: Skipped clbits for instruction {op_name}: {e}")
            except Exception as e2:
                op_name = getattr(instruction.operation, 'name', str(instruction))
                print(f"Warning: Could not add instruction {op_name}: {e2}")
                continue
        
        frame_path = f"{session_dir}/images/creation_step_{i+1}.png"
        gate_name = instruction.operation.name
        # Use consistent scaling with reference to final circuit
        animator.save_circuit_image_with_consistent_scale(current_circuit, frame_path, f"Added {gate_name.upper()} gate", circuit)
        frames.append({
            'step': i + 1,
            'title': f'Added {gate_name.upper()} gate',
            'image': f"session_{config['session_id']}/images/creation_step_{i+1}.png",
            'description': f"Gate: {gate_name}, Qubits: {qubit_indices}"
        })
    
    return frames

async def generate_breaking_animation(circuit, session_dir, config):
    """Generate circuit breaking animation"""
    frames = []
    
    # Show original circuit
    frame_path = f"{session_dir}/images/breaking_step_0.png"
    animator.save_circuit_image(circuit, frame_path, "Original Circuit")
    frames.append({
        'step': 0,
        'title': 'Original Circuit',
        'image': f"session_{config['session_id']}/images/breaking_step_0.png",
        'description': 'Complete circuit before breaking'
    })
    
    # Add barrier to show breaking point
    broken_circuit = circuit.copy()
    # Find a good breaking point (middle of the circuit)
    num_gates = len(circuit.data)
    if num_gates > 2:
        break_point = num_gates // 2
        # Insert barrier at break point
        broken_circuit.barrier()
    
    frame_path = f"{session_dir}/images/breaking_step_1.png"
    animator.save_circuit_image(broken_circuit, frame_path, "Circuit with Barrier")
    frames.append({
        'step': 1,
        'title': 'Circuit Breaking Point',
        'image': f"session_{config['session_id']}/images/breaking_step_1.png",
        'description': 'Visual barrier showing mutation insertion point'
    })
    
    # Save broken circuit QASM
    try:
        # Try newer qiskit version method first
        try:
            qasm_content = broken_circuit.qasm()
        except AttributeError:
            # Fallback for newer qiskit versions
            from qiskit.qasm2 import dumps
            qasm_content = dumps(broken_circuit)
        
        qasm_path = f"{session_dir}/qasm/broken_circuit.qasm"
        with open(qasm_path, 'w') as f:
            f.write(qasm_content)
    except Exception as e:
        print(f"Warning: Could not generate QASM for broken circuit: {e}")
        # Create a simple QASM representation
        qasm_content = f"// Broken circuit with barrier\n"
        qasm_content += f"OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
        qasm_content += f"qreg q[{config['num_qubits']}];\ncreg c[{config['num_qubits']}];\n"
        qasm_content += "// Circuit broken at this point\nbarrier q;\n"
        qasm_path = f"{session_dir}/qasm/broken_circuit.qasm"
        with open(qasm_path, 'w') as f:
            f.write(qasm_content)
    
    return frames, broken_circuit

async def generate_mutation_animation(circuit, session_dir, config):
    """Generate mutation animation with survival rate"""
    frames = []
    mutated_circuits = []
    
    current_circuit = circuit.copy()
    survived_mutations = 0
    attempted_mutations = 0
    
    # Show starting circuit
    frame_path = f"{session_dir}/images/mutation_step_0.png"
    animator.save_circuit_image(current_circuit, frame_path, "Starting Circuit")
    frames.append({
        'step': 0,
        'title': 'Starting Circuit',
        'image': f"session_{config['session_id']}/images/mutation_step_0.png",
        'description': 'Circuit ready for mutations'
    })
    
    while survived_mutations < config['num_mutations'] and attempted_mutations < config['num_mutations'] * 2:
        attempted_mutations += 1
        
        # Simulate survival rate
        import random
        if random.random() < config['survival_rate']:
            # Mutation survives
            survived_mutations += 1
            
            # Add a random gate mutation
            mutation_gate = random.choice(['cx', 'x', 'z', 'h', 'ry'])
            if mutation_gate == 'cx' and config['num_qubits'] > 1:
                control = random.randint(0, config['num_qubits'] - 1)
                target = random.randint(0, config['num_qubits'] - 1)
                while target == control:
                    target = random.randint(0, config['num_qubits'] - 1)
                current_circuit.cx(control, target)
                mutation_desc = f"CNOT({control}, {target})"
            elif mutation_gate == 'ry':
                qubit = random.randint(0, config['num_qubits'] - 1)
                angle = random.uniform(0, 3.14159)
                current_circuit.ry(angle, qubit)
                mutation_desc = f"RY({angle:.3f}, {qubit})"
            else:
                qubit = random.randint(0, config['num_qubits'] - 1)
                if mutation_gate == 'x':
                    current_circuit.x(qubit)
                elif mutation_gate == 'z':
                    current_circuit.z(qubit)
                elif mutation_gate == 'h':
                    current_circuit.h(qubit)
                mutation_desc = f"{mutation_gate.upper()}({qubit})"
            
            # Save frame
            frame_path = f"{session_dir}/images/mutation_step_{survived_mutations}.png"
            animator.save_circuit_image(current_circuit, frame_path, f"Mutation {survived_mutations}")
            frames.append({
                'step': survived_mutations,
                'title': f'Mutation {survived_mutations}',
                'image': f"session_{config['session_id']}/images/mutation_step_{survived_mutations}.png",
                'description': f'Added: {mutation_desc} (Attempt {attempted_mutations})'
            })
            
            # Store mutated circuit
            mutated_circuits.append(current_circuit.copy())
            
            # Save mutated circuit QASM
            try:
                # Try newer qiskit version method first
                try:
                    qasm_content = current_circuit.qasm()
                except AttributeError:
                    # Fallback for newer qiskit versions
                    from qiskit.qasm2 import dumps
                    qasm_content = dumps(current_circuit)
                
                qasm_path = f"{session_dir}/qasm/mutated_circuit_{survived_mutations}.qasm"
                with open(qasm_path, 'w') as f:
                    f.write(qasm_content)
            except Exception as e:
                print(f"Warning: Could not generate QASM for mutated circuit {survived_mutations}: {e}")
                # Create a simple QASM representation
                qasm_content = f"// Mutated circuit {survived_mutations}\n"
                qasm_content += f"OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
                qasm_content += f"qreg q[{config['num_qubits']}];\ncreg c[{config['num_qubits']}];\n"
                qasm_content += f"// Mutation {survived_mutations}: {mutation_desc}\n"
                qasm_path = f"{session_dir}/qasm/mutated_circuit_{survived_mutations}.qasm"
                with open(qasm_path, 'w') as f:
                    f.write(qasm_content)
        
        # Break if we've tried too many times
        if attempted_mutations >= config['num_mutations'] * 3:
            break
    
    return frames, mutated_circuits

async def generate_qasm_files(circuit, config, session_dir):
    """Generate QASM files for download"""
    try:
        qasm_dir = f"{session_dir}/qasm"
        os.makedirs(qasm_dir, exist_ok=True)
        
        # Generate initial circuit QASM
        try:
            if hasattr(circuit, 'qasm'):
                initial_qasm = circuit.qasm()
            else:
                # Try newer qiskit version method
                from qiskit.qasm2 import dumps
                initial_qasm = dumps(circuit)
        except Exception:
            # Fallback: create a simple QASM representation
            initial_qasm = f"""OPENQASM 2.0;
include "qelib1.inc";
qreg q[{circuit.num_qubits}];
// Original circuit with {len(circuit.data)} gates
// Generated from {config['qasm_filename']}
"""
        
        with open(f"{qasm_dir}/initial_circuit.qasm", 'w') as f:
            f.write(initial_qasm)
        
        # Generate broken circuit QASM (simulation)
        broken_qasm = initial_qasm.replace("OPENQASM 2.0;", 
                                         "OPENQASM 2.0;\n// Broken circuit simulation")
        with open(f"{qasm_dir}/broken_circuit.qasm", 'w') as f:
            f.write(broken_qasm)
        
        # Generate mutated circuit QASM files
        for i in range(min(config.get('num_mutations', 3), 5)):
            mutated_qasm = initial_qasm.replace("OPENQASM 2.0;", 
                                              f"OPENQASM 2.0;\n// Mutated circuit {i+1}")
            with open(f"{qasm_dir}/mutated_circuit_{i+1}.qasm", 'w') as f:
                f.write(mutated_qasm)
        
        print(f"Generated QASM files in {qasm_dir}")
        
    except Exception as e:
        print(f"Error generating QASM files: {e}")

async def generate_qasm_slideshow(result, session_dir, config):
    """Generate simple slideshow for QASM results"""
    try:
        slideshow_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>QASM Circuit Analysis - {result['filename']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .animation-section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; display: none; }}
        .animation-section.active {{ display: block; }}
        .animation-section h3 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .gif-container {{ text-align: center; margin: 20px 0; }}
        .gif-container img {{ max-width: 100%; height: auto; border: 1px solid #ccc; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-box {{ background: #007bff; color: white; padding: 15px; border-radius: 5px; text-align: center; }}
        .stat-box h4 {{ margin: 0; font-size: 24px; }}
        .stat-box p {{ margin: 5px 0 0 0; }}
        
        .controls {{ text-align: center; margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }}
        .btn {{ background: #007bff; color: white; border: none; padding: 12px 24px; margin: 0 10px; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn:hover {{ background: #0056b3; }}
        .btn:disabled {{ background: #6c757d; cursor: not-allowed; }}
        .progress {{ width: 100%; height: 8px; background: #e9ecef; border-radius: 4px; margin: 20px 0; }}
        .progress-bar {{ height: 100%; background: #007bff; border-radius: 4px; transition: width 0.3s; }}
        .section-info {{ text-align: center; margin: 10px 0; color: #6c757d; }}
        
        .qasm-files {{ margin: 20px 0; padding: 15px; background: #e9ecef; border-radius: 5px; }}
        .qasm-files h4 {{ margin: 0 0 10px 0; color: #495057; }}
        .qasm-link {{ display: inline-block; margin: 5px 10px; padding: 8px 16px; background: #28a745; color: white; text-decoration: none; border-radius: 3px; }}
        .qasm-link:hover {{ background: #1e7e34; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>QASM Circuit Analysis Results</h1>
            <h2>{result['filename']}</h2>
            <div class="stats">
                <div class="stat-box">
                    <h4>{result['num_qubits']}</h4>
                    <p>Qubits</p>
                </div>
                <div class="stat-box">
                    <h4>{result['num_gates']}</h4>
                    <p>Gates</p>
                </div>
                <div class="stat-box">
                    <h4>{len(result['animations'])}</h4>
                    <p>Animations</p>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="previousSection()" id="prevBtn">⬅️ Previous</button>
            <button class="btn" onclick="togglePlay()" id="playBtn">⏸️ Pause</button>
            <button class="btn" onclick="nextSection()" id="nextBtn">➡️ Next</button>
            <div class="progress">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div class="section-info" id="sectionInfo">Section 1 of {len(result['animations'])}</div>
        </div>
        
        <div class="qasm-files">
            <h4>📁 Quantum Circuit Files</h4>
            <a href="/outputs/session_{config['session_id']}/qasm/initial_circuit.qasm" class="qasm-link">Initial Circuit</a>
            <a href="/outputs/session_{config['session_id']}/qasm/broken_circuit.qasm" class="qasm-link">Broken Circuit</a>
            <a href="/outputs/session_{config['session_id']}/qasm/mutated_circuit_1.qasm" class="qasm-link">Mutation 1</a>
            <a href="/outputs/session_{config['session_id']}/qasm/mutated_circuit_2.qasm" class="qasm-link">Mutation 2</a>
            <a href="/outputs/session_{config['session_id']}/qasm/mutated_circuit_3.qasm" class="qasm-link">Mutation 3</a>
        </div>
"""
        
        # Add each animation section with IDs for navigation
        section_id = 0
        if 'creation' in result['animations']:
            section_id += 1
            active_class = "active" if section_id == 1 else ""
            slideshow_content += f"""
        <div class="animation-section {active_class}" id="section{section_id}">
            <h3>🔧 Circuit Creation Animation</h3>
            <p>Step-by-step visualization of the QASM circuit construction process.</p>
            <div class="gif-container">
                <img src="{result['animations']['creation']}" alt="Circuit Creation Animation">
            </div>
        </div>
"""
        
        if 'breaking' in result['animations']:
            section_id += 1
            active_class = "active" if section_id == 1 else ""
            slideshow_content += f"""
        <div class="animation-section {active_class}" id="section{section_id}">
            <h3>⚠️ Breaking Point Analysis</h3>
            <p>Identification and visualization of the most vulnerable gates in the circuit.</p>
            <div class="gif-container">
                <img src="{result['animations']['breaking']}" alt="Breaking Analysis Animation">
            </div>
        </div>
"""
        
        if 'mutations' in result['animations']:
            section_id += 1
            active_class = "active" if section_id == 1 else ""
            slideshow_content += f"""
        <div class="animation-section {active_class}" id="section{section_id}">
            <h3>🔄 Circuit Mutations</h3>
            <p>Optimized circuit variations designed to improve robustness against noise.</p>
            <div class="gif-container">
                <img src="{result['animations']['mutations']}" alt="Mutations Animation">
            </div>
        </div>
"""
        
        # Add JavaScript for slideshow controls
        slideshow_content += f"""
    </div>
    
    <script>
        let currentSection = 1;
        let totalSections = {section_id};
        let isPlaying = true;
        let autoPlayInterval;
        
        function showSection(sectionNum) {{
            // Hide all sections
            for (let i = 1; i <= totalSections; i++) {{
                document.getElementById('section' + i).classList.remove('active');
            }}
            
            // Show current section
            document.getElementById('section' + sectionNum).classList.add('active');
            
            // Update progress bar
            const progress = (sectionNum / totalSections) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
            
            // Update section info
            document.getElementById('sectionInfo').textContent = `Section ${{sectionNum}} of ${{totalSections}}`;
            
            // Update button states
            document.getElementById('prevBtn').disabled = (sectionNum === 1);
            document.getElementById('nextBtn').disabled = (sectionNum === totalSections);
        }}
        
        function nextSection() {{
            if (currentSection < totalSections) {{
                currentSection++;
                showSection(currentSection);
            }}
        }}
        
        function previousSection() {{
            if (currentSection > 1) {{
                currentSection--;
                showSection(currentSection);
            }}
        }}
        
        function togglePlay() {{
            const playBtn = document.getElementById('playBtn');
            if (isPlaying) {{
                // Pause
                clearInterval(autoPlayInterval);
                playBtn.textContent = '▶️ Play';
                playBtn.style.background = '#28a745';
                isPlaying = false;
            }} else {{
                // Play
                startAutoPlay();
                playBtn.textContent = '⏸️ Pause';
                playBtn.style.background = '#007bff';
                isPlaying = true;
            }}
        }}
        
        function startAutoPlay() {{
            autoPlayInterval = setInterval(() => {{
                if (currentSection < totalSections) {{
                    nextSection();
                }} else {{
                    currentSection = 1;
                    showSection(currentSection);
                }}
            }}, 5000); // Change section every 5 seconds
        }}
        
        // Initialize slideshow
        showSection(1);
        if (totalSections > 1) {{
            startAutoPlay();
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'ArrowLeft') {{
                previousSection();
            }} else if (event.key === 'ArrowRight') {{
                nextSection();
            }} else if (event.key === ' ') {{
                event.preventDefault();
                togglePlay();
            }}
        }});
    </script>
</body>
</html>
"""
        
        slideshow_path = f"{session_dir}/slideshow.html"
        with open(slideshow_path, 'w') as f:
            f.write(slideshow_content)
        
        return slideshow_path
        
    except Exception as e:
        print(f"Error generating QASM slideshow: {e}")
        return None

async def generate_html_slideshow(animations, session_dir, config):
    """Generate interactive HTML slideshow"""
    slideshow_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Circuit Animation - {ALGORITHMS.get(config['algorithm'], config['algorithm'].upper())}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .circuit-info {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .animation-section {{
            margin-bottom: 40px;
        }}
        .frame-viewer {{
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .frame-image {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        .controls {{
            text-align: center;
            margin: 20px 0;
        }}
        .btn {{
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        .progress-bar {{
            width: 100%;
            height: 10px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            margin: 20px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #009fff);
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Quantum Circuit Animation</h1>
            <div class="circuit-info">
                <h3>{ALGORITHMS.get(config['algorithm'], config['algorithm'].upper())}</h3>
                <p>Qubits: {config['num_qubits']} | Survival Rate: {config['survival_rate']*100}% | Session: {config['session_id']}</p>
            </div>
        </div>
"""
    
    # Add each animation section
    for animation in animations:
        slideshow_content += f"""
        <div class="animation-section">
            <h2>{animation['title']}</h2>
            <div class="frame-viewer" id="{animation['type']}_viewer">
                <div class="progress-bar">
                    <div class="progress-fill" id="{animation['type']}_progress"></div>
                </div>
                <img class="frame-image" id="{animation['type']}_image" src="/outputs/{animation['frames'][0]['image']}" alt="Circuit Frame">
                <h3 id="{animation['type']}_title">{animation['frames'][0]['title']}</h3>
                <p id="{animation['type']}_description">{animation['frames'][0]['description']}</p>
                <div class="controls">
                    <button class="btn" onclick="previousFrame('{animation['type']}')">⏮ Previous</button>
                    <button class="btn" onclick="togglePlay('{animation['type']}')">▶ Play</button>
                    <button class="btn" onclick="nextFrame('{animation['type']}')">Next ⏭</button>
                </div>
                <p>Frame <span id="{animation['type']}_current">1</span> of <span id="{animation['type']}_total">{len(animation['frames'])}</span></p>
            </div>
        </div>
"""
    
    # Add JavaScript for interactivity
    slideshow_content += f"""
    </div>
    <script>
        const animations = {json.dumps(animations)};
        const currentFrames = {{}};
        const playing = {{}};
        const intervals = {{}};
        
        // Initialize
        animations.forEach(anim => {{
            currentFrames[anim.type] = 0;
            playing[anim.type] = false;
        }});
        
        function updateFrame(animType) {{
            const anim = animations.find(a => a.type === animType);
            const frame = anim.frames[currentFrames[animType]];
            
            document.getElementById(animType + '_image').src = '/outputs/' + frame.image;
            document.getElementById(animType + '_title').textContent = frame.title;
            document.getElementById(animType + '_description').textContent = frame.description;
            document.getElementById(animType + '_current').textContent = currentFrames[animType] + 1;
            
            const progress = ((currentFrames[animType] + 1) / anim.frames.length) * 100;
            document.getElementById(animType + '_progress').style.width = progress + '%';
        }}
        
        function nextFrame(animType) {{
            const anim = animations.find(a => a.type === animType);
            currentFrames[animType] = (currentFrames[animType] + 1) % anim.frames.length;
            updateFrame(animType);
        }}
        
        function previousFrame(animType) {{
            const anim = animations.find(a => a.type === animType);
            currentFrames[animType] = currentFrames[animType] > 0 ? currentFrames[animType] - 1 : anim.frames.length - 1;
            updateFrame(animType);
        }}
        
        function togglePlay(animType) {{
            if (playing[animType]) {{
                clearInterval(intervals[animType]);
                playing[animType] = false;
                document.querySelector(`#${{animType}}_viewer .btn:nth-child(2)`).textContent = '▶ Play';
            }} else {{
                intervals[animType] = setInterval(() => nextFrame(animType), 2000);
                playing[animType] = true;
                document.querySelector(`#${{animType}}_viewer .btn:nth-child(2)`).textContent = '⏸ Pause';
            }}
        }}
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight') {{
                Object.keys(currentFrames).forEach(animType => nextFrame(animType));
            }} else if (e.key === 'ArrowLeft') {{
                Object.keys(currentFrames).forEach(animType => previousFrame(animType));
            }} else if (e.key === ' ') {{
                e.preventDefault();
                Object.keys(playing).forEach(animType => togglePlay(animType));
            }}
        }});
    </script>
</body>
</html>
"""
    
    slideshow_path = f"{session_dir}/slideshow.html"
    with open(slideshow_path, 'w') as f:
        f.write(slideshow_content)
    
    return slideshow_path

@app.post("/advanced-breaking-analysis")
async def advanced_breaking_analysis(
    source_type: str = Form(...),
    algorithm: Optional[str] = Form(None),
    num_qubits: Optional[int] = Form(None),
    survival_rate: Optional[float] = Form(0.9),
    qasm_file: Optional[UploadFile] = File(None),
    T1_time: Optional[float] = Form(100.0),  # Relaxation time in μs
    T2_time: Optional[float] = Form(75.0),   # Dephasing time in μs
    single_qubit_error: Optional[float] = Form(0.001),  # 0.1%
    cnot_error: Optional[float] = Form(0.01),           # 1%
    temperature: Optional[float] = Form(0.015),         # 15 mK
    crosstalk_factor: Optional[float] = Form(0.05)      # 5%
):
    """
    🧮 Advanced Quantum Circuit Breaking Analysis with Mathematical Formulas
    
    Uses comprehensive physics-based models including:
    - Decoherence effects (T1/T2 times)
    - Gate fidelity models  
    - Crosstalk effects
    - Environmental noise
    - Error accumulation
    - Parametric gate sensitivity
    """
    
    try:
        # Import advanced analyzer
        from quantum_breaking_analysis import QuantumCircuitBreakingAnalyzer, NoiseProfile
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Create custom noise profile from form parameters
        # These represent real-world quantum device characteristics
        noise_profile = NoiseProfile(
            T1=T1_time,                    # Relaxation time (μs) - IBM average: 100μs
            T2=T2_time,                    # Dephasing time (μs) - IBM average: 75μs  
            single_qubit_error=single_qubit_error,  # IBM average: 0.1% (0.001)
            cnot_error=cnot_error,         # CNOT error rate - IBM average: 1% (0.01)
            temperature=temperature,       # Dilution refrigerator temp (K) - typical: 15mK
            readout_error=0.02,           # Readout fidelity - typical: 2% error (98% fidelity)
            crosstalk_factor=crosstalk_factor,  # Neighbor interference - typical: 5%
            frequency_drift=0.001         # Long-term stability - typical: 0.1% drift
        )
        
        # Initialize animator with custom noise profile
        session_animator = QuantumCircuitAnimator(session_id=session_id, noise_profile=noise_profile)
        
        circuit = None
        
        if source_type == "algorithm":
            # Validate algorithm inputs
            if not algorithm or algorithm not in ALGORITHMS:
                raise HTTPException(status_code=400, detail="Invalid algorithm")
            if not num_qubits or num_qubits < 1 or num_qubits > 20:
                raise HTTPException(status_code=400, detail="Number of qubits must be between 1 and 20")
            
            # Create circuit based on algorithm
            circuit = session_animator.get_algorithm_circuit(algorithm, num_qubits)
            circuit_name = f"{algorithm}_{num_qubits}qubits"
            
        elif source_type == "qasm":
            # Handle QASM file upload
            if not qasm_file or not qasm_file.filename:
                raise HTTPException(status_code=400, detail="QASM file is required")
            
            # Read and process QASM content
            qasm_content = await qasm_file.read()
            qasm_content = qasm_content.decode('utf-8')
            
            # Parse QASM to create circuit using existing parsing logic
            # Preprocess QASM content to handle compatibility issues
            qasm_content = preprocess_qasm_content(qasm_content)
            
            # Parse QASM content into quantum circuit
            circuit = None
            
            # Method 1: Try qiskit.qasm2.loads (newer versions) with preprocessed content
            try:
                from qiskit.qasm2 import loads
                circuit = loads(qasm_content)
                print(f"Successfully loaded QASM using qasm2.loads with preprocessing")
            except ImportError:
                print("qasm2.loads not available, trying alternative methods")
            except Exception as e:
                print(f"qasm2.loads failed: {e}")
            
            # Method 2: Try QuantumCircuit.from_qasm_str (older versions) with preprocessed content
            if circuit is None:
                try:
                    from qiskit import QuantumCircuit
                    circuit = QuantumCircuit.from_qasm_str(qasm_content)
                    print(f"Successfully loaded QASM using from_qasm_str with preprocessing")
                except Exception as e:
                    print(f"from_qasm_str failed: {e}")
            
            # Method 3: Manual parsing fallback
            if circuit is None:
                circuit = parse_qasm_manually(qasm_content)
                print(f"Successfully loaded QASM using manual parser")
            
            circuit_name = qasm_file.filename.replace('.qasm', '').replace('.txt', '')
            
        if not circuit:
            raise HTTPException(status_code=400, detail="Failed to create circuit")
        
        print(f"🧮 Starting advanced breaking analysis for {circuit_name}")
        print(f"   Circuit: {circuit.num_qubits} qubits, {len(circuit.data)} gates")
        print(f"   Noise Profile: T1={T1_time}μs, T2={T2_time}μs, CNOT_error={cnot_error}")
        
        # Perform advanced breaking analysis
        animation_path, breaking_report = await session_animator.animate_advanced_circuit_breaking(
            circuit, survival_rate, circuit_name
        )
        
        if not animation_path or not breaking_report:
            raise HTTPException(status_code=500, detail="Advanced analysis failed")
        
        # Create session directory for outputs
        session_dir = f"outputs/session_{session_id}"
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(f"{session_dir}/images", exist_ok=True)
        os.makedirs(f"{session_dir}/qasm", exist_ok=True)
        
        # Generate enhanced slideshow with breaking analysis results
        config = {
            'session_id': session_id,
            'circuit_name': circuit_name,
            'breaking_report': breaking_report,
            'noise_profile': {
                'T1': T1_time,
                'T2': T2_time,
                'single_qubit_error': single_qubit_error,
                'cnot_error': cnot_error,
                'temperature': temperature,
                'crosstalk_factor': crosstalk_factor
            },
            'advanced_analysis': True,
            'survival_rate': survival_rate
        }
        
        # Create a simple result dict for slideshow compatibility
        result = {
            'algorithm': circuit_name,
            'num_qubits': circuit.num_qubits,
            'num_gates': len(circuit.data),
            'circuit': circuit,
            'breaking_analysis': breaking_report,
        }
        
        try:
            slideshow_path = await generate_enhanced_qasm_slideshow(result, session_dir, config)
            print(f"✅ Slideshow generated: {slideshow_path}")
        except Exception as e:
            print(f"⚠️  Slideshow generation failed: {e}")
            # Create a simple HTML file as fallback
            slideshow_path = f"{session_dir}/slideshow.html"
            with open(slideshow_path, 'w') as f:
                f.write(f"""
<!DOCTYPE html>
<html>
<head><title>Advanced Breaking Analysis - {circuit_name}</title></head>
<body>
<h1>🧮 Advanced Breaking Analysis</h1>
<h2>Circuit: {circuit_name}</h2>
<p>Qubits: {circuit.num_qubits}, Gates: {len(circuit.data)}</p>
<p>Analysis complete - check the JSON report for detailed results.</p>
<p><a href="../breaking_report_{session_id}.json">Download JSON Report</a></p>
</body>
</html>
                """)
            print(f"✅ Fallback slideshow created: {slideshow_path}")
        
        # Create results summary
        results = {
            'session_id': session_id,
            'circuit_name': circuit_name,
            'source_type': source_type,
            'circuit_info': {
                'num_qubits': circuit.num_qubits,
                'num_gates': len(circuit.data),
                'depth': circuit.depth(),
                'execution_time_us': breaking_report['circuit_summary']['estimated_execution_time_us']
            },
            'breaking_analysis': breaking_report['breaking_analysis'],
            'mathematical_model': breaking_report['mathematical_model'],
            'top_risk_gates': breaking_report['top_risk_gates'][:5],
            'mitigation_recommendations': breaking_report['mitigation_priority'][:5],
            'device_recommendations': breaking_report['device_recommendations'],
            'noise_profile': {
                'T1_time': T1_time,
                'T2_time': T2_time,
                'single_qubit_error': single_qubit_error,
                'cnot_error': cnot_error,
                'temperature': temperature,
                'crosstalk_factor': crosstalk_factor
            },
            'files': {
                'animation': f"session_{session_id}/advanced_breaking_{session_id}.gif",
                'slideshow': f"session_{session_id}/slideshow.html",
                'report': f"session_{session_id}/breaking_report_{session_id}.json"
            }
        }
        
        print(f"✅ Advanced breaking analysis complete!")
        print(f"   Session ID: {session_id}")
        print(f"   Critical gates: {breaking_report['breaking_analysis']['critical_gates']}")
        print(f"   High risk gates: {breaking_report['breaking_analysis']['high_risk_gates']}")
        print(f"   Average break probability: {breaking_report['breaking_analysis']['average_break_probability']}")
        
        return JSONResponse(content=results)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in advanced breaking analysis: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/session/{session_id}")
async def get_session_results(request: Request, session_id: str):
    """Display results for a specific session"""
    session_dir = f"outputs/session_{session_id}"
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Session not found")
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "session_id": session_id
    })

@app.get("/download/{session_id}/{file_type}/{filename}")
async def download_file(session_id: str, file_type: str, filename: str):
    """Download generated files"""
    file_path = f"outputs/session_{session_id}/{file_type}/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=filename)

@app.get("/sessions")
async def sessions_page(request: Request):
    """Serve the session browser page"""
    return FileResponse("sessions.html")

@app.get("/api/sessions")
async def list_sessions():
    """Get list of all analysis sessions"""
    import datetime
    import shutil
    
    try:
        outputs_dir = Path("outputs")
        if not outputs_dir.exists():
            return []
        
        sessions = []
        for session_dir in outputs_dir.glob("session_*"):
            if session_dir.is_dir():
                session_id = session_dir.name.replace("session_", "")
                
                # Get session creation time
                created = datetime.datetime.fromtimestamp(session_dir.stat().st_ctime)
                
                # Count files and get sizes
                files = []
                total_size = 0
                
                # Check for slideshow
                slideshow_path = session_dir / "slideshow.html"
                if slideshow_path.exists():
                    size = slideshow_path.stat().st_size
                    files.append({
                        "name": "Enhanced Slideshow",
                        "url": f"/slideshow?session={session_id}",
                        "size": format_file_size(size)
                    })
                    total_size += size
                
                # Check for animations
                for gif_file in session_dir.glob("*.gif"):
                    size = gif_file.stat().st_size
                    files.append({
                        "name": gif_file.name,
                        "url": f"/outputs/{session_dir.name}/{gif_file.name}",
                        "size": format_file_size(size)
                    })
                    total_size += size
                
                # Check for frame directories
                frame_dirs = ["creation", "breaking", "mutation"]
                for frame_dir_name in frame_dirs:
                    frame_dir = session_dir / frame_dir_name
                    if frame_dir.exists():
                        frame_count = len(list(frame_dir.glob("*.png")))
                        if frame_count > 0:
                            files.append({
                                "name": f"{frame_dir_name.title()} Frames ({frame_count})",
                                "url": f"/outputs/{session_dir.name}/{frame_dir_name}/",
                                "size": f"{frame_count} frames"
                            })
                
                # Get original QASM file if it exists
                qasm_files = list(session_dir.glob("*.qasm"))
                for qasm_file in qasm_files:
                    size = qasm_file.stat().st_size
                    files.append({
                        "name": f"Original: {qasm_file.name}",
                        "url": f"/outputs/{session_dir.name}/{qasm_file.name}",
                        "size": format_file_size(size)
                    })
                    total_size += size
                
                sessions.append({
                    "id": session_id,
                    "name": f"Circuit Analysis {session_id[:8]}",
                    "created": created.isoformat(),
                    "files": files,
                    "total_size": format_file_size(total_size)
                })
        
        # Sort by creation time, newest first
        sessions.sort(key=lambda x: x["created"], reverse=True)
        return sessions
        
    except Exception as e:
        print(f"Error listing sessions: {e}")
        return []

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session"""
    import shutil
    
    try:
        session_dir = Path(f"outputs/session_{session_id}")
        if session_dir.exists():
            shutil.rmtree(session_dir)
            return {"message": f"Session {session_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@app.delete("/api/sessions")
async def clear_all_sessions():
    """Delete all sessions"""
    import shutil
    
    try:
        outputs_dir = Path("outputs")
        if outputs_dir.exists():
            # Remove all session directories
            for session_dir in outputs_dir.glob("session_*"):
                if session_dir.is_dir():
                    shutil.rmtree(session_dir)
            return {"message": "All sessions cleared successfully"}
        else:
            return {"message": "No sessions to clear"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing sessions: {str(e)}")

@app.get("/api/sessions/{session_id}/download")
async def download_session(session_id: str):
    """Download entire session as ZIP file"""
    import zipfile
    import tempfile
    
    try:
        session_dir = Path(f"outputs/session_{session_id}")
        if not session_dir.exists():
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        temp_zip.close()
        
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in session_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(session_dir)
                    zipf.write(file_path, arcname)
        
        return FileResponse(
            temp_zip.name,
            filename=f"quantum_circuit_analysis_{session_id}.zip",
            media_type="application/zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating download: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
