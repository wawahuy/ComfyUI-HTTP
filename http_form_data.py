"""
HTTP Form Data nodes for ComfyUI
Handles multipart form data creation and management
"""

from typing import Dict, Any, List, Tuple, Union, Optional
import json
import base64
import io
import os
from PIL import Image
import numpy as np

class HTTPFormDataItem:
    """Base Form Data Item Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": ("STRING", {"default": "field_name"}),
                "value": ("STRING", {"default": "field_value"}),
            }
        }
    
    RETURN_TYPES = ("HTTP_FORM_ITEM",)
    RETURN_NAMES = ("form_item",)
    FUNCTION = "create_item"
    CATEGORY = "HTTP/Form Data"
    
    def create_item(self, name: str, value: str):
        """Create a form data item"""
        return ({
            "type": "text",
            "name": name,
            "value": value
        },)

class HTTPFormTextItem:
    """Text Form Data Item Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": ("STRING", {"default": "text_field"}),
                "value": ("STRING", {"default": "text_value"}),
            },
            "optional": {
                "content_type": ("STRING", {"default": "text/plain"}),
            }
        }
    
    RETURN_TYPES = ("HTTP_FORM_ITEM",)
    RETURN_NAMES = ("form_item",)
    FUNCTION = "create_item"
    CATEGORY = "HTTP/Form Data"
    
    def create_item(self, name: str, value: str, content_type: str = "text/plain"):
        """Create a text form data item"""
        return ({
            "type": "text",
            "name": name,
            "value": value,
            "content_type": content_type
        },)

class HTTPFormFileItem:
    """File Form Data Item Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": ("STRING", {"default": "file"}),
                "file_path": ("STRING", {"default": "/path/to/file.txt"}),
            },
            "optional": {
                "filename": ("STRING", {"default": ""}),
                "content_type": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("HTTP_FORM_ITEM",)
    RETURN_NAMES = ("form_item",)
    FUNCTION = "create_item"
    CATEGORY = "HTTP/Form Data"
    
    def create_item(self, name: str, file_path: str, filename: str = "", content_type: str = ""):
        """Create a file form data item"""
        
        # Auto-detect filename if not provided
        if not filename:
            filename = os.path.basename(file_path)
        
        # Auto-detect content type if not provided
        if not content_type:
            ext = os.path.splitext(file_path)[1].lower()
            content_type_map = {
                '.txt': 'text/plain',
                '.json': 'application/json',
                '.xml': 'application/xml',
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp',
                '.mp4': 'video/mp4',
                '.avi': 'video/avi',
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
            }
            content_type = content_type_map.get(ext, 'application/octet-stream')
        
        return ({
            "type": "file",
            "name": name,
            "file_path": file_path,
            "filename": filename,
            "content_type": content_type
        },)

class HTTPFormImageItem:
    """Image Form Data Item Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": ("STRING", {"default": "image"}),
                "image": ("IMAGE",),
            },
            "optional": {
                "filename": ("STRING", {"default": "image.png"}),
                "format": (["PNG", "JPEG", "WEBP"], {"default": "PNG"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100}),
            }
        }
    
    RETURN_TYPES = ("HTTP_FORM_ITEM",)
    RETURN_NAMES = ("form_item",)
    FUNCTION = "create_item"
    CATEGORY = "HTTP/Form Data"
    
    def create_item(self, name: str, image, filename: str = "image.png", 
                   format: str = "PNG", quality: int = 95):
        """Create an image form data item"""
        
        try:
            # Convert ComfyUI image tensor to PIL Image
            if isinstance(image, (list, tuple)):
                image = image[0]  # Take first image if batch
            
            # Convert from tensor to numpy array
            if hasattr(image, 'cpu'):
                image_np = image.cpu().numpy()
            else:
                image_np = np.array(image)
            
            # Ensure correct shape and data type
            if image_np.ndim == 4:
                image_np = image_np[0]  # Remove batch dimension
            if image_np.ndim == 3 and image_np.shape[0] in [1, 3, 4]:
                image_np = np.transpose(image_np, (1, 2, 0))  # CHW to HWC
            
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
                save_kwargs["optimize"] = True
            elif format == "PNG":
                save_kwargs["optimize"] = True
            elif format == "WEBP":
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True
            
            pil_image.save(img_buffer, **save_kwargs)
            img_bytes = img_buffer.getvalue()
            
            # Set content type based on format
            content_type_map = {
                "PNG": "image/png",
                "JPEG": "image/jpeg", 
                "WEBP": "image/webp"
            }
            content_type = content_type_map.get(format, "image/png")
            
            return ({
                "type": "image_bytes",
                "name": name,
                "data": img_bytes,
                "filename": filename,
                "content_type": content_type
            },)
            
        except Exception as e:
            print(f"Error creating image form item: {e}")
            return ({
                "type": "text",
                "name": name,
                "value": f"Error: {str(e)}"
            },)

class HTTPFormData:
    """Form Data Container Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "item1": ("HTTP_FORM_ITEM",),
                "item2": ("HTTP_FORM_ITEM",),
                "item3": ("HTTP_FORM_ITEM",),
                "item4": ("HTTP_FORM_ITEM",),
                "item5": ("HTTP_FORM_ITEM",),
                "item6": ("HTTP_FORM_ITEM",),
                "item7": ("HTTP_FORM_ITEM",),
                "item8": ("HTTP_FORM_ITEM",),
                "item9": ("HTTP_FORM_ITEM",),
                "item10": ("HTTP_FORM_ITEM",),
            }
        }
    
    RETURN_TYPES = ("HTTP_FORM_DATA",)
    RETURN_NAMES = ("form_data",)
    FUNCTION = "create_form_data"
    CATEGORY = "HTTP/Form Data"
    
    def create_form_data(self, **kwargs):
        """Create form data from multiple items"""
        
        form_data = {"data": {}, "files": {}}
        
        # Process all provided items
        for key, item in kwargs.items():
            if item is None:
                continue
                
            item_type = item.get("type", "text")
            item_name = item.get("name", key)
            
            if item_type == "text":
                form_data["data"][item_name] = item.get("value", "")
            
            elif item_type == "file":
                file_path = item.get("file_path", "")
                filename = item.get("filename", "")
                content_type = item.get("content_type", "application/octet-stream")
                
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        form_data["files"][item_name] = (filename, file_data, content_type)
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
                        form_data["data"][item_name] = f"Error reading file: {e}"
                else:
                    form_data["data"][item_name] = f"File not found: {file_path}"
            
            elif item_type == "image_bytes":
                filename = item.get("filename", "image.png")
                content_type = item.get("content_type", "image/png")
                img_bytes = item.get("data", b"")
                
                if img_bytes:
                    form_data["files"][item_name] = (filename, img_bytes, content_type)
                else:
                    form_data["data"][item_name] = "Error: No image data"
        
        return (form_data,)