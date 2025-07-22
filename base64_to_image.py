import base64
import io
from PIL import Image
import numpy as np
import torch
from typing import Dict, Any, Tuple

class Base64ToImageNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "base64_string": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            },
            "optional": {
                "remove_prefix": ("BOOLEAN", {
                    "default": True
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "base64_to_image"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    def base64_to_image(self, base64_string: str, remove_prefix: bool = True) -> Tuple[torch.Tensor]:
        try:
            # Remove data URL prefix if present (data:image/png;base64,)
            if remove_prefix and base64_string.startswith('data:'):
                base64_string = base64_string.split(',', 1)[1]
            
            # Remove any whitespace/newlines
            base64_string = base64_string.strip().replace('\n', '').replace('\r', '')
            
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            
            # Open image with PIL
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert PIL to numpy array
            numpy_image = np.array(pil_image).astype(np.float32) / 255.0
            
            # Convert to torch tensor with batch dimension [1, H, W, C]
            tensor_image = torch.from_numpy(numpy_image)[None,]
            
            print(f"Base64 to Image - Decoded: {pil_image.size[0]}x{pil_image.size[1]} {pil_image.mode}")
            print(f"Base64 to Image - Tensor shape: {tensor_image.shape}")
            
            return (tensor_image,)
            
        except base64.binascii.Error as e:
            print(f"Base64 decode error: {str(e)}")
            # Return a default 1x1 black image
            default_image = torch.zeros(1, 1, 1, 3)
            return (default_image,)
            
        except Exception as e:
            print(f"Error converting base64 to image: {str(e)}")
            # Return a default 1x1 black image
            default_image = torch.zeros(1, 1, 1, 3)
            return (default_image,)
