"""
HTTP Image Loader node for ComfyUI
Downloads and loads images from HTTP URLs
"""

from typing import Dict, Any, Optional, Tuple
from .http_client import HTTPClient
from .http_auth import HTTPAuth
from urllib.parse import urljoin
import json
import io
import numpy as np
from PIL import Image
import torch

class HTTPImageLoader:
    """HTTP Image Loader Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "https://example.com/image.jpg"}),
            },
            "optional": {
                "session": ("HTTP_SESSION",),
                "auth": ("HTTP_AUTH",),
                "headers": ("STRING", {"default": "{}"}),
                "timeout": ("INT", {"default": 30, "min": 1, "max": 300}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
                "allow_redirects": ("BOOLEAN", {"default": True}),
                "cookies": ("STRING", {"default": "{}"}),
                "proxy_url": ("STRING", {"default": ""}),
                "max_size": ("INT", {"default": 10485760, "min": 1024, "max": 104857600}),  # 10MB default
                "resize_mode": (["none", "fit", "fill", "stretch"], {"default": "none"}),
                "target_width": ("INT", {"default": 512, "min": 1, "max": 8192}),
                "target_height": ("INT", {"default": 512, "min": 1, "max": 8192}),
                "convert_mode": (["RGB", "RGBA", "L", "auto"], {"default": "auto"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING", "STRING")
    RETURN_NAMES = ("image", "width", "height", "format", "info")
    FUNCTION = "load_image"
    CATEGORY = "HTTP/Image Operations"
    
    def load_image(self, url: str, session: Optional[Dict] = None, auth: Optional[Dict] = None,
                  headers: str = "{}", timeout: int = 30, verify_ssl: bool = True,
                  allow_redirects: bool = True, cookies: str = "{}", proxy_url: str = "",
                  max_size: int = 10485760, resize_mode: str = "none",
                  target_width: int = 512, target_height: int = 512, convert_mode: str = "auto"):
        """Load image from HTTP URL"""
        
        try:
            # Use session client if provided, otherwise create new one
            if session:
                client = session["client"]
                base_url = session.get("base_url", "")
                if base_url and not url.startswith(("http://", "https://")):
                    url = urljoin(base_url, url)
            else:
                client = HTTPClient()
                client.set_timeout(timeout)
                client.set_ssl_verify(verify_ssl)
                client.allow_redirects = allow_redirects
                
                if proxy_url:
                    client.set_proxy(proxy_url)
            
            # Apply authentication if provided
            if auth:
                HTTPAuth.apply_auth(client, auth)
            
            # Parse headers and set defaults for image requests
            headers_dict = {
                "Accept": "image/*,*/*;q=0.8",  # Accept images with fallback
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            if headers and headers != "{}":
                try:
                    custom_headers = json.loads(headers)
                    headers_dict.update(custom_headers)
                except Exception as e:
                    print(f"Warning: Failed to parse headers: {e}")
            
            client.set_headers(headers_dict)
            
            # Parse cookies
            if cookies and cookies != "{}":
                try:
                    cookies_dict = json.loads(cookies)
                    client.set_cookies(cookies_dict)
                except Exception as e:
                    print(f"Warning: Failed to parse cookies: {e}")
            
            print(f"Loading image from URL: {url}")
            print(f"Headers being sent: {headers_dict}")
            
            # Make the request to get binary image data
            try:
                status_code, response_headers, image_bytes = client.get_binary(url)
                print(f"Response status: {status_code}")
                print(f"Response headers: {response_headers}")
                print(f"Content length: {len(image_bytes)} bytes")
                print(f"Content type: {type(image_bytes)}")
                
                if len(image_bytes) > 0:
                    print(f"First 20 bytes: {image_bytes[:20]}")
                
            except Exception as e:
                error_msg = f"Failed to make HTTP request: {str(e)}"
                print(error_msg)
                fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return (fallback_image, 64, 64, "error", error_msg)
            
            if status_code != 200:
                error_msg = f"HTTP {status_code}: Failed to load image from {url}"
                print(error_msg)
                # Return a small black image as fallback
                fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return (fallback_image, 64, 64, "error", error_msg)
            
            # Check content length
            content_length = len(image_bytes)
            if content_length > max_size:
                error_msg = f"Image too large: {content_length} bytes (max: {max_size})"
                print(error_msg)
                fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return (fallback_image, 64, 64, "error", error_msg)
            
            # Verify we have actual image data
            if content_length < 100:  # Very small file, probably not a valid image
                error_msg = f"Image data too small: {content_length} bytes - may not be a valid image"
                print(error_msg)
                fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return (fallback_image, 64, 64, "error", error_msg)
            
            # Load image with PIL
            try:
                image = Image.open(io.BytesIO(image_bytes))
                original_format = image.format or "Unknown"
                
                # Convert image mode if specified
                if convert_mode != "auto":
                    image = image.convert(convert_mode)
                elif image.mode not in ["RGB", "RGBA", "L"]:
                    # Convert unsupported modes to RGB
                    image = image.convert("RGB")
                
                # Resize image if specified
                original_width, original_height = image.size
                
                if resize_mode != "none":
                    if resize_mode == "fit":
                        # Maintain aspect ratio, fit within target size
                        image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                    elif resize_mode == "fill":
                        # Maintain aspect ratio, fill target size (may crop)
                        img_ratio = original_width / original_height
                        target_ratio = target_width / target_height
                        
                        if img_ratio > target_ratio:
                            # Image is wider, fit height and crop width
                            new_height = target_height
                            new_width = int(target_height * img_ratio)
                        else:
                            # Image is taller, fit width and crop height
                            new_width = target_width
                            new_height = int(target_width / img_ratio)
                        
                        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Crop to target size
                        left = (new_width - target_width) // 2
                        top = (new_height - target_height) // 2
                        right = left + target_width
                        bottom = top + target_height
                        image = image.crop((left, top, right, bottom))
                    
                    elif resize_mode == "stretch":
                        # Stretch to exact target size (may distort)
                        image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Convert PIL Image to tensor
                image_np = np.array(image)
                
                # Handle different image modes
                if len(image_np.shape) == 2:  # Grayscale
                    image_np = np.stack([image_np] * 3, axis=-1)  # Convert to RGB
                elif len(image_np.shape) == 3 and image_np.shape[2] == 4:  # RGBA
                    # Convert RGBA to RGB (blend with white background)
                    rgb = image_np[:, :, :3]
                    alpha = image_np[:, :, 3:4] / 255.0
                    image_np = (rgb * alpha + 255 * (1 - alpha)).astype(np.uint8)
                
                # Normalize to 0-1 range and convert to float32
                image_np = image_np.astype(np.float32) / 255.0
                
                # Convert to PyTorch tensor with batch dimension
                image_tensor = torch.from_numpy(image_np).unsqueeze(0)  # Add batch dimension
                
                # Get final dimensions
                final_height, final_width = image_tensor.shape[1:3]
                
                # Prepare info string
                info = json.dumps({
                    "original_size": f"{original_width}x{original_height}",
                    "final_size": f"{final_width}x{final_height}",
                    "format": original_format,
                    "mode": image.mode,
                    "resize_mode": resize_mode,
                    "file_size": len(image_bytes)
                }, indent=2)
                
                # Close client if not using session
                if not session:
                    client.close()
                
                return (image_tensor, final_width, final_height, original_format, info)
                
            except Exception as e:
                error_msg = f"Failed to process image: {str(e)}"
                print(error_msg)
                fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return (fallback_image, 64, 64, "error", error_msg)
            
        except Exception as e:
            error_msg = f"Image loading failed: {str(e)}"
            print(error_msg)
            fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            return (fallback_image, 64, 64, "error", error_msg)