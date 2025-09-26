import google.generativeai as genai
import json
import streamlit as st
from typing import List, Dict
from models.data_models import Question, Response

class AIInterviewer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Updated model names based on current Gemini API documentation (September 2025)
        model_names = [
            # Latest and most capable models
            'gemini-2.5-pro',                    # Most powerful thinking model
            'gemini-2.5-flash',                  # Best price-performance model
            'gemini-2.5-flash-lite',             # Cost-efficient model
            
            # Gemini 2.0 models  
            'gemini-2.0-flash',                  # Next-gen features
            'gemini-2.0-flash-lite',             # Cost-efficient 2.0
            
            # Gemini 1.5 models (deprecated but still available)
            'gemini-1.5-flash',                  # Fast and versatile
            'gemini-1.5-flash-8b',               # Smaller model (deprecated)
            'gemini-1.5-pro',                    # Advanced reasoning (deprecated)
            
            # Alternative naming patterns (with models/ prefix)
            'models/gemini-2.5-pro',
            'models/gemini-2.5-flash', 
            'models/gemini-2.5-flash-lite',
            'models/gemini-2.0-flash',
            'models/gemini-2.0-flash-lite',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-flash-8b',
            'models/gemini-1.5-pro'
        ]
        
        self.model = None
        self.model_name = None
        last_error = None
        
        # Try models in order of preference (newest/best first)
        for model_name in model_names:
            try:
                st.info(f"🔄 Trying model: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                
                # Test with a simple request
                test_response = self.model.generate_content(
                    "Respond with 'OK' if you can see this message.", 
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=10,
                        temperature=0.1
                    ),
                    request_options={'timeout': 15}  # Increased timeout
                )
                
                if test_response and test_response.text:
                    self.model_name = model_name
                    st.success(f"✅ Successfully connected with: {model_name}")
                    break
                else:
                    st.warning(f"⚠️ Empty response from: {model_name}")
                    continue
                    
            except Exception as e:
                last_error = e
                st.warning(f"❌ Failed with {model_name}: {str(e)[:100]}...")
                continue
        
        if self.model is None:
            error_msg = f"No working Gemini model found. Last error: {last_error}"
            st.error(error_msg)
            raise Exception(error_msg)
        
        print(f"Successfully initialized with model: {self.model_name}")
    
    def generate_questions(self, candidate_background: str = "") -> List[Question]:
        """Generate personalized interview questions using Gemini"""
        prompt = f"""
        Generate exactly 6 interview questions for a Software Development Engineer Intern position.
        
        Candidate background: {candidate_background}
        
        Requirements:
        - 3 Technical questions (data structures, algorithms, programming concepts)
        - 2 Problem-solving questions (debugging, system design, analytical thinking)
        - 1 Behavioral question (experience, motivation, challenges)
        - Questions should be intern-level appropriate
        - Mix of Easy (2), Medium (3), Hard (1) difficulty
        
        Return ONLY a valid JSON array with this exact structure:
        [
            {{
                "id": 1,
                "text": "Question text here",
                "category": "Technical",
                "difficulty": "Easy"
            }},
            {{
                "id": 2,
                "text": "Question text here", 
                "category": "Technical",
                "difficulty": "Medium"
            }}
        ]
        
        Do not include any other text, explanations, or markdown formatting.
        """
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2500,  # Increased for better responses
                top_p=0.9
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                request_options={'timeout': 45}  # Increased timeout
            )
            
            if not response or not response.text:
                st.warning("Empty response from AI. Using fallback questions.")
                return self._get_fallback_questions()
            
            response_text = response.text.strip()
            
            # Clean up response text - remove markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            # Find JSON array boundaries
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                
                try:
                    questions_data = json.loads(json_str)
                except json.JSONDecodeError as je:
                    st.error(f"JSON parsing error: {je}")
                    st.error(f"Raw response: {response_text[:500]}...")
                    return self._get_fallback_questions()
                
                if not isinstance(questions_data, list):
                    st.warning("AI response is not a JSON array. Using fallback questions.")
                    return self._get_fallback_questions()
                
                if len(questions_data) < 6:
                    st.warning(f"AI generated only {len(questions_data)} questions instead of 6. Using fallback questions.")
                    return self._get_fallback_questions()
                
                questions = []
                for i, q_data in enumerate(questions_data[:6]):
                    if not isinstance(q_data, dict):
                        st.warning("Invalid question format in AI response. Using fallback questions.")
                        return self._get_fallback_questions()
                        
                    question = Question(
                        id=i + 1,
                        text=q_data.get('text', '').strip(),
                        category=q_data.get('category', 'Technical'),
                        difficulty=q_data.get('difficulty', 'Medium')
                    )
                    
                    if question.text:
                        questions.append(question)
                
                if len(questions) >= 6:
                    st.success(f"Generated {len(questions)} personalized questions!")
                    return questions[:6]
                else:
                    st.warning("AI generated incomplete questions. Using fallback questions.")
                    return self._get_fallback_questions()
            else:
                st.warning("Could not find JSON array in AI response. Using fallback questions.")
                st.error(f"Raw response: {response_text[:500]}...")
                return self._get_fallback_questions()
                
        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return self._get_fallback_questions()
    
    def _get_fallback_questions(self) -> List[Question]:
        """High-quality fallback questions if AI generation fails"""
        return [
            Question(1, "Explain the difference between an array and a linked list. When would you use each data structure?", "Technical", "Medium"),
            Question(2, "What is time complexity (Big O notation)? Calculate the time complexity of searching through a 2D array using nested loops.", "Technical", "Easy"),
            Question(3, "You're debugging a web application that takes 30 seconds to load. Walk me through your debugging process step by step.", "Problem-Solving", "Medium"),
            Question(4, "Design a basic real-time chat application. What main components and technologies would you need? Consider scalability for 1000+ users.", "Problem-Solving", "Hard"),
            Question(5, "Describe a challenging coding project you worked on. What obstacles did you face and how did you overcome them?", "Behavioral", "Medium"),
            Question(6, "What's the difference between SQL and NoSQL databases? Give an example of when you'd use each.", "Technical", "Easy")
        ]
    
    def evaluate_responses(self, responses: List[Response]) -> Dict:
        """Evaluate all responses and generate comprehensive feedback"""
        
        if not responses:
            return self._basic_evaluation([])
        
        responses_text = ""
        for i, r in enumerate(responses, 1):
            responses_text += f"""
Question {i}: {r.question} 
Category: {r.category}
Answer: {r.answer}
Time taken: {r.time_taken:.1f} seconds
---
"""
        
        prompt = f"""
        Evaluate this SDE intern interview based on the following responses:
        
        {responses_text}
        
        Provide evaluation in this EXACT JSON format (no additional text):
        {{
            "technical_score": 75,
            "communication_score": 80, 
            "problem_solving_score": 70,
            "behavioral_score": 85,
            "overall_score": 78,
            "strengths": ["Clear explanations", "Good examples", "Structured thinking"],
            "improvements": ["More technical depth needed", "Consider edge cases"],
            "detailed_feedback": "Comprehensive paragraph about performance and potential...",
            "recommendation": "Conditional Hire"
        }}
        
        Scoring criteria (0-100):
        - Technical: Accuracy, depth, proper terminology, understanding of concepts
        - Communication: Clarity, structure, completeness of explanations
        - Problem-solving: Logical approach, creativity, systematic methodology
        - Behavioral: Relevant examples, self-awareness, cultural fit, growth mindset
        
        Recommendation options: "Strong Hire", "Hire", "Conditional Hire", "Hold", "No Hire"
        
        Be fair but thorough for intern-level expectations. Consider this is an entry-level position.
        """
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.3,  # Lower temperature for more consistent evaluation
                max_output_tokens=1500,
                top_p=0.8
            )
            
            response = self.model.generate_content(
                prompt, 
                generation_config=generation_config,
                request_options={'timeout': 30}
            )
            
            if not response or not response.text:
                st.warning("Empty evaluation response. Using basic evaluation.")
                return self._basic_evaluation(responses)
            
            response_text = response.text.strip()
            
            # Clean up response text
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            # Find JSON boundaries
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                
                try:
                    evaluation = json.loads(json_str)
                except json.JSONDecodeError as je:
                    st.error(f"Evaluation JSON parsing error: {je}")
                    return self._basic_evaluation(responses)
                
                # Validate and clamp scores
                score_keys = ['technical_score', 'communication_score', 'problem_solving_score', 'behavioral_score', 'overall_score']
                for key in score_keys:
                    if key in evaluation:
                        evaluation[key] = max(0, min(100, int(evaluation.get(key, 0))))
                
                # Ensure required fields exist
                if 'strengths' not in evaluation:
                    evaluation['strengths'] = ["Completed all questions"]
                if 'improvements' not in evaluation:
                    evaluation['improvements'] = ["Continue learning and practicing"]
                if 'detailed_feedback' not in evaluation:
                    evaluation['detailed_feedback'] = "Candidate completed the interview process."
                if 'recommendation' not in evaluation:
                    evaluation['recommendation'] = "Under Review"
                
                return evaluation
            else:
                st.warning("Could not parse evaluation JSON. Using basic evaluation.")
                return self._basic_evaluation(responses)
                
        except Exception as e:
            st.error(f"Evaluation error: {e}")
            return self._basic_evaluation(responses)
    
    def _basic_evaluation(self, responses: List[Response]) -> Dict:
        """Enhanced basic evaluation if AI evaluation fails"""
        if not responses:
            base_score = 50
        else:
            # More sophisticated basic scoring
            avg_length = sum(len(r.answer) for r in responses) / len(responses)
            avg_time = sum(r.time_taken for r in responses) / len(responses)
            
            # Score based on response quality indicators
            length_score = min(100, max(30, avg_length / 15))  # Longer responses generally better
            time_score = 100 if 30 <= avg_time <= 150 else 70  # Good time management
            completion_score = (len(responses) / 6) * 100  # Completion rate
            
            base_score = int((length_score + time_score + completion_score) / 3)
        
        return {
            "technical_score": max(40, base_score - 5),
            "communication_score": max(45, base_score),
            "problem_solving_score": max(35, base_score - 10),
            "behavioral_score": max(50, base_score + 5),
            "overall_score": base_score,
            "strengths": [
                "Completed the interview process",
                "Engaged with all questions",
                "Showed up and participated"
            ],
            "improvements": [
                "Could provide more detailed technical explanations",
                "Practice explaining complex concepts clearly",
                "Consider providing specific examples"
            ],
            "detailed_feedback": f"Candidate participated in the full interview process with an overall performance score of {base_score}/100. This basic evaluation was generated due to AI evaluation system limitations. The candidate showed engagement and completed all required questions within the allotted time frame.",
            "recommendation": "Conditional Hire" if base_score >= 60 else "Hold"
        }