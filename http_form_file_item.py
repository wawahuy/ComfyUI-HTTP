from typing import Dict, Any, Tuple

class HTTPFormFileItemNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "field_name": ("STRING", {
                    "default": "document"
                }),
                "file_content": ("STRING", {
                    "multiline": True,
                    "default": "File content here..."
                }),
                "file_name": ("STRING", {
                    "default": "document.txt"
                }),
            },
            "optional": {
                "file_mime_type": ("STRING", {
                    "default": "text/plain"
                }),
            }
        }
    
    RETURN_TYPES = ("FORM_DATA_ITEM",)
    RETURN_NAMES = ("file_item",)
    FUNCTION = "create_file_item"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    def create_file_item(self, field_name: str, file_content: str, 
                        file_name: str, file_mime_type: str = "text/plain") -> Tuple[Dict]:
        
        form_item = {
            "field_name": field_name,
            "field_type": "file",
            "data": {
                "content": file_content,
                "filename": file_name,
                "mime_type": file_mime_type
            },
            "timestamp": str(hash(field_name + file_content + file_name))
        }
        
        print(f"Form File Item - '{field_name}': {file_name} ({len(file_content)} chars)")
        return (form_item,)
