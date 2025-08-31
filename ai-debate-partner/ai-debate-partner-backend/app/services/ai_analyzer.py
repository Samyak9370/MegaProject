import openai
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk import pos_tag
from collections import Counter
from typing import Dict, List, Tuple, Optional
import logging
import re
import json
from datetime import datetime
from ..core.config import settings

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

class DebateMetrics:
    """Class to store and calculate various debate metrics"""
    def __init__(self):
        self.word_count = 0
        self.unique_words = 0
        self.avg_word_length = 0.0
        self.sentence_count = 0
        self.filler_word_count = 0
        self.vocabulary_richness = 0.0
        self.grammar_errors = 0
        self.hesitation_count = 0
        self.speaking_rate = 0.0  # words per second
        self.pause_frequency = 0.0  # pauses per minute
        self.timestamp = datetime.utcnow()
        self.transcript = ""

class AIAnalyzer:
    FILLER_WORDS = {
        'uh', 'um', 'er', 'ah', 'like', 'you know', 'i mean', 'so', 'well', 'basically',
        'actually', 'literally', 'honestly', 'right', 'okay', 'ok', 'anyway', 'anyways'
    }
    
    HESITATION_PATTERNS = [
        r'\buh+\b', r'\bum+\b', r'\ber+\b', r'\bah+\b', r'\bhm+\b', r'\bmm+\b'
    ]
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.metrics = DebateMetrics()
        self.session_history = []
        
    def _get_wordnet_pos(self, treebank_tag):
        """Map treebank POS tag to first character used by WordNetLemmatizer"""
        tag = treebank_tag[0].upper()
        tag_dict = {"J": wordnet.ADJ,
                  "N": wordnet.NOUN,
                  "V": wordnet.VERB,
                  "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    async def analyze_speech(self, text: str, audio_duration: Optional[float] = None) -> Dict:
        """
        Perform comprehensive analysis of speech text and audio metrics.
        
        Args:
            text: The transcribed speech text
            audio_duration: Optional duration of the audio in seconds
            
        Returns:
            Dict containing analysis results
        """
        if not text.strip():
            return {"error": "No speech content to analyze"}
            
        # Reset metrics for new analysis
        self.metrics = DebateMetrics()
        self.metrics.transcript = text
        
        # Basic text processing
        sentences = sent_tokenize(text)
        words = [word.lower() for word in word_tokenize(text) if word.isalnum()]
        
        # Calculate basic metrics
        self.metrics.word_count = len(words)
        self.metrics.unique_words = len(set(words))
        self.metrics.avg_word_length = sum(len(word) for word in words) / max(1, self.metrics.word_count)
        self.metrics.sentence_count = len(sentences)
        
        # Analyze speech patterns
        self._analyze_filler_words(words)
        self._analyze_vocabulary(words)
        self._analyze_grammar(text)
        self._analyze_hesitation(text)
        
        # Calculate speaking rate if audio duration is provided
        if audio_duration and audio_duration > 0:
            self.metrics.speaking_rate = self.metrics.word_count / (audio_duration / 60)  # Words per minute
        
        # Get AI feedback
        feedback = await self._get_ai_feedback(text)
        
        # Store this analysis in session history
        self.session_history.append(self.metrics)
        
        return self._format_analysis_results(feedback)
        
    def _analyze_filler_words(self, words: List[str]) -> None:
        """Count filler words in the speech"""
        self.metrics.filler_word_count = sum(1 for word in words if word.lower() in self.FILLER_WORDS)
        
    def _analyze_vocabulary(self, words: List[str]) -> None:
        """Analyze vocabulary richness and complexity"""
        # Calculate type-token ratio (TTR) as a measure of lexical diversity
        if self.metrics.word_count > 0:
            self.metrics.vocabulary_richness = self.metrics.unique_words / self.metrics.word_count
            
        # TODO: Add more sophisticated vocabulary analysis (word frequency, lexical sophistication, etc.)
        
    def _analyze_grammar(self, text: str) -> None:
        """Perform basic grammar analysis"""
        # Simple grammar check - count sentence fragments, run-ons, etc.
        # This is a simplified version - consider using a proper grammar checker
        sentences = sent_tokenize(text)
        self.metrics.grammar_errors = 0
        
        for sent in sentences:
            words = word_tokenize(sent)
            if len(words) < 3:  # Very short sentence might be a fragment
                self.metrics.grammar_errors += 1
                
    def _analyze_hesitation(self, text: str) -> None:
        """Detect hesitation patterns in speech"""
        self.metrics.hesitation_count = 0
        for pattern in self.HESITATION_PATTERNS:
            self.metrics.hesitation_count += len(re.findall(pattern, text.lower()))
            
    def _format_analysis_results(self, feedback: Dict) -> Dict:
        """Format the analysis results into a structured response"""
        return {
            "transcript": self.metrics.transcript,
            "metrics": {
                "word_count": self.metrics.word_count,
                "unique_words": self.metrics.unique_words,
                "vocabulary_richness": round(self.metrics.vocabulary_richness, 3),
                "avg_word_length": round(self.metrics.avg_word_length, 2),
                "sentence_count": self.metrics.sentence_count,
                "filler_word_count": self.metrics.filler_word_count,
                "grammar_errors": self.metrics.grammar_errors,
                "hesitation_count": self.metrics.hesitation_count,
                "speaking_rate": round(self.metrics.speaking_rate, 1) if self.metrics.speaking_rate > 0 else None,
                "overall_score": self._calculate_overall_score()
            },
            "feedback": feedback,
            "timestamp": self.metrics.timestamp.isoformat()
        }
        
    def _calculate_overall_score(self) -> float:
        """Calculate an overall score (0-10) based on various metrics"""
        score = 10.0
        
        # Penalize for filler words (max 2 points)
        filler_penalty = min(2.0, self.metrics.filler_word_count * 0.2)
        score -= filler_penalty
        
        # Penalize for grammar errors (max 3 points)
        grammar_penalty = min(3.0, self.metrics.grammar_errors * 0.5)
        score -= grammar_penalty
        
        # Penalize for hesitation (max 2 points)
        hesitation_penalty = min(2.0, self.metrics.hesitation_count * 0.3)
        score -= hesitation_penalty
        
        # Reward vocabulary richness (max 3 points)
        vocab_bonus = min(3.0, self.metrics.vocabulary_richness * 10)
        score = min(10.0, score + vocab_bonus)
        
        return max(0.0, min(10.0, score))  # Ensure score is between 0 and 10

    async def _get_ai_feedback(self, text: str) -> Dict:
        """
        Get detailed feedback from OpenAI's API with structured analysis
        """
        try:
            prompt = """
            You are a professional debate coach. Analyze the following speech and provide feedback in this JSON format:
            
            {
                "strengths": ["list", "key", "strengths"],
                "areas_for_improvement": ["list", "key", "areas"],
                "specific_feedback": {
                    "grammar": "Detailed feedback on grammar",
                    "vocabulary": "Feedback on word choice and variety",
                    "clarity": "Feedback on clarity and coherence",
                    "persuasiveness": "Feedback on argument strength"
                },
                "suggestions": ["actionable", "suggestions"],
                "overall_rating": 7.5,
                "confidence_score": 0.85
            }
            
            Speech to analyze:
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL or "gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional debate coach. Provide detailed, constructive feedback."},
                    {"role": "user", "content": prompt + text}
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            try:
                feedback = json.loads(response.choices[0].message.content)
                return feedback
            except json.JSONDecodeError:
                logging.error("Failed to parse AI feedback as JSON")
                return {"error": "Failed to parse AI feedback"}
                
        except Exception as e:
            logging.error(f"Error getting AI feedback: {str(e)}")
            return {"error": f"Failed to analyze speech: {str(e)}"}

    def get_session_summary(self) -> Dict:
        """
        Generate a summary of the current session's metrics and feedback
        """
        if not self.session_history:
            return {"error": "No session data available"}
            
        # Calculate averages across all session metrics
        total_words = sum(m.word_count for m in self.session_history)
        total_sentences = sum(m.sentence_count for m in self.session_history)
        total_fillers = sum(m.filler_word_count for m in self.session_history)
        total_hesitations = sum(m.hesitation_count for m in self.session_history)
        
        # Calculate speaking rate (words per minute)
        if len(self.session_history) > 1:
            duration = (self.session_history[-1].timestamp - self.session_history[0].timestamp).total_seconds() / 60
            speaking_rate = total_words / duration if duration > 0 else 0
        else:
            speaking_rate = self.session_history[0].speaking_rate
            
        # Calculate filler word rate (per 100 words)
        filler_rate = (total_fillers / total_words * 100) if total_words > 0 else 0
        
        return {
            "session_duration_minutes": (self.session_history[-1].timestamp - self.session_history[0].timestamp).total_seconds() / 60,
            "total_words": total_words,
            "total_sentences": total_sentences,
            "avg_words_per_minute": round(speaking_rate, 1),
            "total_filler_words": total_fillers,
            "filler_word_rate": round(filler_rate, 1),
            "total_hesitations": total_hesitations,
            "start_time": self.session_history[0].timestamp.isoformat(),
            "end_time": self.session_history[-1].timestamp.isoformat()
        }
        
    def clear_session(self) -> None:
        """Clear the current session data"""
        self.session_history = []
        self.metrics = DebateMetrics()
