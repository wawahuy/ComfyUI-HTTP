from typing import Dict, Any, Tuple

class HTTPFormDataConcatNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "form_data_1": ("FORM_DATA",),
                "form_data_2": ("FORM_DATA",),
            }
        }
    
    RETURN_TYPES = ("FORM_DATA",)
    RETURN_NAMES = ("combined_form_data",)
    FUNCTION = "concat_form_data"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    def concat_form_data(self, form_data_1, form_data_2):
        all_items = []
        
        # Add items from first form
        if form_data_1 and "items" in form_data_1:
            all_items.extend(form_data_1["items"])
            print(f"Form Concat - Added {len(form_data_1['items'])} items from form 1")
        
        # Add items from second form
        if form_data_2 and "items" in form_data_2:
            all_items.extend(form_data_2["items"])
            print(f"Form Concat - Added {len(form_data_2['items'])} items from form 2")
        
        combined_form = {
            "items": all_items,
            "field_count": len(all_items)
        }
        
        print(f"Form Concat - Total combined: {len(all_items)} items")
        return (combined_form,)
