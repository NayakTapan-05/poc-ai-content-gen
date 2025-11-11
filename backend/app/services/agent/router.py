"""
Agent router for handling different types of user requests.
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AgentRouter:
    """Router for directing user requests to appropriate handlers."""
    
    def __init__(
        self,
        intent_detector,
        retrieval_service,
        image_generation_service,
        video_generation_service
    ):
        self.intent_detector = intent_detector
        self.retrieval_service = retrieval_service
        self.image_generation_service = image_generation_service
        self.video_generation_service = video_generation_service
    
    async def route(
        self,
        message: str,
        brand_id: Optional[str] = None,
        session_id: Optional[str] = None,
        has_previous_generation: bool = False
    ) -> Dict:
        """
        Route user message to appropriate handler.
        Returns dict with response, media_url, media_type, etc.
        """
        intent_result = self.intent_detector.detect_intent(message, has_previous_generation)
        intent = intent_result['intent']
        
        logger.info(f"Detected intent: {intent} (confidence: {intent_result['confidence']:.2f})")
        
        if intent == "qa":
            return await self._handle_qa(message, brand_id)
        elif intent == "generate_image":
            return await self._handle_generate_image(message, brand_id)
        elif intent == "generate_video":
            return await self._handle_generate_video(message, brand_id)
        elif intent == "refine":
            return await self._handle_generate_image(message, brand_id)
        else:
            return {
                "status": "error",
                "error": "Unable to determine intent",
                "content": "I'm not sure what you'd like me to do. Could you please clarify?"
            }
    
    async def _handle_qa(self, message: str, brand_id: Optional[str]) -> Dict:
        """Handle Q&A requests."""
        if not brand_id:
            return {
                "status": "success",
                "content": "I can help you generate images and videos. Please select a brand or describe what you'd like to create.",
                "intent": "qa"
            }
        
        context = self.retrieval_service.get_brand_context(brand_id, message, top_k=3)
        
        if not context:
            return {
                "status": "success",
                "content": f"I don't have specific information about that for {brand_id}. However, I can help you generate brand-compliant images and videos.",
                "intent": "qa"
            }
        
        response = f"Based on {brand_id}'s brand guidelines:\n\n{context}\n\nWould you like me to generate content based on these guidelines?"
        
        return {
            "status": "success",
            "content": response,
            "intent": "qa",
            "brand_context": context
        }
    
    async def _handle_generate_image(self, message: str, brand_id: Optional[str]) -> Dict:
        """Handle image generation requests."""
        result = await self.image_generation_service.generate(
            user_prompt=message,
            brand_id=brand_id
        )
        
        if result['status'] != 'success':
            return result
        
        return {
            "status": "success",
            "content": f"Generated image: {message[:50]}...",
            "media_url": f"/media/{result['filename']}",
            "media_type": "image",
            "filename": result['filename'],
            "intent": "generate_image",
            "metadata": {
                "original_prompt": result.get('original_prompt', ''),
                "enhanced_prompt": result.get('enhanced_prompt', ''),
                "caption": result.get('caption', '')
            }
        }
    
    async def _handle_generate_video(self, message: str, brand_id: Optional[str]) -> Dict:
        """Handle video generation requests."""
        result = await self.video_generation_service.generate(
            user_prompt=message,
            brand_id=brand_id
        )
        
        if result['status'] != 'success':
            return result
        
        return {
            "status": "success",
            "content": f"Generated video: {message[:50]}...",
            "media_url": f"/media/{result['filename']}",
            "media_type": "video",
            "filename": result['filename'],
            "intent": "generate_video",
            "metadata": {
                "original_prompt": result.get('original_prompt', ''),
                "enhanced_prompt": result.get('enhanced_prompt', ''),
                "num_frames": result.get('num_frames', 0)
            }
        }
