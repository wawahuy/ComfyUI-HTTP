from .http_get import HTTPGetNode
from .http_get_json_field import HTTPGetJSONFieldNode
from .http_post_form_data import HTTPPostFormDataNode
from .http_post_json import HTTPPostJSONNode
from .http_post_raw import HTTPPostRawNode
from .http_form_data import HTTPFormDataNode
from .http_form_data_concat import HTTPFormDataConcatNode
from .http_form_text_item import HTTPFormTextItemNode
from .http_form_file_item import HTTPFormFileItemNode
from .http_form_image_item import HTTPFormImageItemNode
from .base64_to_image import Base64ToImageNode
from .image_to_base64 import ImageToBase64Node

NODE_CLASS_MAPPINGS = {
    "HTTPGetNode": HTTPGetNode,
    "HTTPGetJSONFieldNode": HTTPGetJSONFieldNode,
    "HTTPPostFormDataNode": HTTPPostFormDataNode,
    "HTTPPostJSONNode": HTTPPostJSONNode,
    "HTTPPostRawNode": HTTPPostRawNode,
    "HTTPFormDataNode": HTTPFormDataNode,
    "HTTPFormDataConcatNode": HTTPFormDataConcatNode,
    "HTTPFormTextItemNode": HTTPFormTextItemNode,
    "HTTPFormFileItemNode": HTTPFormFileItemNode,
    "HTTPFormImageItemNode": HTTPFormImageItemNode,
    "Base64ToImageNode": Base64ToImageNode,
    "ImageToBase64Node": ImageToBase64Node,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HTTPGetNode": "HTTP Get",
    "HTTPGetJSONFieldNode": "HTTP Get JSON Field",
    "HTTPPostFormDataNode": "HTTP Post Form Data",
    "HTTPPostJSONNode": "HTTP Post JSON",
    "HTTPPostRawNode": "HTTP Post Raw",
    "HTTPFormDataNode": "HTTP Form Data",
    "HTTPFormDataConcatNode": "HTTP Form Data Concat",
    "HTTPFormTextItemNode": "HTTP Form Text Item",
    "HTTPFormFileItemNode": "HTTP Form File Item",
    "HTTPFormImageItemNode": "HTTP Form Image Item",
    "Base64ToImageNode": "Base64 to Image",
    "ImageToBase64Node": "Image to Base64",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']