# Quantum Circuit Mutation Animation - Step 1 Complete

## Overview

This project implements a quantum circuit mutation animation pipeline that reads circuit data from CSV files and creates animated GIFs showing the evolution of quantum circuits through mutation processes.

## What We've Accomplished (Step 1)

### ✅ Core Features Implemented

1. **CSV Data Processing**: Successfully reads `merged_data_001.csv` with circuit parameters
2. **Initial Circuit Generation**: Creates quantum circuits matching the statistical properties from CSV data
3. **Circuit Breaking**: Removes gates at specified positions and adds visual barriers
4. **Mutation Process**: Adds new gates with configurable survival rates (default 90%)
5. **Animation Generation**: Creates frame-by-frame GIFs showing circuit evolution
6. **Multi-row Processing**: Processes multiple CSV rows automatically

### 📊 CSV Data Structure Supported

The pipeline works with the following CSV columns:
- `Origin_program`: Circuit identifier
- `algorithm`: Algorithm type (ae, dj, ghz, etc.)
- `qubits`: Number of qubits
- `gates`: Total gate count
- `singlequbit_gates`: Single-qubit gate count
- `multiqubit_gates`: Multi-qubit gate count
- `measurement_gates`: Measurement gate count
- `Gate`: Type of gate to remove/add
- `New_gate`: Gate type for mutations
- `Position_percent`: Position for mutations (percentage)
- `Line`: Line number for circuit breaking
- `Killed`: Mutation survival indicator

### 🎯 Animation Pipeline Process

1. **Initial Circuit Building**: 
   - Reads circuit parameters from CSV
   - Generates random circuit matching gate counts
   - Animates gate-by-gate construction

2. **Circuit Breaking**:
   - Removes gate at specified position (`Line` or `Position_int`)
   - Inserts visual barrier to show break point

3. **Mutation Phase**:
   - Attempts specified number of mutations (default: 5)
   - Each mutation survives with 90% probability
   - Inserts new gates at calculated positions

4. **GIF Export**:
   - Saves complete animation as GIF file
   - Each frame shows circuit state at that step

### 📁 Files Generated

- `animate_qc_mutation.py`: Main animation script
- `demo_circuit.py`: Sample circuit demonstration
- `circuit_evolution_row_X.gif`: Animation for each CSV row
- `sample_circuit.png`: Example circuit diagram

### 🚀 Usage

```bash
# Activate virtual environment
cd /home/jeshik_1/jeshik/Quantum-Circuit-Mutants-Empirical-Evaluation
source .venv/bin/activate

# Run animation on CSV data
cd RecomendationTool
python animate_qc_mutation.py

# View sample circuit
python demo_circuit.py
```

### 📈 Sample Output

The script successfully processed the first 3 rows from `merged_data_001.csv`:

```
Row 1: ae_indep_qiskit_2 - 2 qubits, 7 operations → 4/5 mutations applied
Row 2: ae_indep_qiskit_2 - 2 qubits, 7 operations → 5/5 mutations applied  
Row 3: ae_indep_qiskit_2 - 2 qubits, 7 operations → 5/5 mutations applied
```

### 🔧 Technical Details

**Dependencies Installed:**
- qiskit: Quantum circuit simulation and visualization
- pandas: CSV data processing
- matplotlib: Circuit diagram rendering
- pillow: Image processing and GIF creation
- numpy: Numerical operations
- pylatexenc: LaTeX encoding for circuit labels

**Key Improvements Made:**
- Fixed matplotlib canvas compatibility issues
- Added robust error handling for circuit rendering
- Implemented fallback mechanisms for different matplotlib versions
- Enhanced position calculation logic
- Added comprehensive logging and progress tracking

### 🎨 Visual Features

- **Circuit Diagrams**: Professional quantum circuit visualizations
- **Barrier Visualization**: Clear indication of circuit break points
- **Gate Animation**: Step-by-step gate addition with smooth transitions
- **Mutation Tracking**: Visual indication of successful mutations
- **GIF Export**: Smooth animations with configurable frame duration

### 📋 Next Steps (Future Enhancements)

1. **Algorithm-Specific Circuits**: Implement canonical circuits for each algorithm type
2. **Advanced Mutation Strategies**: Add fitness-based selection instead of random survival
3. **Interactive Visualization**: Web-based interface for real-time circuit exploration
4. **Batch Processing**: Optimize for processing large CSV files
5. **Custom Gate Libraries**: Support for additional quantum gate types

### 🔍 Example Circuit Data

```
Origin Program: ae_indep_qiskit_2
Algorithm: ae (Amplitude Estimation)
Qubits: 2
Gates: 8 total (5 single-qubit, 3 multi-qubit, 2 measurement)
New gate: cx (CNOT)
Position: 60% through circuit
```

This completes **Step 1** of the quantum circuit mutation animation pipeline with full functionality for processing CSV data and generating animated visualizations of circuit evolution through mutation processes.
