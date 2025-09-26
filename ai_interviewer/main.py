import streamlit as st
from services.ai_service import AIInterviewer
from ui.setup_phase import show_setup_phase
from ui.interview_phase import show_interview_phase
from ui.results_phase import show_results_phase
from utils.session_utils import initialize_session_state, test_api_connection

st.set_page_config(
    page_title="AI Interviewer - SDE Intern",
    page_icon="🤖",
    layout="wide"
)

def main():
    """Main application function"""
    initialize_session_state()
    
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Gemini API Key", type="password", 
                               help="Get your free API key from Google AI Studio")
        
        if api_key:
            st.success("✅ API Key configured")
            
            if st.button("🧪 Test API Connection", key="test_api_btn"):
                with st.spinner("Testing API connection..."):
                    success = test_api_connection(api_key)
                    st.rerun()
            
            if st.session_state.api_tested and st.session_state.api_test_result:
                if st.session_state.api_test_result.startswith("success_with_"):
                    model_name = st.session_state.api_test_result.replace("success_with_", "")
                    st.success(f"✅ API connection successful!\nUsing model: {model_name}")
                elif st.session_state.api_test_result == "no_working_model_found":
                    st.error("❌ No working Gemini model found. Check your API key and quota.")
                elif st.session_state.api_test_result == "empty_response":
                    st.error("❌ API test failed - empty response")
                else:
                    st.error(f"❌ API test failed: {st.session_state.api_test_result}")
                
                if st.button("Clear Test Result", key="clear_test"):
                    st.session_state.api_tested = False
                    st.session_state.api_test_result = None
                    st.rerun()
                    
        else:
            st.warning("⚠️ Please enter your Gemini API key")
            st.markdown("""
            **Get your free API key:**
            1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
            2. Create a new API key
            3. Paste it above
            
            **Supported Models:**
            - gemini-2.0-flash-exp (Latest)
            - gemini-1.5-flash (Recommended)
            - gemini-1.5-pro
            - gemini-1.0-pro
            """)
        
        if st.session_state.phase != 'setup':
            st.divider()
            st.subheader("Progress")
            if st.session_state.phase == 'interview':
                progress = min(1.0, max(0.0, (st.session_state.current_question + 1) / len(st.session_state.questions)))
                st.progress(progress)
                st.write(f"Question {st.session_state.current_question + 1} of {len(st.session_state.questions)}")
            elif st.session_state.phase == 'results':
                st.success("Interview Complete!")
    
    if not api_key:
        st.error("Please configure your Gemini API key in the sidebar to continue.")
        return
    
    try:
        interviewer = AIInterviewer(api_key)
    except Exception as e:
        st.error(f"Error initializing AI Interviewer: {e}")
        return
    
    if st.session_state.phase == 'setup':
        show_setup_phase(interviewer)
    elif st.session_state.phase == 'interview':
        show_interview_phase()
    elif st.session_state.phase == 'results':
        show_results_phase(interviewer)

if __name__ == "__main__":
    main()