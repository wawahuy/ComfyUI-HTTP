import requests
import json
import time
from typing import Dict, Any, Tuple

class HTTPPostRawNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "url": ("STRING", {
                    "multiline": False,
                    "default": "https://httpbin.org/post"
                }),
                "raw_data": ("STRING", {
                    "multiline": True,
                    "default": "name=John&email=john@example.com&message=Hello World"
                }),
            },
            "optional": {
                "content_type": ("STRING", {
                    "default": "text/plain"
                }),
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
    FUNCTION = "http_post_raw"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always run - bypass ComfyUI caching
        return float("NaN")
    
    def http_post_raw(self, url: str, raw_data: str, content_type: str = "text/plain", 
                     headers: str = "", timeout: int = 30, retry_count: int = 1, 
                     retry_delay: int = 5) -> Tuple[str, str, int, bool, str]:
        
        request_id = f"post_raw_{int(time.time())}"
        last_error = ""
        
        for attempt in range(retry_count):
            try:
                request_headers = {"User-Agent": "ComfyUI-HTTPPost/1.0", "Content-Type": content_type}
                if headers:
                    try:
                        parsed_headers = json.loads(headers)
                        request_headers.update(parsed_headers)
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid headers JSON format: {headers}")
                
                print(f"HTTP Post Raw - Attempt {attempt + 1}/{retry_count} - URL: {url}")
                print(f"HTTP Post Raw - Content-Type: {content_type}")
                print(f"HTTP Post Raw - Data length: {len(raw_data)} chars")
                
                response = requests.post(
                    url=url,
                    data=raw_data,
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
                    print(f"HTTP Post Raw - Success: Request {request_id} completed")
                    return (response_text, response_json, status_code, True, request_id)
                else:
                    last_error = f"HTTP error {status_code}: {response_text[:200]}"
                    
            except requests.exceptions.Timeout:
                last_error = f"Request timeout after {timeout} seconds"
                print(f"HTTP Post Raw - Attempt {attempt + 1} failed: {last_error}")
                
            except requests.exceptions.ConnectionError:
                last_error = f"Connection error to {url}"
                print(f"HTTP Post Raw - Attempt {attempt + 1} failed: {last_error}")
                
            except Exception as e:
                last_error = f"HTTP Post Raw Error: {str(e)}"
                print(f"HTTP Post Raw - Attempt {attempt + 1} failed: {last_error}")
            
            if attempt < retry_count - 1:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
        
        print(f"HTTP Post Raw - All attempts failed for request {request_id}")
        return (last_error, "{}", 0, False, request_id)
