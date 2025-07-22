import io
from PIL import Image
import numpy as np
from typing import Dict, Any, Tuple

class HTTPFormImageItemNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "field_name": ("STRING", {
                    "default": "image"
                }),
                "image_input": ("IMAGE",),
            },
            "optional": {
                "image_format": (["png", "jpg", "jpeg", "webp"], {
                    "default": "png"
                }),
                "image_filename": ("STRING", {
                    "default": "photo"
                }),
            }
        }
    
    RETURN_TYPES = ("FORM_DATA_ITEM",)
    RETURN_NAMES = ("image_item",)
    FUNCTION = "create_image_item"
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
    
    def create_image_item(self, field_name: str, image_input, 
                         image_format: str = "png", image_filename: str = "photo") -> Tuple[Dict]:
        
        try:
            pil_image = self.tensor_to_pil(image_input)
            
            img_buffer = io.BytesIO()
            if image_format.lower() == "jpg":
                image_format = "jpeg"
            pil_image.save(img_buffer, format=image_format.upper())
            img_bytes = img_buffer.getvalue()
            
            form_item = {
                "field_name": field_name,
                "field_type": "image",
                "data": {
                    "content": img_bytes,
                    "filename": f"{image_filename}.{image_format}",
                    "mime_type": f"image/{image_format.lower()}"
                },
                "timestamp": str(hash(field_name + image_filename + str(len(img_bytes))))
            }
            
            print(f"Form Image Item - '{field_name}': {image_filename}.{image_format} ({len(img_bytes)} bytes)")
            return (form_item,)
            
        except Exception as e:
            print(f"Error creating image item '{field_name}': {str(e)}")
            form_item = {
                "field_name": field_name,
                "field_type": "image",
                "data": None,
                "error": str(e),
                "timestamp": str(hash(field_name + str(e)))
            }
            return (form_item,)
