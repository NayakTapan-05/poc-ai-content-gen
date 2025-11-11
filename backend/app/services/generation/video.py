"""
Video generation service with safety checks.
"""
from typing import Dict, Optional
import logging
from pathlib import Path

from app import config

logger = logging.getLogger(__name__)


class VideoGenerationService:
    """Service for generating videos with safety checks."""
    
    def __init__(self, video_provider, safety_service, prompt_composer):
        self.video_provider = video_provider
        self.safety_service = safety_service
        self.prompt_composer = prompt_composer
    
    async def generate(
        self,
        user_prompt: str,
        brand_id: Optional[str] = None,
        template_prompt: Optional[str] = None,
        num_frames: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        fps: Optional[int] = None,
        seed: Optional[int] = None
    ) -> Dict:
        """
        Generate a video with safety checks.
        Returns dict with status, filepath, filename, safety_checks, etc.
        """
        if config.ENABLE_SAFETY_CHECKS:
            text_safe, text_scores = self.safety_service.check_text_safety(user_prompt)
            if not text_safe:
                logger.warning(f"Unsafe text detected: {text_scores}")
                return {
                    "status": "error",
                    "error": "Text content flagged as potentially unsafe",
                    "safety_checks": {"text_safe": False, "text_scores": text_scores}
                }
        
        prompt_result = self.prompt_composer.compose_prompt(
            user_prompt=user_prompt,
            brand_id=brand_id,
            template_prompt=template_prompt
        )
        
        enhanced_prompt = prompt_result['enhanced_prompt']
        
        if num_frames is None:
            num_frames = config.VIDEO_FRAMES
        if num_inference_steps is None:
            num_inference_steps = config.VIDEO_STEPS
        if fps is None:
            fps = config.VIDEO_FPS
        
        logger.info(f"Generating video: {enhanced_prompt[:50]}...")
        result = self.video_provider.generate_video(
            prompt=enhanced_prompt,
            num_frames=num_frames,
            num_inference_steps=num_inference_steps,
            fps=fps,
            seed=seed
        )
        
        if result['status'] != 'success':
            return result
        
        result.update({
            "original_prompt": prompt_result['original_prompt'],
            "enhanced_prompt": enhanced_prompt,
            "brand_context": prompt_result.get('brand_context', ''),
            "safety_checks": {
                "text_safe": True
            }
        })
        
        return result
