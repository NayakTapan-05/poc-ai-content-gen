import torch
from diffusers import DiffusionPipeline
import os
from datetime import datetime
from typing import Optional, Dict
import logging
import imageio

logger = logging.getLogger(__name__)

class VideoGeneratorService:
    def __init__(self, output_dir: str = "./data/generated_content"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        self.pipeline = None
        self.model_loaded = False
    
    def load_model(self):
        """
        Load ModelScope text-to-video model.
        This is done lazily to avoid loading the model on startup.
        """
        if self.model_loaded:
            return
        
        logger.info("Loading ModelScope text-to-video model...")
        
        try:
            self.pipeline = DiffusionPipeline.from_pretrained(
                "damo-vilab/text-to-video-ms-1.7b",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None
            )
            
            self.pipeline = self.pipeline.to(self.device)
            
            if self.device == "cuda":
                self.pipeline.enable_model_cpu_offload()
                self.pipeline.enable_vae_slicing()
            
            self.model_loaded = True
            logger.info("ModelScope text-to-video model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading ModelScope model: {e}")
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
        
        enhanced_prompt += ", cinematic, high quality, smooth motion"
        
        return enhanced_prompt
    
    def generate_video(
        self,
        prompt: str,
        brand_metadata: Optional[Dict[str, str]] = None,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 25,
        num_frames: int = 16,
        guidance_scale: float = 9.0
    ) -> Dict[str, str]:
        """
        Generate a video using ModelScope text-to-video model.
        """
        self.load_model()
        
        if brand_metadata:
            enhanced_prompt = self.construct_prompt(prompt, brand_metadata)
        else:
            enhanced_prompt = prompt
        
        logger.info(f"Generating video with prompt: {enhanced_prompt}")
        
        default_negative_prompt = "low quality, blurry, distorted, deformed, ugly, bad anatomy, static, still image"
        if negative_prompt:
            final_negative_prompt = f"{negative_prompt}, {default_negative_prompt}"
        else:
            final_negative_prompt = default_negative_prompt
        
        try:
            video_frames = self.pipeline(
                prompt=enhanced_prompt,
                negative_prompt=final_negative_prompt,
                num_inference_steps=num_inference_steps,
                num_frames=num_frames,
                guidance_scale=guidance_scale
            ).frames[0]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            filepath = os.path.join(self.output_dir, filename)
            
            writer = imageio.get_writer(filepath, fps=8)
            for frame in video_frames:
                writer.append_data(frame)
            writer.close()
            
            logger.info(f"Video saved to: {filepath}")
            
            return {
                "status": "success",
                "filepath": filepath,
                "filename": filename,
                "prompt": enhanced_prompt,
                "original_prompt": prompt,
                "num_frames": len(video_frames)
            }
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

video_generator = VideoGeneratorService()
