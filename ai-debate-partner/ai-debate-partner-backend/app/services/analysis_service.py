import openai
from typing import List, Dict, Any
from ..core.config import settings
from ..models.schemas import Feedback, AnalysisType
import json

class AnalysisService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.system_prompt = """You are an expert debate coach and public speaking analyst. 
        Analyze the provided debate transcript and provide detailed feedback on the following aspects:
        1. Grammar and sentence structure
        2. Vocabulary and word choice
        3. Confidence and clarity of expression
        4. Overall fluency and coherence
        
        Provide specific examples from the text and suggest improvements where necessary."""
    
    async def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """Analyze the transcript and return feedback."""
        try:
            # Call OpenAI API for analysis
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Please analyze this debate transcript:\n\n{transcript}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the response
            analysis = response.choices[0].message.content
            
            # Generate structured feedback
            feedback = self._generate_structured_feedback(analysis, transcript)
            
            return {
                "transcript": transcript,
                "analysis": analysis,
                "feedback": feedback
            }
            
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _generate_structured_feedback(self, analysis: str, transcript: str) -> List[Dict]:
        """Convert the analysis into structured feedback items."""
        # This is a simplified version - in a real app, you'd want to parse the AI's response
        # more carefully to extract specific scores and feedback for each category
        
        # For now, we'll return a basic structure with placeholder values
        return [
            {
                "type": "grammar",
                "score": 8.5,
                "feedback": "Good grammar overall, but watch out for subject-verb agreement in complex sentences.",
                "suggestions": [
                    "Review subject-verb agreement rules",
                    "Consider varying your sentence structure"
                ]
            },
            {
                "type": "vocabulary",
                "score": 7.8,
                "feedback": "Good use of debate terminology, but could benefit from more advanced vocabulary.",
                "suggestions": [
                    "Learn 5 new debate-related terms this week",
                    "Practice using synonyms for common words"
                ]
            },
            {
                "type": "confidence",
                "score": 9.0,
                "feedback": "You speak with good confidence and clarity.",
                "suggestions": [
                    "Work on maintaining consistent volume throughout your speech"
                ]
            },
            {
                "type": "fluency",
                "score": 8.2,
                "feedback": "Good flow between points. Some hesitation could be reduced with more practice.",
                "suggestions": [
                    "Practice speaking without fillers (um, uh, like)",
                    "Work on smoother transitions between points"
                ]
            },
            {
                "type": "overall",
                "score": 8.4,
                "feedback": "Strong performance overall with good structure and argumentation.",
                "suggestions": [
                    "Continue practicing to reduce filler words",
                    "Work on expanding your vocabulary further"
                ]
            }
        ]
        
    def _calculate_scores(self, analysis: str) -> Dict[str, float]:
        """Calculate scores based on the analysis."""
        # In a real implementation, you would parse the analysis to extract scores
        # For now, we'll return placeholder values
        return {
            "grammar": 8.5,
            "vocabulary": 7.8,
            "confidence": 9.0,
            "fluency": 8.2,
            "overall": 8.4
        }

# Create a singleton instance
analysis_service = AnalysisService()
