import streamlit as st
from rxn4chemistry import RXN4ChemistryWrapper
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="IBM RXN Chemistry Protocol Extractor",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    /* IMPROVED VISIBILITY STYLES */
    .step-box {
        background-color: #e8f5e9; /* Light green tint for high visibility */
        color: #1b5e20; /* Dark green text */
        padding: 18px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 6px solid #4caf50; /* Green highlight */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        font-size: 1.05rem;
    }
    .step-box strong {
        color: #1b5e20;
        font-size: 1.15rem;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #ffd700;
    }
    .info-box strong {
        font-size: 1.1rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    .success-box {
        background: linear-gradient(90deg, #d4edda 0%, #aed581 100%); /* Vibrant Green gradient */
        color: #155724; /* Darker text for contrast */
        padding: 18px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 6px solid #28a745;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
    }
    .success-box strong {
        font-size: 1.2rem;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 5px solid #dc3545;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'extraction_history' not in st.session_state:
    st.session_state.extraction_history = []
if 'api_initialized' not in st.session_state:
    st.session_state.api_initialized = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'example_text' not in st.session_state:
    st.session_state.example_text = ''


# Function to load API key with multiple fallback methods
def load_api_key():
    """Try multiple methods to load the API key"""
    
    # Method 1: Try Streamlit secrets (for deployment)
    try:
        if "ibm_rxn_api_key" in st.secrets:
            return st.secrets["ibm_rxn_api_key"]
    except Exception:
        pass
    
    # Method 2: Try environment variable
    api_key = os.environ.get("IBM_RXN_API_KEY")
    if api_key:
        return api_key
    
    # Method 3: Try reading from secrets.toml directly (for local development)
    return None

# Sidebar
with st.sidebar:
    st.header("📋 About")
    st.markdown("""
    This tool uses **IBM RXN for Chemistry** to extract structured synthesis 
    protocol steps from natural language descriptions of chemical reactions.
    
    ### Features:
    - 🔍 Extract action steps
    - 📝 View detailed results
    - 💾 Download extracted protocols
    - 📊 History tracking
    
    ### How to use:
    1. Enter your API key (if not configured)
    2. Paste your reaction procedure
    3. Click "Extract Protocol Steps"
    4. Review the structured output
    """)
    
    st.divider()
    
    st.header("⚙️ Settings")
    show_raw_response = st.checkbox("Show raw API response", value=False)
    enable_history = st.checkbox("Enable extraction history", value=True)
    
    if enable_history and st.session_state.extraction_history:
        if st.button("Clear History", type="secondary"):
            st.session_state.extraction_history = []
            st.rerun()
    
    st.divider()
    
    # API Key Configuration in Sidebar
    st.header("🔑 API Configuration")
    
    # Check if API key is already loaded
    if not st.session_state.api_key:
        st.session_state.api_key = load_api_key()
    
    if st.session_state.api_key:
        st.success("✅ API Key loaded successfully!")
        masked_key = st.session_state.api_key[:10] + "..." + st.session_state.api_key[-10:]
        st.text(f"Key: {masked_key}")
        
        if st.button("Change API Key"):
            st.session_state.api_key = None
            st.session_state.api_initialized = False
            st.rerun()
    else:
        st.warning("⚠️ API Key not found")
        
        with st.expander("📖 How to setup API Key"):
            st.markdown("""
            **Method 1: Create secrets.toml file**
            1. Create folder: `.streamlit` in your project
            2. Create file: `secrets.toml` inside `.streamlit`
            3. Add: `ibm_rxn_api_key = "your-key-here"`
            
            **Method 2: Set environment variable**
            ```
            set IBM_RXN_API_KEY=your-key-here
            ```
            
            **Method 3: Enter manually below**
            """)
        
        # Manual API key input
        manual_key = st.text_input(
            "Enter API Key manually:",
            type="password",
            help="Your IBM RXN API key"
        )
        
        if st.button("Save API Key") and manual_key:
            st.session_state.api_key = manual_key
            st.session_state.api_initialized = False
            st.success("✅ API Key saved for this session!")
            st.rerun()

# Main content
st.markdown('<h1 class="main-header">🧪 IBM RXN Chemistry Protocol Extractor</h1>', unsafe_allow_html=True)

# Check if API key is available
if not st.session_state.api_key:
    st.markdown("""
    <div class="error-box">
        <strong>❌ API Key Required</strong><br>
        Please configure your IBM RXN API key in the sidebar to use this application.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("""
<div class="info-box">
    <strong>📌 Instructions:</strong> Paste a chemical reaction procedure below. 
    The AI will identify and extract individual synthesis steps such as additions, 
    heating, stirring, purification, etc.
</div>
""", unsafe_allow_html=True)

# Initialize API wrapper with error handling
try:
    if not st.session_state.api_initialized:
        with st.spinner("🔄 Initializing IBM RXN API..."):
            rxn_wrapper = RXN4ChemistryWrapper(api_key=st.session_state.api_key)
            st.session_state.rxn_wrapper = rxn_wrapper
            st.session_state.api_initialized = True
    else:
        rxn_wrapper = st.session_state.rxn_wrapper
except Exception as e:
    st.markdown(f"""
    <div class="error-box">
        <strong>❌ Failed to initialize IBM RXN API:</strong><br>
        {str(e)}
    </div>
    """, unsafe_allow_html=True)
    st.info("💡 Please check your API key is valid and try again.")
    if st.button("Reset API Configuration"):
        st.session_state.api_key = None
        st.session_state.api_initialized = False
        st.rerun()
    st.stop()

# Example procedures
with st.expander("📖 View Example Procedures", expanded=True):
    st.markdown("""
    **Example 1: Organolithium Synthesis** (Lithiation followed by quench)
    """)
    
    # Using LaTeX for chemical formulas
    example1 = """To a solution of 2-bromopyridine ($1.0\ g$, $6.33\ mmol$) in THF ($20\ mL$) at $-78^{\circ}C$ was added $n-BuLi$ ($2.5\ M$ in hexanes, $2.78\ mL$, $6.96\ mmol$) dropwise. The mixture was stirred for $30\ min$ at $-78^{\circ}C$, then DMF ($0.74\ mL$, $9.5\ mmol$) was added. The reaction was warmed to room temperature and stirred for $2\ h$. The mixture was quenched with saturated $NH_{4}Cl$ solution and extracted with EtOAc ($3\ x\ 20\ mL$). The combined organic layers were dried over $Na_{2}SO_{4}$, filtered, and concentrated under reduced pressure to give the crude product."""
    
    st.markdown("""
    **Example 2: Aldol Condensation** (Base-catalyzed C-C bond formation)
    """)
    
    example2 = """A mixture of benzaldehyde ($10.6\ g$, $100\ mmol$) and acetone ($7.3\ mL$, $100\ mmol$) in ethanol ($50\ mL$) was treated with $10\%\ NaOH$ solution ($10\ mL$). The mixture was stirred at room temperature for $3\ hours$. The precipitate was collected by filtration, washed with cold ethanol, and dried to afford the product as a yellow solid ($12.5\ g$, $85\%\ yield$)."""

    st.markdown("""
    **Example 3: Model Description** (Text describing the AI's function)
    """)
    
    # Restored third example with LaTeX for temperature/concentration
    example3 = """The IBM RXN for Chemistry tool uses a sophisticated deep-learning model, often described as a Transformer-based sequence-to-sequence architecture, to effectively "translate" a free-form, natural language experimental procedure into a structured, machine-readable protocol. For instance, a sentence like, "The mixture was stirred for 30 minutes at $25^{\circ}C$, then the $pH$ was adjusted to $9$ by addition of $6M\ NaOH$," is converted into a distinct sequence of action steps: STIR for 30 minutes at $25^{\circ}C$, followed by PH with $6M\ NaOH$ to $pH\ 9$. This process extracts all relevant chemical entities, quantities, conditions, and operations, standardizing the information into a format that is not only easily analyzable but also directly executable by robotic chemical synthesis platforms like RoboRXN, thereby accelerating the work of chemists."""

    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Load Example 1", use_container_width=True, key="load1"):
            st.session_state.example_text = example1
            st.rerun()
    with col2:
        if st.button("Load Example 2", use_container_width=True, key="load2"):
            st.session_state.example_text = example2
            st.rerun()
    with col3:
        if st.button("Load Example 3", use_container_width=True, key="load3"):
            st.session_state.example_text = example3
            st.rerun()


# Text input area
input_text = st.text_area(
    "Reaction Procedure Text",
    height=300,
    placeholder="Paste your chemical reaction procedure here...",
    value=st.session_state.get('example_text', ''),
    key="procedure_input"
)

# Character count
if input_text:
    st.caption(f"📊 Character count: {len(input_text)}")

# Action buttons
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    extract_button = st.button("🔬 Extract Protocol Steps", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

if clear_button:
    st.session_state.example_text = ''
    if 'last_result' in st.session_state:
        del st.session_state.last_result
    st.rerun()

# Main extraction logic
if extract_button:
    if not input_text.strip():
        st.warning("⚠️ Please enter some reaction procedure text first.")
    else:
        with st.spinner("🔄 Extracting synthesis protocol steps..."):
            try:
                # Call IBM RXN API
                result = rxn_wrapper.paragraph_to_actions(paragraph=input_text)
                
                # Store result in session state
                st.session_state.last_result = result
                
                # Extract actions
                actions = result.get("actions", [])
                
                if actions:
                    # Success message
                    st.markdown(f"""
                    <div class="success-box">
                        ✅ <strong>Successfully extracted {len(actions)} protocol steps!</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display extracted steps
                    st.subheader("📋 Extracted Protocol Steps:")
                    
                    for i, action in enumerate(actions, 1):
                        st.markdown(f"""
                        <div class="step-box">
                            <strong>Step {i}:</strong> {action}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show raw response if enabled
                    if show_raw_response:
                        st.subheader("🔍 Raw API Response:")
                        st.json(result)
                    
                    # Add to history
                    if enable_history:
                        st.session_state.extraction_history.append({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'input': input_text[:100] + "..." if len(input_text) > 100 else input_text,
                            'steps_count': len(actions),
                            'actions': actions
                        })
                    
                    # Download options
                    st.subheader("💾 Download Results:")
                    col1_dl, col2_dl, col3_dl = st.columns(3)
                    
                    with col1_dl:
                        # Download as JSON
                        json_data = json.dumps(result, indent=2)
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_data,
                            file_name="protocol_steps.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                    with col2_dl:
                        # Download as TXT
                        txt_data = "\n\n".join([f"Step {i}: {action}" for i, action in enumerate(actions, 1)])
                        st.download_button(
                            label="📥 Download TXT",
                            data=txt_data,
                            file_name="protocol_steps.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col3_dl:
                        # Download as Markdown
                        md_data = "# Extracted Protocol Steps\n\n" + "\n\n".join([f"**Step {i}:** {action}" for i, action in enumerate(actions, 1)])
                        st.download_button(
                            label="📥 Download MD",
                            data=md_data,
                            file_name="protocol_steps.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                
                else:
                    st.info("ℹ️ No protocol steps extracted. Please verify the input format and try again.")
                    
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                    <strong>❌ Error calling IBM RXN API:</strong><br>
                    {str(e)}
                </div>
                """, unsafe_allow_html=True)
                st.info("""
                💡 **Troubleshooting tips:**
                - Check your API key is valid and active
                - Verify your internet connection
                - Ensure the input text is a valid chemical procedure
                - Try with one of the example procedures first
                """)

# Display extraction history
if enable_history and st.session_state.extraction_history:
    st.divider()
    st.subheader("📜 Extraction History")
    
    # Show last 5 entries
    for idx, entry in enumerate(reversed(st.session_state.extraction_history[-5:]), 1):
        with st.expander(f"🕐 {entry['timestamp']} - {entry['steps_count']} steps extracted"):
            st.write(f"**Input preview:** {entry['input']}")
            st.write("**Extracted steps:**")
            for i, action in enumerate(entry['actions'], 1):
                st.write(f"{i}. {action}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Powered by <strong>IBM RXN for Chemistry</strong> | Built with ❤️ using Streamlit</p>
    <p style="font-size: 0.8rem;">⚗️ For research and educational purposes</p>
</div>
""", unsafe_allow_html=True)
