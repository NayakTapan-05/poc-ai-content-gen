"""
Local video generation provider with GPU/CPU support.
Uses Stable Video Diffusion (SVD) for both GPU and CPU modes.
"""
import torch
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video
from PIL import Image
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
import logging
import numpy as np

logger = logging.getLogger(__name__)


class LocalVideoProvider:
    """Provider for local video generation with GPU/CPU support."""
    
    def __init__(self, model_name: str = "svd-xt", device: str = "cpu", output_dir: Path = Path("./data/generated_content")):
        self.model_name = model_name
        self.device = device
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.pipeline = None
        self.model_loaded = False
        
        self.model_configs = {
            "svd-xt": {
                "model_id": "stabilityai/stable-video-diffusion-img2vid-xt",
                "gpu_frames": 25,
                "gpu_steps": 25,
                "cpu_frames": 8,
                "cpu_steps": 8
            }
        }
    
    def load_model(self):
        """Lazy load the video generation model."""
        if self.model_loaded:
            return
        
        config = self.model_configs.get(self.model_name)
        if not config:
            raise ValueError(f"Unknown model: {self.model_name}")
        
        logger.info(f"Loading video model: {self.model_name} ({config['model_id']}) on {self.device}")
        
        try:
            if self.device == "cuda":
                self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
                    config['model_id'],
                    torch_dtype=torch.float16,
                    variant="fp16"
                )
                self.pipeline.enable_model_cpu_offload()
            else:
                self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
                    config['model_id'],
                    torch_dtype=torch.float32
                )
            
            self.pipeline = self.pipeline.to(self.device)
            self.model_loaded = True
            logger.info(f"Video model loaded successfully: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error loading video model: {e}")
            raise
    
    def _create_initial_image(self, prompt: str, size: int = 256) -> Image.Image:
        """
        Create a simple initial image from prompt.
        For SVD, we need an initial image to animate.
        In a real implementation, this could use the image generator.
        For now, create a simple colored image with text.
        """
        from PIL import ImageDraw, ImageFont
        
        img = Image.new('RGB', (size, size), color=(100, 150, 200))
        draw = ImageDraw.Draw(img)
        
        for i in range(0, size, 20):
            draw.line([(0, i), (size, i)], fill=(120, 170, 220), width=2)
        
        return img
    
    def generate_video(
        self,
        prompt: str,
        num_frames: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        fps: int = 8,
        motion_bucket_id: int = 127,
        noise_aug_strength: float = 0.02,
        seed: Optional[int] = None
    ) -> Dict:
        """
        Generate a video from prompt.
        SVD is img2vid, so we create an initial image first.
        Returns dict with status, filepath, filename, etc.
        """
        self.load_model()
        
        config = self.model_configs[self.model_name]
        
        if num_frames is None:
            num_frames = config['gpu_frames'] if self.device == "cuda" else config['cpu_frames']
        if num_inference_steps is None:
            num_inference_steps = config['gpu_steps'] if self.device == "cuda" else config['cpu_steps']
        
        logger.info(f"Generating video: {prompt[:50]}... (frames={num_frames}, steps={num_inference_steps}, device={self.device})")
        
        try:
            initial_image = self._create_initial_image(prompt, size=256)
            
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            else:
                generator = None
            
            frames = self.pipeline(
                initial_image,
                decode_chunk_size=2,
                num_frames=num_frames,
                num_inference_steps=num_inference_steps,
                motion_bucket_id=motion_bucket_id,
                noise_aug_strength=noise_aug_strength,
                generator=generator
            ).frames[0]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            filepath = self.output_dir / filename
            
            export_to_video(frames, str(filepath), fps=fps)
            logger.info(f"Video saved to: {filepath} ({len(frames)} frames)")
            
            return {
                "status": "success",
                "filepath": str(filepath),
                "filename": filename,
                "prompt": prompt,
                "num_frames": len(frames),
                "fps": fps,
                "model": self.model_name,
                "device": self.device
            }
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
