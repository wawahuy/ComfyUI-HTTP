from typing import Dict, Any, Tuple

class HTTPFormTextItemNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "field_name": ("STRING", {
                    "default": "name"
                }),
                "text_value": ("STRING", {
                    "multiline": True,
                    "default": "John Doe"
                }),
            }
        }
    
    RETURN_TYPES = ("FORM_DATA_ITEM",)
    RETURN_NAMES = ("text_item",)
    FUNCTION = "create_text_item"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    def create_text_item(self, field_name: str, text_value: str) -> Tuple[Dict]:
        form_item = {
            "field_name": field_name,
            "field_type": "text",
            "data": text_value,
            "timestamp": str(hash(field_name + text_value))
        }
        
        print(f"Form Text Item - '{field_name}': {text_value[:50]}...")
        return (form_item,)
