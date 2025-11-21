from pathlib import Path

async def generate_enhanced_qasm_slideshow(result, session_dir, config):
    """Generate interactive slideshow with frame-by-frame controls for QASM results"""
    try:
        # Ensure session_dir is a Path object
        if isinstance(session_dir, str):
            session_dir = Path(session_dir)
        
        # Check if individual frames exist
        images_dir = session_dir / "images"
        creation_frames = []
        breaking_frames = []
        mutation_frames = []
        
        if images_dir.exists():
            # Check if this is advanced breaking analysis
            advanced_frames = sorted([f for f in images_dir.glob("advanced_breaking_step_*.png")], 
                                   key=lambda x: int(x.stem.split('_')[-1]))
            
            if advanced_frames:
                # Use advanced breaking frames
                creation_frames = advanced_frames  # Show as creation section
                breaking_frames = []
                mutation_frames = []
            else:
                # Sort frames numerically by extracting the step number
                creation_frames = sorted([f for f in images_dir.glob("creation_step_*.png")], 
                                       key=lambda x: int(x.stem.split('_')[-1]))
                breaking_frames = sorted([f for f in images_dir.glob("breaking_step_*.png")], 
                                       key=lambda x: int(x.stem.split('_')[-1]))
                mutation_frames = sorted([f for f in images_dir.glob("mutation_step_*.png")], 
                                       key=lambda x: int(x.stem.split('_')[-1]))
        
        # Get circuit name from result or config
        circuit_name = result.get('algorithm', config.get('circuit_name', 'Unknown Circuit'))
        
        # Generate the HTML content
        slideshow_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>QASM Circuit Analysis - {circuit_name}</title>
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
            max-width: 1400px;
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
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        .stat-box {{
            background: rgba(255,255,255,0.2);
            padding: 15px 25px;
            border-radius: 10px;
            text-align: center;
            min-width: 100px;
        }}
        .stat-box h4 {{
            margin: 0;
            font-size: 28px;
            color: #fff;
        }}
        .stat-box p {{
            margin: 5px 0 0 0;
            color: rgba(255,255,255,0.8);
        }}
        
        .animation-section {{
            margin: 40px 0;
            padding: 25px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            display: none;
        }}
        .animation-section.active {{
            display: block;
        }}
        .animation-section h3 {{
            color: #fff;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 15px;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        
        .frame-viewer {{
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .frame-image {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        
        .animation-controls {{
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}
        .btn {{
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 12px 20px;
            margin: 0 5px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }}
        .btn:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        .btn:disabled {{
            background: rgba(255,255,255,0.1);
            cursor: not-allowed;
            transform: none;
        }}
        
        .frame-progress {{
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            margin: 15px 0;
            cursor: pointer;
        }}
        .frame-progress-bar {{
            height: 100%;
            background: #28a745;
            border-radius: 4px;
            transition: width 0.3s;
        }}
        .frame-info {{
            color: rgba(255,255,255,0.8);
            margin: 10px 0;
            font-size: 14px;
        }}
        
        .section-navigation {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}
        .section-navigation .btn {{
            font-size: 18px;
            padding: 15px 30px;
        }}
        .section-info {{
            color: rgba(255,255,255,0.8);
            margin: 15px 0;
            font-size: 16px;
        }}
        
        .qasm-files {{
            margin: 30px 0;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}
        .qasm-files h4 {{
            margin: 0 0 15px 0;
            color: #fff;
            font-size: 20px;
        }}
        .qasm-link {{
            display: inline-block;
            margin: 8px;
            padding: 10px 20px;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s;
        }}
        .qasm-link:hover {{
            background: #1e7e34;
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 QASM Circuit Analysis Results</h1>
            <h2>{circuit_name}</h2>
            <div class="stats">
                <div class="stat-box">
                    <h4>{result.get('circuit_summary', {}).get('num_qubits', result.get('num_qubits', 'N/A'))}</h4>
                    <p>Qubits</p>
                </div>
                <div class="stat-box">
                    <h4>{result.get('circuit_summary', {}).get('total_gates', result.get('num_gates', 'N/A'))}</h4>
                    <p>Gates</p>
                </div>
                <div class="stat-box">
                    <h4>{len([f for f in [creation_frames, breaking_frames, mutation_frames] if f])}</h4>
                    <p>Animations</p>
                </div>
            </div>
        </div>
        
        <div class="section-navigation">
            <button class="btn" onclick="previousSection()" id="prevSectionBtn">⬅️ Previous Section</button>
            <button class="btn" onclick="nextSection()" id="nextSectionBtn">➡️ Next Section</button>
            <div class="section-info" id="sectionInfo">Section 1 of 3</div>
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

        # Add creation animation section
        section_count = 0
        is_advanced_analysis = config.get('advanced_analysis', False)
        
        if creation_frames:
            section_count += 1
            frame_paths = [f"/outputs/session_{config['session_id']}/images/{f.name}" for f in creation_frames]
            
            if is_advanced_analysis:
                section_title = "🧮 Advanced Breaking Analysis"
                section_description = "Mathematical analysis of quantum circuit breaking points using real device physics."
            else:
                section_title = "🔧 Circuit Creation Animation"
                section_description = "Step-by-step visualization of the QASM circuit construction process."
                
            slideshow_content += f"""
        <div class="animation-section active" id="section1">
            <h3>{section_title}</h3>
            <p>{section_description}</p>
            
            <div class="frame-viewer">
                <img id="creationFrame" src="{frame_paths[0] if frame_paths else ''}" alt="Circuit Creation Frame" class="frame-image">
            </div>
            
            <div class="animation-controls">
                <button class="btn" onclick="frameControls.creation.previous()">⬅️ Previous</button>
                <button class="btn" onclick="frameControls.creation.togglePlay()" id="creationPlayBtn">⏸️ Pause</button>
                <button class="btn" onclick="frameControls.creation.next()">➡️ Next</button>
                <div class="frame-progress" onclick="frameControls.creation.seekToFrame(event)">
                    <div class="frame-progress-bar" id="creationProgressBar"></div>
                </div>
                <div class="frame-info" id="creationFrameInfo">Frame 1 of {len(frame_paths)}</div>
            </div>
        </div>
"""

        # Add breaking animation section
        if breaking_frames:
            section_count += 1
            frame_paths = [f"/outputs/session_{config['session_id']}/images/{f.name}" for f in breaking_frames]
            active_class = "active" if section_count == 1 else ""
            slideshow_content += f"""
        <div class="animation-section {active_class}" id="section{section_count}">
            <h3>⚠️ Breaking Point Analysis</h3>
            <p>Identification and visualization of the most vulnerable gates in the circuit.</p>
            
            <div class="frame-viewer">
                <img id="breakingFrame" src="{frame_paths[0] if frame_paths else ''}" alt="Breaking Analysis Frame" class="frame-image">
            </div>
            
            <div class="animation-controls">
                <button class="btn" onclick="frameControls.breaking.previous()">⬅️ Previous</button>
                <button class="btn" onclick="frameControls.breaking.togglePlay()" id="breakingPlayBtn">⏸️ Pause</button>
                <button class="btn" onclick="frameControls.breaking.next()">➡️ Next</button>
                <div class="frame-progress" onclick="frameControls.breaking.seekToFrame(event)">
                    <div class="frame-progress-bar" id="breakingProgressBar"></div>
                </div>
                <div class="frame-info" id="breakingFrameInfo">Frame 1 of {len(frame_paths)}</div>
            </div>
        </div>
"""

        # Add mutation animation section
        if mutation_frames:
            section_count += 1
            frame_paths = [f"/outputs/session_{config['session_id']}/images/{f.name}" for f in mutation_frames]
            active_class = "active" if section_count == 1 else ""
            slideshow_content += f"""
        <div class="animation-section {active_class}" id="section{section_count}">
            <h3>🔄 Circuit Mutations</h3>
            <p>Optimized circuit variations designed to improve robustness against noise.</p>
            
            <div class="frame-viewer">
                <img id="mutationFrame" src="{frame_paths[0] if frame_paths else ''}" alt="Mutation Frame" class="frame-image">
            </div>
            
            <div class="animation-controls">
                <button class="btn" onclick="frameControls.mutation.previous()">⬅️ Previous</button>
                <button class="btn" onclick="frameControls.mutation.togglePlay()" id="mutationPlayBtn">⏸️ Pause</button>
                <button class="btn" onclick="frameControls.mutation.next()">➡️ Next</button>
                <div class="frame-progress" onclick="frameControls.mutation.seekToFrame(event)">
                    <div class="frame-progress-bar" id="mutationProgressBar"></div>
                </div>
                <div class="frame-info" id="mutationFrameInfo">Frame 1 of {len(frame_paths)}</div>
            </div>
        </div>
"""

        # Add JavaScript for both section and frame controls
        slideshow_content += f"""
    </div>
    
    <script>
        // Animation frame data - ensure numerical order
        const animationData = {{
            creation: {sorted([f.name for f in creation_frames], key=lambda x: int(x.split('_')[-1].split('.')[0]))},
            breaking: {sorted([f.name for f in breaking_frames], key=lambda x: int(x.split('_')[-1].split('.')[0]))},
            mutation: {sorted([f.name for f in mutation_frames], key=lambda x: int(x.split('_')[-1].split('.')[0]))}
        }};
        
        // Section navigation
        let currentSection = 1;
        let totalSections = {section_count};
        
        function showSection(sectionNum) {{
            for (let i = 1; i <= totalSections; i++) {{
                document.getElementById('section' + i).classList.remove('active');
            }}
            document.getElementById('section' + sectionNum).classList.add('active');
            document.getElementById('sectionInfo').textContent = `Section ${{sectionNum}} of ${{totalSections}}`;
            
            // Update buttons
            document.getElementById('prevSectionBtn').disabled = sectionNum <= 1;
            document.getElementById('nextSectionBtn').disabled = sectionNum >= totalSections;
        }}
        
        function previousSection() {{
            if (currentSection > 1) {{
                currentSection--;
                showSection(currentSection);
            }}
        }}
        
        function nextSection() {{
            if (currentSection < totalSections) {{
                currentSection++;
                showSection(currentSection);
            }}
        }}
        
        // Frame controls for each animation
        const frameControls = {{
            creation: createFrameController('creation'),
            breaking: createFrameController('breaking'),
            mutation: createFrameController('mutation')
        }};
        
        function createFrameController(animationType) {{
            let currentFrame = 0;
            let isPlaying = false;
            let playInterval = null;
            const frames = animationData[animationType];
            const sessionId = '{config['session_id']}';
            
            return {{
                currentFrame: 0,
                isPlaying: false,
                
                showFrame: function(frameIndex) {{
                    if (frames.length === 0) return;
                    
                    currentFrame = Math.max(0, Math.min(frameIndex, frames.length - 1));
                    const frameElement = document.getElementById(animationType + 'Frame');
                    if (frameElement) {{
                        frameElement.src = `/outputs/session_${{sessionId}}/images/${{frames[currentFrame]}}`;
                    }}
                    
                    // Update progress bar
                    const progressBar = document.getElementById(animationType + 'ProgressBar');
                    if (progressBar) {{
                        const progress = frames.length > 1 ? (currentFrame / (frames.length - 1)) * 100 : 0;
                        progressBar.style.width = progress + '%';
                    }}
                    
                    // Update frame info
                    const frameInfo = document.getElementById(animationType + 'FrameInfo');
                    if (frameInfo) {{
                        frameInfo.textContent = `Frame ${{currentFrame + 1}} of ${{frames.length}}`;
                    }}
                }},
                
                next: function() {{
                    if (currentFrame < frames.length - 1) {{
                        this.showFrame(currentFrame + 1);
                    }}
                }},
                
                previous: function() {{
                    if (currentFrame > 0) {{
                        this.showFrame(currentFrame - 1);
                    }}
                }},
                
                togglePlay: function() {{
                    const playBtn = document.getElementById(animationType + 'PlayBtn');
                    if (isPlaying) {{
                        clearInterval(playInterval);
                        isPlaying = false;
                        if (playBtn) playBtn.textContent = '▶️ Play';
                    }} else {{
                        playInterval = setInterval(() => {{
                            if (currentFrame < frames.length - 1) {{
                                this.showFrame(currentFrame + 1);
                            }} else {{
                                this.showFrame(0); // Loop back to start
                            }}
                        }}, 1000);
                        isPlaying = true;
                        if (playBtn) playBtn.textContent = '⏸️ Pause';
                    }}
                }},
                
                seekToFrame: function(event) {{
                    const progressBar = event.currentTarget;
                    const rect = progressBar.getBoundingClientRect();
                    const clickX = event.clientX - rect.left;
                    const progressBarWidth = rect.width;
                    const clickPercentage = clickX / progressBarWidth;
                    const targetFrame = Math.round(clickPercentage * (frames.length - 1));
                    this.showFrame(targetFrame);
                }}
            }};
        }}
        
        // Initialize
        showSection(1);
        
        // Keyboard controls
        document.addEventListener('keydown', function(event) {{
            switch(event.key) {{
                case 'ArrowLeft':
                    previousSection();
                    break;
                case 'ArrowRight':
                    nextSection();
                    break;
                case ' ':
                    event.preventDefault();
                    // Toggle play for current section
                    if (currentSection === 1 && frameControls.creation) frameControls.creation.togglePlay();
                    else if (currentSection === 2 && frameControls.breaking) frameControls.breaking.togglePlay();
                    else if (currentSection === 3 && frameControls.mutation) frameControls.mutation.togglePlay();
                    break;
            }}
        }});
    </script>
</body>
</html>
"""
        
        # Save slideshow
        slideshow_path = session_dir / "slideshow.html"
        with open(slideshow_path, 'w') as f:
            f.write(slideshow_content)
            
        print(f"Enhanced slideshow saved to {slideshow_path}")
        return slideshow_path
        
    except Exception as e:
        print(f"Error generating enhanced slideshow: {e}")
        import traceback
        traceback.print_exc()
        return None
