"""
Local image generation provider with GPU/CPU support.
Supports SD-Turbo (GPU), SD1.5 (GPU), and ONNX (CPU fallback).
"""
import torch
from diffusers import StableDiffusionPipeline, DiffusionPipeline
from optimum.onnxruntime import ORTStableDiffusionPipeline
from PIL import Image
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class LocalImageProvider:
    """Provider for local image generation with GPU/CPU support."""
    
    def __init__(self, model_name: str = "sd-turbo", device: str = "cpu", output_dir: Path = Path("./data/generated_content")):
        self.model_name = model_name
        self.device = device
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.pipeline = None
        self.model_loaded = False
        
        self.model_configs = {
            "sd-turbo": {
                "model_id": "stabilityai/sd-turbo",
                "requires_gpu": True,
                "default_steps": 4,
                "default_guidance": 0.0
            },
            "sd15": {
                "model_id": "runwayml/stable-diffusion-v1-5",
                "requires_gpu": True,
                "default_steps": 20,
                "default_guidance": 7.5
            },
            "onnx": {
                "model_id": "runwayml/stable-diffusion-v1-5",
                "requires_gpu": False,
                "default_steps": 8,
                "default_guidance": 7.5
            }
        }
        
        if self.device == "cpu" and self.model_name in ["sd-turbo", "sd15"]:
            logger.warning(f"CPU detected but {self.model_name} requires GPU. Falling back to ONNX.")
            self.model_name = "onnx"
    
    def load_model(self):
        """Lazy load the image generation model."""
        if self.model_loaded:
            return
        
        config = self.model_configs.get(self.model_name)
        if not config:
            raise ValueError(f"Unknown model: {self.model_name}")
        
        logger.info(f"Loading image model: {self.model_name} ({config['model_id']}) on {self.device}")
        
        try:
            if self.model_name == "onnx":
                self.pipeline = ORTStableDiffusionPipeline.from_pretrained(
                    config['model_id'],
                    export=True
                )
            elif self.model_name == "sd-turbo":
                self.pipeline = DiffusionPipeline.from_pretrained(
                    config['model_id'],
                    torch_dtype=torch.float16,
                    variant="fp16"
                )
                self.pipeline = self.pipeline.to(self.device)
            else:
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    config['model_id'],
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    variant="fp16" if self.device == "cuda" else None
                )
                self.pipeline = self.pipeline.to(self.device)
            
            self.model_loaded = True
            logger.info(f"Image model loaded successfully: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error loading image model: {e}")
            raise
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        width: int = 256,
        height: int = 256,
        seed: Optional[int] = None
    ) -> Dict:
        """
        Generate an image.
        Returns dict with status, filepath, filename, etc.
        """
        self.load_model()
        
        config = self.model_configs[self.model_name]
        
        if num_inference_steps is None:
            num_inference_steps = config['default_steps']
        if guidance_scale is None:
            guidance_scale = config['default_guidance']
        
        if negative_prompt is None:
            negative_prompt = "low quality, blurry, distorted, deformed, ugly, bad anatomy"
        
        logger.info(f"Generating image: {prompt[:50]}... (steps={num_inference_steps}, guidance={guidance_scale}, size={width}x{height})")
        
        try:
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            else:
                generator = None
            
            if self.model_name == "onnx":
                image = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=height,
                    width=width
                ).images[0]
            else:
                image = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=height,
                    width=width,
                    generator=generator
                ).images[0]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.png"
            filepath = self.output_dir / filename
            
            image.save(filepath)
            logger.info(f"Image saved to: {filepath}")
            
            return {
                "status": "success",
                "filepath": str(filepath),
                "filename": filename,
                "prompt": prompt,
                "model": self.model_name,
                "device": self.device
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
