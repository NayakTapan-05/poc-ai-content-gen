import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image
import os
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class ImageGeneratorService:
    def __init__(self, output_dir: str = "./data/generated_content"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        self.pipeline = None
        self.model_loaded = False
    
    def load_model(self):
        """
        Load Stable Diffusion XL model.
        This is done lazily to avoid loading the model on startup.
        """
        if self.model_loaded:
            return
        
        logger.info("Loading Stable Diffusion XL model...")
        
        try:
            self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True,
                variant="fp16" if self.device == "cuda" else None
            )
            
            self.pipeline = self.pipeline.to(self.device)
            
            if self.device == "cuda":
                self.pipeline.enable_model_cpu_offload()
            
            self.model_loaded = True
            logger.info("Stable Diffusion XL model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Stable Diffusion XL model: {e}")
            raise
    
    def construct_prompt(self, user_prompt: str, brand_metadata: Dict[str, str]) -> str:
        """
        Construct enhanced prompt using brand metadata from RAG pipeline.
        """
        tone_of_voice = brand_metadata.get('tone_of_voice', '')
        brand_communications = brand_metadata.get('brand_communications', '')
        visual_style = brand_metadata.get('visual_style', '')
        color_palette = brand_metadata.get('color_palette', '')
        target_audience = brand_metadata.get('target_audience', '')
        
        enhanced_prompt = user_prompt
        
        if tone_of_voice:
            enhanced_prompt += f", {tone_of_voice} tone"
        
        if visual_style:
            enhanced_prompt += f", {visual_style} style"
        
        if color_palette:
            enhanced_prompt += f", using {color_palette} colors"
        
        if brand_communications:
            enhanced_prompt += f", {brand_communications}"
        
        if target_audience:
            enhanced_prompt += f", appealing to {target_audience}"
        
        enhanced_prompt += ", professional photography, high quality, detailed, 8k resolution"
        
        return enhanced_prompt
    
    def generate_image(
        self,
        prompt: str,
        brand_metadata: Optional[Dict[str, str]] = None,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, str]:
        """
        Generate an image using Stable Diffusion XL.
        """
        self.load_model()
        
        if brand_metadata:
            enhanced_prompt = self.construct_prompt(prompt, brand_metadata)
        else:
            enhanced_prompt = prompt
        
        logger.info(f"Generating image with prompt: {enhanced_prompt}")
        
        default_negative_prompt = "low quality, blurry, distorted, deformed, ugly, bad anatomy, watermark, text, signature"
        if negative_prompt:
            final_negative_prompt = f"{negative_prompt}, {default_negative_prompt}"
        else:
            final_negative_prompt = default_negative_prompt
        
        try:
            image = self.pipeline(
                prompt=enhanced_prompt,
                negative_prompt=final_negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height
            ).images[0]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            image.save(filepath)
            logger.info(f"Image saved to: {filepath}")
            
            return {
                "status": "success",
                "filepath": filepath,
                "filename": filename,
                "prompt": enhanced_prompt,
                "original_prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

image_generator = ImageGeneratorService()
