import streamlit as st
import google.generativeai as genai

def initialize_session_state():
    """Initialize session state variables"""
    if 'phase' not in st.session_state:
        st.session_state.phase = 'setup'  
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'candidate_name' not in st.session_state:
        st.session_state.candidate_name = ""
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'question_start_time' not in st.session_state:
        st.session_state.question_start_time = None
    if 'api_tested' not in st.session_state:
        st.session_state.api_tested = False
    if 'api_test_result' not in st.session_state:
        st.session_state.api_test_result = None

def test_api_connection(api_key):
    """Test API connection with current Gemini models and store result in session state"""
    try:
        genai.configure(api_key=api_key)
        
        # Updated model names based on current Gemini API (September 2025)
        model_names = [
            # Try the most stable and widely available models first
            'gemini-2.5-flash',
            'gemini-2.5-pro', 
            'gemini-2.0-flash',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            
            # Try with models/ prefix as backup
            'models/gemini-2.5-flash',
            'models/gemini-2.5-pro',
            'models/gemini-2.0-flash', 
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]
        
        last_error = None
        
        for model_name in model_names:
            try:
                st.info(f"Testing connection with {model_name}...")
                
                test_model = genai.GenerativeModel(model_name)
                test_response = test_model.generate_content(
                    "Respond with exactly 'API_TEST_SUCCESS' if you receive this message.",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=20,
                        temperature=0.1,
                        top_p=0.8
                    ),
                    request_options={'timeout': 20}
                )
                
                if test_response and test_response.text:
                    response_text = test_response.text.strip()
                    st.success(f"✅ API test successful with {model_name}")
                    st.success(f"Response: {response_text}")
                    
                    st.session_state.api_test_result = f"success_with_{model_name}"
                    st.session_state.api_tested = True
                    return True
                else:
                    st.warning(f"⚠️ Empty response from {model_name}")
                    last_error = f"Empty response from {model_name}"
                    continue
                    
            except Exception as e:
                error_msg = str(e)
                st.warning(f"❌ Failed with {model_name}: {error_msg[:100]}...")
                last_error = error_msg
                
                # Special handling for common errors
                if "404" in error_msg:
                    st.info(f"Model {model_name} not found, trying next model...")
                elif "quota" in error_msg.lower():
                    st.error("⚠️ API quota exceeded. Please check your usage limits.")
                elif "permission" in error_msg.lower():
                    st.error("⚠️ Permission denied. Please check your API key permissions.")
                elif "timeout" in error_msg.lower():
                    st.warning("⚠️ Request timed out. Trying next model...")
                
                continue
        
        # No working model found
        st.session_state.api_test_result = f"no_working_model_found: {last_error}"
        st.session_state.api_tested = True
        st.error("❌ No working Gemini model found.")
        
        if last_error:
            st.error(f"Last error: {last_error}")
        
        # Show helpful suggestions
        st.markdown("""
        ### Troubleshooting Tips:
        1. **Check your API key**: Make sure it's valid and active
        2. **Verify quota**: Check your usage limits in [Google AI Studio](https://aistudio.google.com)
        3. **Try again**: Sometimes models have temporary availability issues
        4. **Check regions**: Some models may not be available in your region
        """)
        
        return False
        
    except Exception as e:
        error_msg = str(e)
        st.session_state.api_test_result = error_msg
        st.session_state.api_tested = True
        st.error(f"❌ API configuration error: {error_msg}")
        
        # Provide specific guidance for common issues
        if "api_key" in error_msg.lower():
            st.info("💡 Make sure your API key is correctly configured.")
        elif "module" in error_msg.lower():
            st.info("💡 Make sure you have installed: `pip install google-generativeai`")
        
        return False

def reset_session():
    """Reset all session state variables"""
    keys_to_keep = ['api_tested', 'api_test_result']  # Keep API test results
    
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    
    initialize_session_state()

def get_model_info():
    """Get information about available models"""
    return {
        'gemini-2.5-pro': {
            'description': 'Most powerful thinking model with maximum response accuracy',
            'best_for': 'Complex reasoning, analysis, and detailed responses',
            'status': 'Stable'
        },
        'gemini-2.5-flash': {
            'description': 'Best price-performance model with well-rounded capabilities',
            'best_for': 'General use, low latency, high volume tasks',
            'status': 'Stable'
        },
        'gemini-2.0-flash': {
            'description': 'Next-gen features with improved capabilities',
            'best_for': 'Speed, native tool use, 1M token context',
            'status': 'Stable'
        },
        'gemini-1.5-flash': {
            'description': 'Fast and versatile multimodal model (deprecated but available)',
            'best_for': 'Scaling across diverse tasks',
            'status': 'Deprecated - will be retired September 24, 2025'
        },
        'gemini-1.5-pro': {
            'description': 'Advanced reasoning model (deprecated but available)',
            'best_for': 'Complex reasoning tasks with large context',
            'status': 'Deprecated - will be retired September 24, 2025'
        }
    }

def display_model_status():
    """Display current model availability and status"""
    st.subheader("📋 Current Gemini Model Status")
    
    model_info = get_model_info()
    
    for model_name, info in model_info.items():
        with st.expander(f"🤖 {model_name}"):
            st.write(f"**Description:** {info['description']}")
            st.write(f"**Best for:** {info['best_for']}")
            
            if 'Deprecated' in info['status']:
                st.warning(f"⚠️ **Status:** {info['status']}")
            else:
                st.success(f"✅ **Status:** {info['status']}")
                
    st.info("💡 The application will automatically try models in order of preference and use the first available one.")