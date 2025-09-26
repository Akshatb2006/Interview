import streamlit as st
from datetime import datetime
from utils.report_utils import generate_report

def show_results_phase(interviewer):
    """Results phase - show evaluation and feedback"""
    st.title("📊 Interview Results")
    
    if not st.session_state.responses:
        st.error("No responses found. Please restart the interview.")
        return
    
    with st.spinner("Analyzing your responses..."):
        evaluation = interviewer.evaluate_responses(st.session_state.responses)
    
    overall_score = evaluation.get('overall_score', 0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if overall_score >= 85:
            st.success(f"🌟 **Overall Score: {overall_score}/100**")
        elif overall_score >= 75:
            st.info(f"👍 **Overall Score: {overall_score}/100**")
        elif overall_score >= 65:
            st.warning(f"⚡ **Overall Score: {overall_score}/100**")
        else:
            st.error(f"📚 **Overall Score: {overall_score}/100**")
    
    st.subheader("Performance Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scores = {
            "🔧 Technical Knowledge": evaluation.get('technical_score', 0),
            "💬 Communication": evaluation.get('communication_score', 0),
            "🧩 Problem Solving": evaluation.get('problem_solving_score', 0),
            "👥 Behavioral Fit": evaluation.get('behavioral_score', 0)
        }
        
        for label, score in scores.items():
            if score >= 80:
                st.success(f"{label}: {score}/100")
            elif score >= 70:
                st.info(f"{label}: {score}/100")
            elif score >= 60:
                st.warning(f"{label}: {score}/100")
            else:
                st.error(f"{label}: {score}/100")
    
    with col2:
        recommendation = evaluation.get('recommendation', 'Under Review')
        st.subheader("Recommendation")
        
        if recommendation in ['Strong Hire', 'Hire']:
            st.success(f"✅ **{recommendation}**")
        elif recommendation == 'Conditional Hire':
            st.warning(f"⚠️ **{recommendation}**")
        else:
            st.error(f"❌ **{recommendation}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Strengths")
        strengths = evaluation.get('strengths', [])
        for strength in strengths:
            st.write(f"✅ {strength}")
    
    with col2:
        st.subheader("Areas for Improvement")
        improvements = evaluation.get('improvements', [])
        for improvement in improvements:
            st.write(f"🎯 {improvement}")
    
    st.subheader("Detailed Feedback")
    feedback = evaluation.get('detailed_feedback', 'No detailed feedback available.')
    st.write(feedback)
    
    st.subheader("Interview Statistics")
    total_time = sum(r.time_taken for r in st.session_state.responses)
    avg_time = total_time / len(st.session_state.responses)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Time", f"{int(total_time//60)}m {int(total_time%60)}s")
    with col2:
        st.metric("Average per Question", f"{int(avg_time//60)}m {int(avg_time%60)}s")
    with col3:
        st.metric("Questions Completed", f"{len(st.session_state.responses)}/6")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Report", use_container_width=True):
            report = generate_report(evaluation, st.session_state.responses)
            st.download_button(
                label="Download Full Report",
                data=report,
                file_name=f"Interview_Report_{st.session_state.candidate_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("🔄 New Interview", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()