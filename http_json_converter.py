"""
HTTP JSON conversion and manipulation nodes for ComfyUI
Handles JSON parsing, formatting, and field extraction
"""

import json
from typing import Any, Dict, Union, List

try:
    from jsonpath_ng import parse as jsonpath_parse
    from jsonpath_ng.ext import parse as jsonpath_ext_parse
    JSONPATH_AVAILABLE = True
except ImportError:
    JSONPATH_AVAILABLE = False
    print("Warning: jsonpath-ng not available. JSONPath functionality will be limited.")

class HTTPConvertJSON:
    """JSON Converter Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_data": ("STRING", {"default": "{}"}),
                "operation": (["parse", "stringify", "format", "minify"], {"default": "parse"}),
            },
            "optional": {
                "indent": ("INT", {"default": 2, "min": 0, "max": 8}),
                "sort_keys": ("BOOLEAN", {"default": False}),
                "ensure_ascii": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("result", "formatted")
    FUNCTION = "convert_json"
    CATEGORY = "HTTP/JSON"
    
    def convert_json(self, input_data: str, operation: str, indent: int = 2, 
                    sort_keys: bool = False, ensure_ascii: bool = False):
        """Convert and format JSON data"""
        
        try:
            if operation == "parse":
                # Parse JSON string and return formatted version
                parsed_data = json.loads(input_data)
                formatted = json.dumps(parsed_data, indent=indent, sort_keys=sort_keys, 
                                     ensure_ascii=ensure_ascii)
                return (json.dumps(parsed_data), formatted)
            
            elif operation == "stringify":
                # Convert to JSON string
                if isinstance(input_data, str):
                    try:
                        # Try to parse as JSON first
                        parsed_data = json.loads(input_data)
                        result = json.dumps(parsed_data, separators=(',', ':'))
                        formatted = json.dumps(parsed_data, indent=indent, sort_keys=sort_keys,
                                             ensure_ascii=ensure_ascii)
                    except:
                        # If not valid JSON, treat as string value
                        result = json.dumps(input_data)
                        formatted = json.dumps(input_data, indent=indent)
                else:
                    result = json.dumps(input_data, separators=(',', ':'))
                    formatted = json.dumps(input_data, indent=indent, sort_keys=sort_keys,
                                         ensure_ascii=ensure_ascii)
                return (result, formatted)
            
            elif operation == "format":
                # Format JSON with proper indentation
                parsed_data = json.loads(input_data)
                formatted = json.dumps(parsed_data, indent=indent, sort_keys=sort_keys,
                                     ensure_ascii=ensure_ascii)
                return (formatted, formatted)
            
            elif operation == "minify":
                # Minify JSON (remove whitespace)
                parsed_data = json.loads(input_data)
                minified = json.dumps(parsed_data, separators=(',', ':'))
                return (minified, minified)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            return (error_msg, error_msg)
        except Exception as e:
            error_msg = f"JSON conversion error: {str(e)}"
            return (error_msg, error_msg)

class HTTPGetJSONField:
    """JSON Field Extractor Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_data": ("STRING", {"default": "{}"}),
                "field_path": ("STRING", {"default": "$.data"}),
                "extraction_method": (["jsonpath", "simple", "nested"], {"default": "jsonpath"}),
            },
            "optional": {
                "default_value": ("STRING", {"default": ""}),
                "return_type": (["string", "json", "auto"], {"default": "auto"}),
                "multiple_results": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("value", "formatted_value", "count")
    FUNCTION = "extract_field"
    CATEGORY = "HTTP/JSON"
    
    def extract_field(self, json_data: str, field_path: str, extraction_method: str,
                     default_value: str = "", return_type: str = "auto", 
                     multiple_results: bool = False):
        """Extract field from JSON data"""
        
        try:
            # Parse JSON data
            data = json.loads(json_data)
            
            results = []
            
            if extraction_method == "jsonpath":
                # Use JSONPath to extract data
                if JSONPATH_AVAILABLE:
                    try:
                        jsonpath_expr = jsonpath_ext_parse(field_path)
                        matches = jsonpath_expr.find(data)
                        results = [match.value for match in matches]
                    except Exception as e:
                        print(f"JSONPath error: {e}")
                        # Fallback to simple extraction
                        results = self._simple_extract(data, field_path, default_value)
                else:
                    print("JSONPath not available, using simple extraction")
                    results = self._simple_extract(data, field_path, default_value)
            
            elif extraction_method == "simple":
                # Simple dot notation extraction (e.g., "data.user.name")
                results = self._simple_extract(data, field_path, default_value)
            
            elif extraction_method == "nested":
                # Nested bracket notation (e.g., "data['user']['name']")
                results = self._nested_extract(data, field_path, default_value)
            
            # Handle results
            if not results:
                return (default_value, default_value, 0)
            
            if multiple_results:
                # Return all results as JSON array
                if return_type == "json":
                    result = json.dumps(results, indent=2)
                else:
                    result = json.dumps(results)
                formatted = json.dumps(results, indent=2)
                return (result, formatted, len(results))
            else:
                # Return first result
                first_result = results[0]
                
                if return_type == "string":
                    result = str(first_result)
                    formatted = str(first_result)
                elif return_type == "json":
                    result = json.dumps(first_result, indent=2)
                    formatted = result
                else:  # auto
                    if isinstance(first_result, (dict, list)):
                        result = json.dumps(first_result)
                        formatted = json.dumps(first_result, indent=2)
                    else:
                        result = str(first_result)
                        formatted = str(first_result)
                
                return (result, formatted, len(results))
        
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            return (error_msg, error_msg, 0)
        except Exception as e:
            error_msg = f"Field extraction error: {str(e)}"
            return (error_msg, error_msg, 0)
    
    def _simple_extract(self, data: Any, path: str, default: str) -> List[Any]:
        """Extract using simple dot notation"""
        try:
            parts = path.strip().split('.')
            current = data
            
            for part in parts:
                if part.startswith('$'):
                    continue  # Skip JSONPath root indicator
                
                if isinstance(current, dict):
                    current = current.get(part, None)
                elif isinstance(current, list) and part.isdigit():
                    index = int(part)
                    current = current[index] if 0 <= index < len(current) else None
                else:
                    return [default] if default else []
                
                if current is None:
                    return [default] if default else []
            
            return [current] if current is not None else ([default] if default else [])
        
        except Exception:
            return [default] if default else []
    
    def _nested_extract(self, data: Any, path: str, default: str) -> List[Any]:
        """Extract using nested bracket notation"""
        try:
            # Simple evaluation of bracket notation
            # Note: This is a basic implementation and might not handle all cases
            current = data
            
            # Remove quotes and parse bracket notation
            path = path.strip()
            if path.startswith('$'):
                path = path[1:]
            
            # Split by brackets and dots
            import re
            parts = re.findall(r"(?:\['([^']+)'\]|\[(\d+)\]|\.([^.\[]+)|([^.\[]+))", path)
            
            for part_tuple in parts:
                part = next((p for p in part_tuple if p), None)
                if not part:
                    continue
                
                if isinstance(current, dict):
                    current = current.get(part, None)
                elif isinstance(current, list) and part.isdigit():
                    index = int(part)
                    current = current[index] if 0 <= index < len(current) else None
                else:
                    return [default] if default else []
                
                if current is None:
                    return [default] if default else []
            
            return [current] if current is not None else ([default] if default else [])
        
        except Exception:
            return [default] if default else []