"""
Base64 conversion nodes for ComfyUI HTTP
Converts between images and base64 strings
"""

import base64
import io
import json
import numpy as np
import torch
from PIL import Image
from typing import Tuple

class Base64ToImage:
    """Base64 to Image Converter Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_string": ("STRING", {"default": ""}),
            },
            "optional": {
                "remove_prefix": ("BOOLEAN", {"default": True}),
                "convert_mode": (["RGB", "RGBA", "L", "auto"], {"default": "auto"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "width", "height", "info")
    FUNCTION = "convert_to_image"
    CATEGORY = "HTTP/Image Conversion"
    
    def convert_to_image(self, base64_string: str, remove_prefix: bool = True, 
                        convert_mode: str = "auto") -> Tuple:
        """Convert base64 string to image tensor"""
        
        try:
            # Remove data URL prefix if present
            if remove_prefix and base64_string.startswith('data:'):
                # Find the comma that separates the header from the data
                comma_index = base64_string.find(',')
                if comma_index != -1:
                    base64_string = base64_string[comma_index + 1:]
            
            # Decode base64 string
            try:
                image_bytes = base64.b64decode(base64_string)
            except Exception as e:
                error_msg = f"Base64 decode error: {str(e)}"
                print(error_msg)
                # Return fallback image
                fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return (fallback_image, 64, 64, error_msg)
            
            # Load image with PIL
            try:
                image = Image.open(io.BytesIO(image_bytes))
                original_format = image.format or "Unknown"
                original_mode = image.mode
                
                # Convert image mode if specified
                if convert_mode != "auto":
                    image = image.convert(convert_mode)
                elif image.mode not in ["RGB", "RGBA", "L"]:
                    # Convert unsupported modes to RGB
                    image = image.convert("RGB")
                
                # Convert PIL Image to numpy array
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
                image_tensor = torch.from_numpy(image_np).unsqueeze(0)
                
                # Get dimensions
                height, width = image_tensor.shape[1:3]
                
                # Prepare info
                info = json.dumps({
                    "size": f"{width}x{height}",
                    "original_format": original_format,
                    "original_mode": original_mode,
                    "final_mode": image.mode,
                    "data_size": len(image_bytes)
                }, indent=2)
                
                return (image_tensor, width, height, info)
                
            except Exception as e:
                error_msg = f"Image processing error: {str(e)}"
                print(error_msg)
                fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
                return (fallback_image, 64, 64, error_msg)
            
        except Exception as e:
            error_msg = f"Base64 to image conversion failed: {str(e)}"
            print(error_msg)
            fallback_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            return (fallback_image, 64, 64, error_msg)

class ImageToBase64:
    """Image to Base64 Converter Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "format": (["PNG", "JPEG", "WEBP"], {"default": "PNG"}),
            },
            "optional": {
                "quality": ("INT", {"default": 95, "min": 1, "max": 100}),
                "add_prefix": ("BOOLEAN", {"default": True}),
                "optimize": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("base64_string", "data_url", "size_bytes")
    FUNCTION = "convert_to_base64"
    CATEGORY = "HTTP/Image Conversion"
    
    def convert_to_base64(self, image, format: str = "PNG", quality: int = 95, 
                         add_prefix: bool = True, optimize: bool = True) -> Tuple[str, str, int]:
        """Convert image tensor to base64 string"""
        
        try:
            # Handle batch dimension
            if isinstance(image, (list, tuple)):
                image = image[0]  # Take first image if batch
            
            # Convert from tensor to numpy array
            if hasattr(image, 'cpu'):
                image_np = image.cpu().numpy()
            else:
                image_np = np.array(image)
            
            # Remove batch dimension if present
            if image_np.ndim == 4:
                image_np = image_np[0]
            
            # Convert from CHW to HWC if needed
            if image_np.ndim == 3 and image_np.shape[0] in [1, 3, 4]:
                image_np = np.transpose(image_np, (1, 2, 0))
            
            # Normalize to 0-255 range
            if image_np.dtype == np.float32 or image_np.dtype == np.float64:
                image_np = (image_np * 255).astype(np.uint8)
            
            # Convert to PIL Image
            if image_np.shape[2] == 1:
                pil_image = Image.fromarray(image_np[:, :, 0], mode='L')
            elif image_np.shape[2] == 3:
                pil_image = Image.fromarray(image_np, mode='RGB')
            elif image_np.shape[2] == 4:
                pil_image = Image.fromarray(image_np, mode='RGBA')
            else:
                raise ValueError(f"Unsupported image shape: {image_np.shape}")
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            save_kwargs = {"format": format}
            
            if format == "JPEG":
                save_kwargs["quality"] = quality
                if optimize:
                    save_kwargs["optimize"] = True
                # Convert RGBA to RGB for JPEG
                if pil_image.mode == "RGBA":
                    rgb_image = Image.new("RGB", pil_image.size, (255, 255, 255))
                    rgb_image.paste(pil_image, mask=pil_image.split()[-1])
                    pil_image = rgb_image
            elif format == "PNG":
                if optimize:
                    save_kwargs["optimize"] = True
            elif format == "WEBP":
                save_kwargs["quality"] = quality
                if optimize:
                    save_kwargs["optimize"] = True
            
            pil_image.save(img_buffer, **save_kwargs)
            img_bytes = img_buffer.getvalue()
            
            # Convert to base64
            base64_string = base64.b64encode(img_bytes).decode('utf-8')
            
            # Create data URL if requested
            if add_prefix:
                mime_types = {
                    "PNG": "image/png",
                    "JPEG": "image/jpeg",
                    "WEBP": "image/webp"
                }
                mime_type = mime_types.get(format, "image/png")
                data_url = f"data:{mime_type};base64,{base64_string}"
            else:
                data_url = base64_string
            
            return (base64_string, data_url, len(img_bytes))
            
        except Exception as e:
            error_msg = f"Image to base64 conversion failed: {str(e)}"
            print(error_msg)
            return (error_msg, error_msg, 0)