import base64
import io
from PIL import Image
import numpy as np
import torch
from typing import Dict, Any, Tuple

class ImageToBase64Node:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "image_format": (["png", "jpg", "jpeg", "webp"], {
                    "default": "png"
                }),
                "include_prefix": ("BOOLEAN", {
                    "default": True
                }),
                "quality": ("INT", {
                    "default": 95,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64_string",)
    FUNCTION = "image_to_base64"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    def tensor_to_pil(self, tensor):
        """Convert tensor to PIL Image"""
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        
        numpy_image = (tensor.cpu().numpy() * 255).astype(np.uint8)
        
        if numpy_image.shape[-1] == 3:
            return Image.fromarray(numpy_image, 'RGB')
        elif numpy_image.shape[-1] == 4:
            return Image.fromarray(numpy_image, 'RGBA')
        elif len(numpy_image.shape) == 2:
            return Image.fromarray(numpy_image, 'L')
        else:
            return Image.fromarray(numpy_image[:,:,:3], 'RGB')
    
    def image_to_base64(self, image: torch.Tensor, image_format: str = "png", 
                       include_prefix: bool = True, quality: int = 95) -> Tuple[str]:
        try:
            # Convert tensor to PIL
            pil_image = self.tensor_to_pil(image)
            
            # Save to bytes buffer
            img_buffer = io.BytesIO()
            
            if image_format.lower() == "jpg":
                image_format = "jpeg"
            
            save_kwargs = {"format": image_format.upper()}
            if image_format.lower() == "jpeg":
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True
            
            pil_image.save(img_buffer, **save_kwargs)
            img_bytes = img_buffer.getvalue()
            
            # Encode to base64
            base64_string = base64.b64encode(img_bytes).decode('utf-8')
            
            # Add data URL prefix if requested
            if include_prefix:
                mime_type = f"image/{image_format.lower()}"
                base64_string = f"data:{mime_type};base64,{base64_string}"
            
            print(f"Image to Base64 - Format: {image_format}")
            print(f"Image to Base64 - Size: {pil_image.size[0]}x{pil_image.size[1]}")
            print(f"Image to Base64 - Base64 length: {len(base64_string)} chars")
            
            return (base64_string,)
            
        except Exception as e:
            print(f"Error converting image to base64: {str(e)}")
            return ("",)
