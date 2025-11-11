"""
Prompt composition service for enhancing prompts with brand context.
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PromptComposer:
    """Service for composing enhanced prompts with brand context."""
    
    def __init__(self, retrieval_service):
        self.retrieval_service = retrieval_service
    
    def compose_prompt(
        self,
        user_prompt: str,
        brand_id: Optional[str] = None,
        template_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Compose an enhanced prompt with brand context.
        Returns dict with original_prompt, enhanced_prompt, brand_context.
        """
        base_prompt = template_prompt if template_prompt else user_prompt
        
        brand_context = ""
        if brand_id:
            brand_metadata = self.retrieval_service.get_brand_metadata_dict(brand_id)
            
            if brand_metadata:
                tone = brand_metadata.get('tone_of_voice', '')
                style = brand_metadata.get('visual_style', '')
                colors = brand_metadata.get('color_palette', '')
                communications = brand_metadata.get('brand_communications', '')
                audience = brand_metadata.get('target_audience', '')
                
                enhanced_parts = [base_prompt]
                
                if tone:
                    enhanced_parts.append(f"{tone} tone")
                if style:
                    enhanced_parts.append(f"{style} style")
                if colors:
                    enhanced_parts.append(f"using {colors} colors")
                if communications:
                    enhanced_parts.append(communications)
                if audience:
                    enhanced_parts.append(f"appealing to {audience}")
                
                enhanced_parts.append("professional, high quality, detailed")
                
                enhanced_prompt = ", ".join(enhanced_parts)
                brand_context = f"Brand: {brand_id}\n" + "\n".join([f"{k}: {v}" for k, v in brand_metadata.items()])
            else:
                enhanced_prompt = base_prompt
        else:
            enhanced_prompt = base_prompt
        
        return {
            "original_prompt": user_prompt,
            "base_prompt": base_prompt,
            "enhanced_prompt": enhanced_prompt,
            "brand_context": brand_context
        }
