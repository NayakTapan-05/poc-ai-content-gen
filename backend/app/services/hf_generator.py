"""
Hugging Face Inference API Integration
Supports both Inference API and Inference Endpoints
Uses direct API calls to avoid InferenceClient bugs
"""

import os
import io
import base64
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class HFGenerator:
    """Hugging Face generation service using direct API calls"""
    
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        if not self.hf_token:
            raise ValueError("HF_TOKEN environment variable not set")
        
        self.api_base = "https://api-inference.huggingface.co/models"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        self.image_models = {
            "sd-turbo": "stabilityai/sd-turbo",
            "sd15": "runwayml/stable-diffusion-v1-5"
        }
        
        self.svd_img2vid_endpoint = os.getenv("HF_SVD_IMG2VID_ENDPOINT")
        self.svd_xt_endpoint = os.getenv("HF_SVD_XT_ENDPOINT")
        
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.media_dir = self.data_dir / "generated_content"
        self.media_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_image(
        self,
        prompt: str,
        model_id: str = "sd-turbo",
        width: int = 768,
        height: int = 768,
        num_inference_steps: int = 4,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate image using HF Inference API
        
        Args:
            prompt: Text prompt for generation
            model_id: Model identifier (sd-turbo or sd15)
            width: Image width
            height: Image height
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for generation
            seed: Random seed for reproducibility
        
        Returns:
            Dict with media_url and metadata
        """
        try:
            model_name = self.image_models.get(model_id, self.image_models["sd-turbo"])
            api_url = f"{self.api_base}/{model_name}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "width": width,
                    "height": height
                }
            }
            
            if seed is not None:
                payload["parameters"]["seed"] = seed
            
            logger.info(f"Calling HF API: {api_url}")
            response = requests.post(api_url, headers=self.headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                error_detail = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"HF API error: {error_detail}")
                raise Exception(error_detail)
            
            image_bytes = response.content
            
            import time
            filename = f"image_{int(time.time())}_{seed or 'random'}.png"
            filepath = self.media_dir / filename
            
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            
            logger.info(f"Generated image saved to {filepath}")
            
            return {
                "media_url": f"/media/{filename}",
                "model": model_name,
                "prompt": prompt,
                "width": width,
                "height": height,
                "steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "seed": seed
            }
        
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'response'):
                try:
                    error_msg = f"{error_msg} | Response: {e.response.text}"
                except:
                    pass
            logger.error(f"Image generation failed: {error_msg}")
            raise Exception(f"HF image generation failed: {error_msg}")
    
    def generate_video(
        self,
        prompt: str,
        model_id: str = "svd-img2vid",
        image: Optional[bytes] = None,
        num_frames: int = 12,
        num_inference_steps: int = 8,
        fps: int = 8,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate video using HF Inference Endpoints
        
        Args:
            prompt: Text prompt for generation
            model_id: Model identifier (svd-img2vid or svd-xt)
            image: Starting image bytes (required for img2vid)
            num_frames: Number of video frames
            num_inference_steps: Number of denoising steps
            fps: Frames per second
            seed: Random seed for reproducibility
        
        Returns:
            Dict with media_url and metadata
        """
        try:
            if model_id == "svd-img2vid":
                endpoint_url = self.svd_img2vid_endpoint
            elif model_id == "svd-xt":
                endpoint_url = self.svd_xt_endpoint
            else:
                raise ValueError(f"Unknown video model: {model_id}")
            
            if not endpoint_url:
                raise ValueError(
                    f"Inference Endpoint URL not configured for {model_id}. "
                    f"Please set HF_SVD_IMG2VID_ENDPOINT or HF_SVD_XT_ENDPOINT in .env"
                )
            
            headers = {
                "Authorization": f"Bearer {self.hf_token}",
                "Content-Type": "application/json"
            }
            
            image_b64 = None
            if image:
                image_b64 = base64.b64encode(image).decode('utf-8')
            
            payload = {
                "inputs": {
                    "prompt": prompt,
                    "image": image_b64,
                    "num_frames": num_frames,
                    "num_inference_steps": num_inference_steps,
                    "fps": fps
                }
            }
            
            if seed is not None:
                payload["inputs"]["seed"] = seed
            
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Endpoint returned {response.status_code}: {response.text}")
            
            import time
            filename = f"video_{int(time.time())}_{seed or 'random'}.mp4"
            filepath = self.media_dir / filename
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            return {
                "media_url": f"/media/{filename}",
                "model": model_id,
                "prompt": prompt,
                "num_frames": num_frames,
                "fps": fps,
                "steps": num_inference_steps,
                "seed": seed
            }
        
        except Exception as e:
            raise Exception(f"HF video generation failed: {str(e)}")
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        return {
            "image": [
                {"id": "sd-turbo", "label": "Stable Diffusion Turbo"},
                {"id": "sd15", "label": "Stable Diffusion 1.5"}
            ],
            "video": [
                {"id": "svd-img2vid", "label": "Stable Video Diffusion (img2vid)"},
                {"id": "svd-xt", "label": "Stable Video Diffusion (img2vid-xt)"}
            ],
            "defaults": {
                "imageId": os.getenv("IMAGE_MODEL", "sd-turbo"),
                "videoId": os.getenv("VIDEO_MODEL", "svd-img2vid")
            }
        }
