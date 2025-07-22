import requests
import json
import time
from typing import Dict, Any, Tuple

class HTTPPostFormDataNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "url": ("STRING", {
                    "multiline": False,
                    "default": "https://httpbin.org/post"
                }),
                "form_data": ("FORM_DATA",),
            },
            "optional": {
                "headers": ("STRING", {
                    "multiline": True,
                    "default": '{"User-Agent": "ComfyUI-HTTPPost/1.0"}'
                }),
                "timeout": ("INT", {
                    "default": 30,
                    "min": 5,
                    "max": 300,
                    "step": 5
                }),
                "retry_count": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 5,
                    "step": 1
                }),
                "retry_delay": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 30,
                    "step": 1
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("response_text", "response_json", "status_code", "success", "request_id")
    FUNCTION = "http_post_form_data"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always run - bypass ComfyUI caching
        return float("NaN")
    
    def http_post_form_data(self, url: str, form_data, headers: str = "",
                           timeout: int = 30, retry_count: int = 1, retry_delay: int = 5) -> Tuple[str, str, int, bool, str]:
        
        request_id = f"post_form_{int(time.time())}"
        last_error = ""
        
        for attempt in range(retry_count):
            try:
                request_headers = {"User-Agent": "ComfyUI-HTTPPost/1.0"}
                if headers:
                    try:
                        parsed_headers = json.loads(headers)
                        request_headers.update(parsed_headers)
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid headers JSON format: {headers}")
                
                print(f"HTTP Post Form Data - Attempt {attempt + 1}/{retry_count} - URL: {url}")
                
                if form_data is None or "items" not in form_data:
                    print("HTTP Post Form Data - No form data provided")
                    response = requests.post(
                        url=url,
                        headers=request_headers,
                        timeout=timeout
                    )
                else:
                    form_fields = {}
                    files = {}
                    
                    for item in form_data["items"]:
                        field_name = item["field_name"]
                        field_type = item["field_type"]
                        data = item.get("data")
                        
                        if data is None:
                            continue
                        
                        if field_type == "text":
                            form_fields[field_name] = data
                            print(f"HTTP Post Form Data - Text field: {field_name}")
                            
                        elif field_type == "file":
                            if isinstance(data, dict):
                                files[field_name] = (
                                    data["filename"], 
                                    data["content"], 
                                    data["mime_type"]
                                )
                                print(f"HTTP Post Form Data - File field: {field_name} ({data['filename']})")
                            
                        elif field_type == "image":
                            if isinstance(data, dict):
                                files[field_name] = (
                                    data["filename"], 
                                    data["content"], 
                                    data["mime_type"]
                                )
                                print(f"HTTP Post Form Data - Image field: {field_name} ({data['filename']})")
                    
                    if "Content-Type" in request_headers:
                        del request_headers["Content-Type"]
                    
                    print(f"HTTP Post Form Data - Sending {len(form_fields)} text fields and {len(files)} files")
                    
                    response = requests.post(
                        url=url,
                        data=form_fields,
                        files=files if files else None,
                        headers=request_headers,
                        timeout=timeout
                    )
                
                response_text = response.text
                
                response_json = "{}"
                try:
                    json.loads(response_text)
                    response_json = response_text
                except json.JSONDecodeError:
                    response_json = "{}"
                
                status_code = response.status_code
                success = 200 <= status_code < 300
                
                if success:
                    print(f"HTTP Post Form Data - Success: Request {request_id} completed")
                    return (response_text, response_json, status_code, True, request_id)
                else:
                    last_error = f"HTTP error {status_code}: {response_text[:200]}"
                    
            except requests.exceptions.Timeout:
                last_error = f"Request timeout after {timeout} seconds"
                print(f"HTTP Post Form Data - Attempt {attempt + 1} failed: {last_error}")
                
            except requests.exceptions.ConnectionError:
                last_error = f"Connection error to {url}"
                print(f"HTTP Post Form Data - Attempt {attempt + 1} failed: {last_error}")
                
            except Exception as e:
                last_error = f"HTTP Post Form Data Error: {str(e)}"
                print(f"HTTP Post Form Data - Attempt {attempt + 1} failed: {last_error}")
            
            if attempt < retry_count - 1:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
        
        print(f"HTTP Post Form Data - All attempts failed for request {request_id}")
        return (last_error, "{}", 0, False, request_id)
