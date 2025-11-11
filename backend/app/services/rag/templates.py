"""
Template service for content generation templates.
"""
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for managing content generation templates."""
    
    def __init__(self):
        self.templates = {
            "product_showcase": {
                "id": "product_showcase",
                "name": "Product Showcase",
                "description": "Highlight a product with professional photography",
                "type": "image",
                "fields": [
                    {"name": "product_name", "label": "Product Name", "type": "text", "required": True},
                    {"name": "setting", "label": "Setting/Background", "type": "text", "required": False},
                    {"name": "mood", "label": "Mood/Atmosphere", "type": "text", "required": False}
                ],
                "prompt_template": "Professional product photography of {product_name}, {setting}, {mood}, high quality, detailed, 8k resolution"
            },
            "lifestyle_image": {
                "id": "lifestyle_image",
                "name": "Lifestyle Image",
                "description": "Create lifestyle imagery with people and products",
                "type": "image",
                "fields": [
                    {"name": "scene", "label": "Scene Description", "type": "text", "required": True},
                    {"name": "people", "label": "People Description", "type": "text", "required": False},
                    {"name": "activity", "label": "Activity", "type": "text", "required": False}
                ],
                "prompt_template": "{scene} with {people} {activity}, natural lighting, authentic, lifestyle photography"
            },
            "brand_campaign": {
                "id": "brand_campaign",
                "name": "Brand Campaign",
                "description": "Generate brand campaign visuals",
                "type": "image",
                "fields": [
                    {"name": "message", "label": "Campaign Message", "type": "text", "required": True},
                    {"name": "visual_style", "label": "Visual Style", "type": "text", "required": False}
                ],
                "prompt_template": "Brand campaign visual: {message}, {visual_style}, professional, high impact"
            },
            "product_video": {
                "id": "product_video",
                "name": "Product Video",
                "description": "Create a short product demonstration video",
                "type": "video",
                "fields": [
                    {"name": "product_name", "label": "Product Name", "type": "text", "required": True},
                    {"name": "action", "label": "Action/Movement", "type": "text", "required": False}
                ],
                "prompt_template": "Product video of {product_name}, {action}, smooth motion, professional"
            },
            "lifestyle_video": {
                "id": "lifestyle_video",
                "name": "Lifestyle Video",
                "description": "Create lifestyle video content",
                "type": "video",
                "fields": [
                    {"name": "scene", "label": "Scene Description", "type": "text", "required": True},
                    {"name": "mood", "label": "Mood/Feeling", "type": "text", "required": False}
                ],
                "prompt_template": "Lifestyle video: {scene}, {mood}, natural, authentic, cinematic"
            }
        }
    
    def list_templates(self, content_type: Optional[str] = None) -> List[Dict]:
        """
        List all templates, optionally filtered by type.
        """
        templates = list(self.templates.values())
        
        if content_type:
            templates = [t for t in templates if t['type'] == content_type]
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get a specific template by ID."""
        return self.templates.get(template_id)
    
    def fill_template(self, template_id: str, fields: Dict[str, str]) -> str:
        """
        Fill a template with provided field values.
        Returns the filled prompt.
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        prompt_template = template['prompt_template']
        
        filled_prompt = prompt_template
        for field in template['fields']:
            field_name = field['name']
            field_value = fields.get(field_name, '')
            
            if field['required'] and not field_value:
                raise ValueError(f"Required field missing: {field_name}")
            
            filled_prompt = filled_prompt.replace(f"{{{field_name}}}", field_value)
        
        import re
        filled_prompt = re.sub(r'\s*\{\w+\}\s*', ' ', filled_prompt)
        filled_prompt = re.sub(r'\s+', ' ', filled_prompt).strip()
        
        return filled_prompt
