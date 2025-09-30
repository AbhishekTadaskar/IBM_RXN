import streamlit as st
from rxn4chemistry import RXN4ChemistryWrapper
import json
from datetime import datetime

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
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .step-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 5px solid #28a745;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'extraction_history' not in st.session_state:
    st.session_state.extraction_history = []
if 'api_initialized' not in st.session_state:
    st.session_state.api_initialized = False

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
    1. Paste your reaction procedure
    2. Click "Extract Protocol Steps"
    3. Review the structured output
    """)
    
    st.divider()
    
    st.header("⚙️ Settings")
    show_raw_response = st.checkbox("Show raw API response", value=False)
    enable_history = st.checkbox("Enable extraction history", value=True)
    
    if enable_history and st.session_state.extraction_history:
        if st.button("Clear History", type="secondary"):
            st.session_state.extraction_history = []
            st.rerun()

# Main content
st.markdown('<h1 class="main-header">🧪 IBM RXN Chemistry Protocol Extractor</h1>', unsafe_allow_html=True)

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
        API_KEY = st.secrets["ibm_rxn_api_key"]
        rxn_wrapper = RXN4ChemistryWrapper(api_key=API_KEY)
        st.session_state.rxn_wrapper = rxn_wrapper
        st.session_state.api_initialized = True
    else:
        rxn_wrapper = st.session_state.rxn_wrapper
except Exception as e:
    st.error(f"❌ Failed to initialize IBM RXN API: {e}")
    st.info("Please check your API key in the Streamlit secrets configuration.")
    st.stop()

# Example procedures
with st.expander("📖 View Example Procedures"):
    example1 = """To a solution of 2-bromopyridine (1.0 g, 6.33 mmol) in THF (20 mL) 
    at -78°C was added n-BuLi (2.5 M in hexanes, 2.78 mL, 6.96 mmol) dropwise. 
    The mixture was stirred for 30 min at -78°C, then DMF (0.74 mL, 9.5 mmol) was added. 
    The reaction was warmed to room temperature and stirred for 2 h. The mixture was 
    quenched with saturated NH4Cl solution and extracted with EtOAc (3 x 20 mL). 
    The combined organic layers were dried over Na2SO4, filtered, and concentrated 
    under reduced pressure to give the crude product."""
    
    example2 = """A mixture of benzaldehyde (10.6 g, 100 mmol) and acetone (7.3 mL, 100 mmol) 
    in ethanol (50 mL) was treated with 10% NaOH solution (10 mL). The mixture was stirred 
    at room temperature for 3 hours. The precipitate was collected by filtration, washed 
    with cold ethanol, and dried to afford the product as a yellow solid (12.5 g, 85% yield)."""
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load Example 1"):
            st.session_state.example_text = example1
    with col2:
        if st.button("Load Example 2"):
            st.session_state.example_text = example2

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
with col3:
    if st.session_state.get('last_result'):
        download_enabled = True
    else:
        download_enabled = False

if clear_button:
    st.session_state.example_text = ''
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
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Download as JSON
                        json_data = json.dumps(result, indent=2)
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_data,
                            file_name="protocol_steps.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # Download as TXT
                        txt_data = "\n\n".join([f"Step {i}: {action}" for i, action in enumerate(actions, 1)])
                        st.download_button(
                            label="📥 Download TXT",
                            data=txt_data,
                            file_name="protocol_steps.txt",
                            mime="text/plain"
                        )
                    
                    with col3:
                        # Download as Markdown
                        md_data = "# Extracted Protocol Steps\n\n" + "\n\n".join([f"**Step {i}:** {action}" for i, action in enumerate(actions, 1)])
                        st.download_button(
                            label="📥 Download MD",
                            data=md_data,
                            file_name="protocol_steps.md",
                            mime="text/markdown"
                        )
                
                else:
                    st.info("ℹ️ No protocol steps extracted. Please verify the input format and try again.")
                    
            except Exception as e:
                st.error(f"❌ Error calling IBM RXN API: {str(e)}")
                st.info("💡 **Troubleshooting tips:**\n- Check your API key is valid\n- Verify your internet connection\n- Ensure the input text is a valid chemical procedure")

# Display extraction history
if enable_history and st.session_state.extraction_history:
    st.divider()
    st.subheader("📜 Extraction History")
    
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