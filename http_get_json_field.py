import json
from typing import Dict, Any, Tuple, Union

class HTTPGetJSONFieldNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "json_input": ("STRING", {
                    "multiline": True,
                    "default": '{"data": {"message": "Hello World"}, "status": "success"}'
                }),
                "field_path": ("STRING", {
                    "multiline": False,
                    "default": "data.message"
                }),
            },
            "optional": {
                "default_value": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "return_as_string": ("BOOLEAN", {
                    "default": True
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("field_value", "error_message", "found")
    FUNCTION = "get_json_field"
    CATEGORY = "HTTP/API"
    
    def get_json_field(self, json_input: str, field_path: str, 
                      default_value: str = "", return_as_string: bool = True) -> Tuple[str, str, bool]:
        try:
            data = json.loads(json_input)
            
            path_parts = field_path.split('.')
            
            current_value = data
            for part in path_parts:
                if isinstance(current_value, dict) and part in current_value:
                    current_value = current_value[part]
                elif isinstance(current_value, list):
                    try:
                        index = int(part)
                        if 0 <= index < len(current_value):
                            current_value = current_value[index]
                        else:
                            return (default_value, f"List index {index} out of range", False)
                    except ValueError:
                        return (default_value, f"Cannot access list with key '{part}'", False)
                else:
                    return (default_value, f"Field '{part}' not found in path '{field_path}'", False)
            
            if return_as_string:
                if isinstance(current_value, (dict, list)):
                    result_value = json.dumps(current_value, ensure_ascii=False)
                else:
                    result_value = str(current_value)
            else:
                result_value = str(current_value)
            
            print(f"JSON Field Get - Path: {field_path}, Found: {type(current_value).__name__}")
            return (result_value, "", True)
            
        except json.JSONDecodeError as e:
            error_message = f"Invalid JSON format: {str(e)}"
            print(f"JSON Field Error: {error_message}")
            return (default_value, error_message, False)
            
        except Exception as e:
            error_message = f"Error getting field: {str(e)}"
            print(f"JSON Field Error: {error_message}")
            return (default_value, error_message, False)