import streamlit as st
import time
from models.data_models import Response

def show_interview_phase():
    """Interview phase - ask questions and collect responses"""
    current_q_idx = st.session_state.current_question
    questions = st.session_state.questions
    
    if current_q_idx >= len(questions):
        st.session_state.phase = 'results'
        st.rerun()
        return
    
    current_question = questions[current_q_idx]
    
    progress = min(1.0, max(0.0, (current_q_idx + 1) / len(questions)))
    st.progress(progress, text=f"Question {current_q_idx + 1} of {len(questions)}")
    
    # Timer
    if st.session_state.question_start_time:
        elapsed = time.time() - st.session_state.question_start_time
        remaining = max(0, 180 - elapsed)  
        
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        
        if remaining > 60:
            st.success(f"⏰ Time remaining: {mins}:{secs:02d}")
        elif remaining > 30:
            st.warning(f"⏰ Time remaining: {mins}:{secs:02d}")
        elif remaining > 0:
            st.error(f"⏰ Time remaining: {mins}:{secs:02d}")
        else:
            st.error("⏰ Time's up!")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Question {current_q_idx + 1}")
    with col2:
        category_colors = {
            'Technical': '🔧',
            'Problem-Solving': '🧩', 
            'Behavioral': '👥'
        }
        st.info(f"{category_colors.get(current_question.category, '❓')} {current_question.category}")
    
    st.markdown(f"**{current_question.text}**")
    
    answer = st.text_area(
        "Your Answer:",
        placeholder="Type your detailed response here...",
        height=200,
        key=f"answer_{current_q_idx}"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_q_idx > 0:
            if st.button("← Previous", use_container_width=True):
                save_current_response(answer, current_question)
                st.session_state.current_question -= 1
                st.session_state.question_start_time = time.time()
                st.rerun()
    
    with col2:
        if 'remaining' in locals() and remaining <= 0:
            st.error("Time expired!")
            if st.button("Auto-Submit", use_container_width=True):
                submit_response(answer or "No response provided (time expired)", current_question)
    
    with col3:
        if current_q_idx < len(questions) - 1:
            if st.button("Next →", use_container_width=True):
                if not answer.strip():
                    st.error("Please provide an answer before proceeding.")
                else:
                    submit_response(answer, current_question)
        else:
            if st.button("Finish Interview", use_container_width=True):
                if not answer.strip():
                    st.error("Please provide an answer before finishing.")
                else:
                    submit_response(answer, current_question)
                    st.session_state.phase = 'results'
                    st.rerun()

def save_current_response(answer, question):
    """Save current response without advancing"""
    if answer.strip():
        time_taken = time.time() - st.session_state.question_start_time
        response = Response(
            question_id=question.id,
            question=question.text,
            category=question.category,
            answer=answer.strip(),
            time_taken=time_taken
        )
        
        existing_idx = None
        for i, r in enumerate(st.session_state.responses):
            if r.question_id == question.id:
                existing_idx = i
                break
        
        if existing_idx is not None:
            st.session_state.responses[existing_idx] = response
        else:
            st.session_state.responses.append(response)

def submit_response(answer, question):
    """Submit response and advance to next question"""
    time_taken = time.time() - st.session_state.question_start_time
    
    response = Response(
        question_id=question.id,
        question=question.text,
        category=question.category,
        answer=answer.strip() or "No response provided",
        time_taken=time_taken
    )
    
    existing_idx = None
    for i, r in enumerate(st.session_state.responses):
        if r.question_id == question.id:
            existing_idx = i
            break
    
    if existing_idx is not None:
        st.session_state.responses[existing_idx] = response
    else:
        st.session_state.responses.append(response)
    
    st.session_state.current_question += 1
    st.session_state.question_start_time = time.time()
    st.rerun()