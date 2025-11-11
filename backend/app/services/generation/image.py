"""
Image generation service with safety checks and watermarking.
"""
from typing import Dict, Optional
import logging
from pathlib import Path

from app import config

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Service for generating images with safety checks."""
    
    def __init__(self, image_provider, safety_service, caption_service, prompt_composer):
        self.image_provider = image_provider
        self.safety_service = safety_service
        self.caption_service = caption_service
        self.prompt_composer = prompt_composer
    
    async def generate(
        self,
        user_prompt: str,
        brand_id: Optional[str] = None,
        template_prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        seed: Optional[int] = None
    ) -> Dict:
        """
        Generate an image with safety checks.
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
        
        if width is None:
            width = config.IMAGE_SIZE
        if height is None:
            height = config.IMAGE_SIZE
        if num_inference_steps is None:
            num_inference_steps = config.IMAGE_STEPS
        if guidance_scale is None:
            guidance_scale = config.IMAGE_GUIDANCE_SCALE
        
        logger.info(f"Generating image: {enhanced_prompt[:50]}...")
        result = self.image_provider.generate_image(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height,
            seed=seed
        )
        
        if result['status'] != 'success':
            return result
        
        if config.ENABLE_SAFETY_CHECKS:
            image_safe, image_detections = self.safety_service.check_image_safety(result['filepath'])
            if not image_safe:
                logger.warning(f"Unsafe image detected: {image_detections}")
                Path(result['filepath']).unlink(missing_ok=True)
                return {
                    "status": "error",
                    "error": "Generated image flagged as potentially unsafe",
                    "safety_checks": {"image_safe": False, "image_detections": image_detections}
                }
        
        caption = ""
        if config.ENABLE_SAFETY_CHECKS:
            try:
                caption = self.caption_service.caption_image(result['filepath'])
                logger.info(f"Generated caption: {caption}")
            except Exception as e:
                logger.error(f"Error generating caption: {e}")
        
        result.update({
            "original_prompt": prompt_result['original_prompt'],
            "enhanced_prompt": enhanced_prompt,
            "brand_context": prompt_result.get('brand_context', ''),
            "caption": caption,
            "safety_checks": {
                "text_safe": True,
                "image_safe": True
            }
        })
        
        return result
