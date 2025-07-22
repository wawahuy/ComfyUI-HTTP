from typing import Dict, Any, Tuple, List, Optional

class HTTPFormDataNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "optional": {
                "item1": ("FORM_DATA_ITEM",),
                "item2": ("FORM_DATA_ITEM",),
                "item3": ("FORM_DATA_ITEM",),
                "item4": ("FORM_DATA_ITEM",),
                "item5": ("FORM_DATA_ITEM",),
            }
        }
    
    RETURN_TYPES = ("FORM_DATA",)
    RETURN_NAMES = ("form_data",)
    FUNCTION = "combine_form_data"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    def combine_form_data(self, **kwargs):
        items = []
        
        for key, item in kwargs.items():
            if item is not None:
                items.append(item)
                print(f"Form Data - Added: {item['field_name']}")
        
        form_data = {
            "items": items,
            "field_count": len(items)
        }
        
        print(f"Form Data - Total: {len(items)} items")
        return (form_data,)
