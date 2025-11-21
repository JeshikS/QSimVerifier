#!/usr/bin/env python3
"""
Test script to generate slideshow for existing session
"""

import sys
import os
sys.path.append('/home/jeshik_1/jeshik/QSimVerifier/CircuitAnimation')

from enhanced_slideshow import generate_enhanced_qasm_slideshow
import asyncio
from pathlib import Path

async def test_slideshow_generation():
    """Test slideshow generation for session_d3d1a280"""
    
    session_dir = Path("/home/jeshik_1/jeshik/QSimVerifier/CircuitAnimation/outputs/session_d3d1a280")
    
    # Mock result data for the advanced analysis
    result = {
        'algorithm': 'ae_6qubits',
        'num_qubits': 6,
        'num_gates': 7,
        'circuit': None,  # Not needed for slideshow
        'breaking_analysis': {}
    }
    
    # Mock config data
    config = {
        'session_id': 'd3d1a280',
        'circuit_name': 'ae_6qubits',
        'advanced_analysis': True,
        'survival_rate': 0.9
    }
    
    print(f"🔧 Testing slideshow generation for session d3d1a280")
    print(f"   Session dir: {session_dir}")
    print(f"   Images available: {len(list(session_dir.glob('images/advanced_breaking_step_*.png')))}")
    
    try:
        slideshow_path = await generate_enhanced_qasm_slideshow(result, session_dir, config)
        
        if slideshow_path and slideshow_path.exists():
            print(f"✅ Slideshow generated successfully!")
            print(f"   Path: {slideshow_path}")
            print(f"   Size: {slideshow_path.stat().st_size} bytes")
        else:
            print(f"❌ Slideshow generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_slideshow_generation())