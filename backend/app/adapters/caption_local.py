"""
Local caption adapter using BLIP for image captioning.
"""
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class LocalCaptionAdapter:
    """Adapter for local BLIP image captioning."""
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.processor = None
        self.model = None
    
    def load_model(self):
        """Lazy load the caption model."""
        if self.model is None:
            logger.info(f"Loading caption model: {self.model_name} on {self.device}")
            self.processor = BlipProcessor.from_pretrained(self.model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
            self.model.to(self.device)
            logger.info("Caption model loaded successfully")
    
    def caption_image(self, image_path: str) -> str:
        """Generate caption for an image."""
        self.load_model()
        
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            outputs = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            logger.error(f"Error captioning image: {e}")
            return ""
    
    def caption_image_pil(self, image: Image.Image) -> str:
        """Generate caption for a PIL image."""
        self.load_model()
        
        try:
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            outputs = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            logger.error(f"Error captioning image: {e}")
            return ""
