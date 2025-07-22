import requests
import json
import time
from typing import Dict, Any, Tuple

class HTTPGetNode:
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "url": ("STRING", {
                    "multiline": False,
                    "default": "https://httpbin.org/json"
                }),
            },
            "optional": {
                "headers": ("STRING", {
                    "multiline": True,
                    "default": '{"Content-Type": "application/json", "User-Agent": "ComfyUI-HTTPPull-Starter/1.0"}'
                }),
                "params": ("STRING", {
                    "multiline": True,
                    "default": '{"workflow": "started", "source": "comfyui"}'
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
    RETURN_NAMES = ("response_text", "response_json", "status_code", "success", "workflow_id")
    FUNCTION = "http_get"
    CATEGORY = "HTTP/API"
    OUTPUT_NODE = False
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always run - bypass ComfyUI caching
        return float("NaN")
    
    def http_get(self, url: str, headers: str = "", params: str = "",
                       timeout: int = 30, retry_count: int = 1, retry_delay: int = 5) -> Tuple[str, str, int, bool, str]:
        
        workflow_id = f"wf_{int(time.time())}"
        
        last_error = ""
        
        for attempt in range(retry_count):
            try:
                request_headers = {"Content-Type": "application/json"}
                if headers:
                    try:
                        parsed_headers = json.loads(headers)
                        request_headers.update(parsed_headers)
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid headers JSON format: {headers}")
                
                request_params = {}
                if params:
                    try:
                        request_params = json.loads(params)
                        request_params["workflow_id"] = workflow_id
                        request_params["attempt"] = attempt + 1
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid params JSON format: {params}")
                
                print(f"HTTP Get - Attempt {attempt + 1}/{retry_count} - URL: {url}")
                
                response = requests.get(
                    url=url,
                    headers=request_headers,
                    params=request_params,
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
                    print(f"HTTP Get - Success: Workflow {workflow_id} started")
                    return (response_text, response_json, status_code, True, workflow_id)
                else:
                    last_error = f"HTTP error {status_code}: {response_text[:200]}"
                    
            except requests.exceptions.Timeout:
                last_error = f"Request timeout after {timeout} seconds"
                print(f"HTTP Get - Attempt {attempt + 1} failed: {last_error}")
                
            except requests.exceptions.ConnectionError:
                last_error = f"Connection error to {url}"
                print(f"HTTP Get - Attempt {attempt + 1} failed: {last_error}")
                
            except Exception as e:
                last_error = f"HTTP Get Error: {str(e)}"
                print(f"HTTP Get - Attempt {attempt + 1} failed: {last_error}")
            
            if attempt < retry_count - 1:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
        
        print(f"HTTP Get - All attempts failed for workflow {workflow_id}")
        return (last_error, "{}", 0, False, workflow_id)
