"""
Safety service for content moderation using Detoxify and NudeNet.
"""
from detoxify import Detoxify
from nudenet import NudeDetector
from PIL import Image
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class SafetyService:
    """Service for content safety checks."""
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.text_model = None
        self.image_model = None
        
        self.text_toxicity_threshold = 0.7
        self.image_nsfw_threshold = 0.6
    
    def load_text_model(self):
        """Lazy load text toxicity model."""
        if self.text_model is None:
            logger.info("Loading Detoxify model for text safety")
            self.text_model = Detoxify('original', device=self.device)
            logger.info("Detoxify model loaded")
    
    def load_image_model(self):
        """Lazy load image NSFW detection model."""
        if self.image_model is None:
            logger.info("Loading NudeNet model for image safety")
            self.image_model = NudeDetector()
            logger.info("NudeNet model loaded")
    
    def check_text_safety(self, text: str) -> Tuple[bool, Dict]:
        """
        Check if text is safe.
        Returns (is_safe, scores_dict)
        """
        self.load_text_model()
        
        try:
            scores = self.text_model.predict(text)
            
            is_safe = all(score < self.text_toxicity_threshold for score in scores.values())
            
            return is_safe, scores
        except Exception as e:
            logger.error(f"Error checking text safety: {e}")
            return True, {}  # Default to safe on error
    
    def check_image_safety(self, image_path: str) -> Tuple[bool, Dict]:
        """
        Check if image is safe (not NSFW).
        Returns (is_safe, detections_dict)
        """
        self.load_image_model()
        
        try:
            detections = self.image_model.detect(image_path)
            
            nsfw_detected = False
            nsfw_classes = ['EXPOSED_ANUS', 'EXPOSED_BREAST_F', 'EXPOSED_GENITALIA_F', 
                           'EXPOSED_GENITALIA_M', 'EXPOSED_BUTTOCKS']
            
            for detection in detections:
                if detection['class'] in nsfw_classes and detection['score'] > self.image_nsfw_threshold:
                    nsfw_detected = True
                    break
            
            is_safe = not nsfw_detected
            
            return is_safe, {"detections": detections, "nsfw_detected": nsfw_detected}
        except Exception as e:
            logger.error(f"Error checking image safety: {e}")
            return True, {}  # Default to safe on error
    
    def check_image_safety_pil(self, image: Image.Image, temp_path: str) -> Tuple[bool, Dict]:
        """
        Check if PIL image is safe.
        Saves to temp path for NudeNet processing.
        """
        try:
            image.save(temp_path)
            return self.check_image_safety(temp_path)
        except Exception as e:
            logger.error(f"Error checking PIL image safety: {e}")
            return True, {}
