"""
Intent detection service for routing user requests.
"""
from typing import Dict, Literal
import logging

logger = logging.getLogger(__name__)

IntentType = Literal["qa", "generate_image", "generate_video", "refine", "unknown"]


class IntentDetector:
    """Service for detecting user intent from messages."""
    
    def __init__(self):
        self.qa_keywords = [
            "what", "how", "why", "when", "where", "who", "explain", "tell me",
            "describe", "define", "meaning", "information", "about"
        ]
        
        self.image_keywords = [
            "image", "picture", "photo", "poster", "banner", "visual", "graphic",
            "illustration", "render", "artwork"
        ]
        
        self.video_keywords = [
            "video", "clip", "animate", "animation", "footage", "movie", "motion",
            "frames", "sequence"
        ]
        
        self.refine_keywords = [
            "change", "modify", "adjust", "update", "improve", "enhance", "fix",
            "make it", "can you", "different", "another", "redo"
        ]
        
        self.generate_keywords = [
            "create", "generate", "make", "produce", "design", "build", "show me"
        ]
    
    def detect_intent(self, message: str, has_previous_generation: bool = False) -> Dict:
        """
        Detect intent from user message.
        Returns dict with intent type and confidence.
        """
        message_lower = message.lower()
        
        if has_previous_generation:
            refine_score = sum(1 for kw in self.refine_keywords if kw in message_lower)
            if refine_score > 0:
                return {
                    "intent": "refine",
                    "confidence": min(refine_score / len(self.refine_keywords), 1.0),
                    "reasoning": "User wants to refine previous generation"
                }
        
        qa_score = sum(1 for kw in self.qa_keywords if kw in message_lower)
        
        image_score = sum(1 for kw in self.image_keywords if kw in message_lower)
        video_score = sum(1 for kw in self.video_keywords if kw in message_lower)
        generate_score = sum(1 for kw in self.generate_keywords if kw in message_lower)
        
        if video_score > 0 and video_score >= image_score:
            return {
                "intent": "generate_video",
                "confidence": min((video_score + generate_score) / 5, 1.0),
                "reasoning": "User wants to generate a video"
            }
        elif image_score > 0 or generate_score > 0:
            return {
                "intent": "generate_image",
                "confidence": min((image_score + generate_score) / 5, 1.0),
                "reasoning": "User wants to generate an image"
            }
        elif qa_score > 0:
            return {
                "intent": "qa",
                "confidence": min(qa_score / len(self.qa_keywords), 1.0),
                "reasoning": "User is asking a question"
            }
        else:
            return {
                "intent": "generate_image",
                "confidence": 0.5,
                "reasoning": "Default to image generation"
            }
