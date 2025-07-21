from .http_get import HTTPGetNode
from .http_get_json_field import HTTPGetJSONFieldNode

NODE_CLASS_MAPPINGS = {
    "HTTPGetNode": HTTPGetNode,
    "HTTPGetJSONFieldNode": HTTPGetJSONFieldNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HTTPGetNode": "HTTP Get",
    "HTTPGetJSONFieldNode": "HTTP Get JSON Field",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']