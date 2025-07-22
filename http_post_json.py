import requests
import json
import time
from typing import Dict, Any, Tuple

class HTTPPostJSONNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "url": ("STRING", {
                    "multiline": False,
                    "default": "https://httpbin.org/post"
                }),
                "json_data": ("STRING", {
                    "multiline": True,
                    "default": '{"user": "john", "action": "create", "data": {"title": "Test", "content": "Hello World"}}'
                }),
            },
            "optional": {
                "headers": ("STRING", {
                    "multiline": True,
                    "default": '{"User-Agent": "ComfyUI-HTTPPost/1.0", "Content-Type": "application/json"}'
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
    FUNCTION = "http_post_json"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always run - bypass ComfyUI caching
        return float("NaN")
    
    def http_post_json(self, url: str, json_data: str, headers: str = "",
                      timeout: int = 30, retry_count: int = 1, retry_delay: int = 5) -> Tuple[str, str, int, bool, str]:
        
        request_id = f"post_json_{int(time.time())}"
        last_error = ""
        
        for attempt in range(retry_count):
            try:
                request_headers = {"User-Agent": "ComfyUI-HTTPPost/1.0", "Content-Type": "application/json"}
                if headers:
                    try:
                        parsed_headers = json.loads(headers)
                        request_headers.update(parsed_headers)
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid headers JSON format: {headers}")
                
                print(f"HTTP Post JSON - Attempt {attempt + 1}/{retry_count} - URL: {url}")
                
                try:
                    request_data = json.loads(json_data) if json_data else {}
                except json.JSONDecodeError:
                    last_error = f"Invalid JSON data format: {json_data}"
                    print(f"HTTP Post JSON - Error: {last_error}")
                    continue
                
                print(f"HTTP Post JSON - Sending JSON data ({len(json_data)} chars)")
                
                response = requests.post(
                    url=url,
                    json=request_data,
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
                    print(f"HTTP Post JSON - Success: Request {request_id} completed")
                    return (response_text, response_json, status_code, True, request_id)
                else:
                    last_error = f"HTTP error {status_code}: {response_text[:200]}"
                    
            except requests.exceptions.Timeout:
                last_error = f"Request timeout after {timeout} seconds"
                print(f"HTTP Post JSON - Attempt {attempt + 1} failed: {last_error}")
                
            except requests.exceptions.ConnectionError:
                last_error = f"Connection error to {url}"
                print(f"HTTP Post JSON - Attempt {attempt + 1} failed: {last_error}")
                
            except Exception as e:
                last_error = f"HTTP Post JSON Error: {str(e)}"
                print(f"HTTP Post JSON - Attempt {attempt + 1} failed: {last_error}")
            
            if attempt < retry_count - 1:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
        
        print(f"HTTP Post JSON - All attempts failed for request {request_id}")
        return (last_error, "{}", 0, False, request_id)
