# ComfyUI HTTP Nodes
# A comprehensive collection of HTTP client nodes for ComfyUI
# Supports all HTTP methods, session management, authentication, and file handling

from .http_client import HTTPClient
from .http_session_manager import HTTPSessionManager
from .http_auth import HTTPAuth
from .http_get import HTTPGet
from .http_post import HTTPPost
from .http_put import HTTPPut
from .http_patch import HTTPPatch
from .http_delete import HTTPDelete
from .http_head import HTTPHead
from .http_options import HTTPOptions
from .http_form_data import HTTPFormData, HTTPFormDataItem, HTTPFormFileItem, HTTPFormImageItem, HTTPFormTextItem
from .http_form_data_concat import HTTPFormDataConcat
from .http_json_converter import HTTPConvertJSON, HTTPGetJSONField
from .http_file_upload import HTTPFileUpload
from .http_image_loader import HTTPImageLoader
from .http_display_result import HTTPDisplayResult
from .base64_converter import Base64ToImage, ImageToBase64
from .utils import HTTPUtils

# Node class mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    # Core HTTP methods
    "HTTPGet": HTTPGet,
    "HTTPPost": HTTPPost,
    "HTTPPut": HTTPPut,
    "HTTPPatch": HTTPPatch,
    "HTTPDelete": HTTPDelete,
    "HTTPHead": HTTPHead,
    "HTTPOptions": HTTPOptions,
    
    # Session and authentication
    "HTTPSessionManager": HTTPSessionManager,
    "HTTPAuth": HTTPAuth,
    
    # Form data handling
    "HTTPFormData": HTTPFormData,
    "HTTPFormDataItem": HTTPFormDataItem,
    "HTTPFormFileItem": HTTPFormFileItem,
    "HTTPFormImageItem": HTTPFormImageItem,
    "HTTPFormTextItem": HTTPFormTextItem,
    "HTTPFormDataConcat": HTTPFormDataConcat,
    
    # JSON utilities
    "HTTPConvertJSON": HTTPConvertJSON,
    "HTTPGetJSONField": HTTPGetJSONField,
    
    # File and image handling
    "HTTPFileUpload": HTTPFileUpload,
    "HTTPImageLoader": HTTPImageLoader,
    "Base64ToImage": Base64ToImage,
    "ImageToBase64": ImageToBase64,
    
    # Display and utilities
    "HTTPDisplayResult": HTTPDisplayResult,
    "HTTPUtils": HTTPUtils
}

# Display names for ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS = {
    "HTTPGet": "HTTP GET Request",
    "HTTPPost": "HTTP POST Request", 
    "HTTPPut": "HTTP PUT Request",
    "HTTPPatch": "HTTP PATCH Request",
    "HTTPDelete": "HTTP DELETE Request",
    "HTTPHead": "HTTP HEAD Request",
    "HTTPOptions": "HTTP OPTIONS Request",
    "HTTPSessionManager": "HTTP Session Manager",
    "HTTPAuth": "HTTP Authentication",
    "HTTPFormData": "HTTP Form Data",
    "HTTPFormDataItem": "HTTP Form Data Item",
    "HTTPFormFileItem": "HTTP Form File Item",
    "HTTPFormImageItem": "HTTP Form Image Item", 
    "HTTPFormTextItem": "HTTP Form Text Item",
    "HTTPFormDataConcat": "HTTP Form Data Concat",
    "HTTPConvertJSON": "HTTP Convert JSON",
    "HTTPGetJSONField": "HTTP Get JSON Field",
    "HTTPFileUpload": "HTTP File Upload",
    "HTTPImageLoader": "HTTP Image Loader",
    "Base64ToImage": "Base64 to Image",
    "ImageToBase64": "Image to Base64",
    "HTTPDisplayResult": "HTTP Display Result",
    "HTTPUtils": "HTTP Utilities"
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]
