"""
HTTP Form Data Concatenation node for ComfyUI
Combines multiple form data objects into one
"""

from typing import Dict, Any, Optional

class HTTPFormDataConcat:
    """Form Data Concatenation Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "form_data1": ("HTTP_FORM_DATA",),
            },
            "optional": {
                "form_data2": ("HTTP_FORM_DATA",),
                "form_data3": ("HTTP_FORM_DATA",),
                "form_data4": ("HTTP_FORM_DATA",),
                "form_data5": ("HTTP_FORM_DATA",),
                "overwrite_duplicates": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("HTTP_FORM_DATA",)
    RETURN_NAMES = ("combined_form_data",)
    FUNCTION = "concat_form_data"
    CATEGORY = "HTTP/Form Data"
    
    def concat_form_data(self, form_data1: Dict[str, Any], form_data2: Optional[Dict[str, Any]] = None,
                        form_data3: Optional[Dict[str, Any]] = None, form_data4: Optional[Dict[str, Any]] = None,
                        form_data5: Optional[Dict[str, Any]] = None, overwrite_duplicates: bool = True):
        """Concatenate multiple form data objects"""
        
        combined_data = {"data": {}, "files": {}}
        
        # List of form data objects to process
        form_data_list = [form_data1, form_data2, form_data3, form_data4, form_data5]
        
        for form_data in form_data_list:
            if form_data is None:
                continue
            
            # Merge data fields
            data_fields = form_data.get("data", {})
            for key, value in data_fields.items():
                if key in combined_data["data"] and not overwrite_duplicates:
                    # If key exists and we don't want to overwrite, append a suffix
                    suffix = 1
                    new_key = f"{key}_{suffix}"
                    while new_key in combined_data["data"]:
                        suffix += 1
                        new_key = f"{key}_{suffix}"
                    combined_data["data"][new_key] = value
                else:
                    combined_data["data"][key] = value
            
            # Merge file fields
            file_fields = form_data.get("files", {})
            for key, value in file_fields.items():
                if key in combined_data["files"] and not overwrite_duplicates:
                    # If key exists and we don't want to overwrite, append a suffix
                    suffix = 1
                    new_key = f"{key}_{suffix}"
                    while new_key in combined_data["files"]:
                        suffix += 1
                        new_key = f"{key}_{suffix}"
                    combined_data["files"][new_key] = value
                else:
                    combined_data["files"][key] = value
        
        return (combined_data,)