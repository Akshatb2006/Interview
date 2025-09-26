import streamlit as st
import time

def show_setup_phase(interviewer):
    """Setup phase - collect candidate info and generate questions"""
    st.title("🤖 AI Interviewer - SDE Intern Role")
    
    st.markdown("""
    ### Welcome to your AI Interview!
    
    Hi! I'm your AI interviewer for the Software Development Engineer Intern position. 
    This interview will include 6 questions covering technical knowledge, problem-solving, and behavioral aspects.
    
    **What to expect:**
    - 6 personalized questions (3 Technical, 2 Problem-Solving, 1 Behavioral)
    - 3 minutes per question
    - Immediate evaluation and feedback
    """)
    
    with st.form("candidate_setup"):
        st.subheader("Candidate Information")
        
        name = st.text_input("Full Name *", placeholder="Enter your full name")
        background = st.text_area(
            "Programming Background (Optional)", 
            placeholder="Brief description of your programming experience, languages, projects...",
            height=100
        )
        
        submitted = st.form_submit_button("Start Interview", use_container_width=True)
        
        if submitted:
            if not name.strip():
                st.error("Please enter your name to continue.")
                return
            
            st.session_state.candidate_name = name.strip()
            
            with st.spinner("Generating personalized questions..."):
                try:
                    questions = interviewer.generate_questions(background)
                    st.session_state.questions = questions
                    st.session_state.phase = 'interview'
                    st.session_state.start_time = time.time()
                    st.session_state.question_start_time = time.time()
                    st.success("Questions generated! Starting interview...")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate questions: {e}")
                    st.info("Using sample questions instead...")
                    questions = interviewer._get_fallback_questions()
                    st.session_state.questions = questions
                    st.session_state.phase = 'interview'
                    st.session_state.start_time = time.time()
                    st.session_state.question_start_time = time.time()
                    st.rerun()
        
        col1, col2 = st.columns(2)
        with col2:
            if st.form_submit_button("🚀 Use Sample Questions", use_container_width=True):
                if not name.strip():
                    st.error("Please enter your name to continue.")
                    return
                
                st.session_state.candidate_name = name.strip()
                questions = interviewer._get_fallback_questions()
                st.session_state.questions = questions
                st.session_state.phase = 'interview'
                st.session_state.start_time = time.time()
                st.session_state.question_start_time = time.time()
                st.success("Using sample questions! Starting interview...")
                time.sleep(1)
                st.rerun()