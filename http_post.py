"""
HTTP POST request node for ComfyUI
Performs POST requests with support for JSON, form data, and file uploads
"""

from typing import Dict, Any, Optional, Union
from .http_client import HTTPClient
from .http_auth import HTTPAuth
from urllib.parse import urljoin
import json

class HTTPPost:
    """HTTP POST Request Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "https://api.example.com/data"}),
                "content_type": (["json", "form", "raw", "form-data"], {"default": "json"}),
            },
            "optional": {
                "session": ("HTTP_SESSION",),
                "auth": ("HTTP_AUTH",),
                "headers": ("STRING", {"default": "{}"}),
                "json_data": ("STRING", {"default": "{}"}),
                "form_data": ("HTTP_FORM_DATA",),
                "raw_data": ("STRING", {"default": ""}),
                "timeout": ("INT", {"default": 30, "min": 1, "max": 300}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
                "allow_redirects": ("BOOLEAN", {"default": True}),
                "cookies": ("STRING", {"default": "{}"}),
                "proxy_url": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("INT", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("status_code", "headers", "content", "json")
    FUNCTION = "make_request"
    CATEGORY = "HTTP/Methods"
    
    def make_request(self, url: str, content_type: str, session: Optional[Dict] = None, 
                    auth: Optional[Dict] = None, headers: str = "{}", json_data: str = "{}", 
                    form_data: Optional[Dict] = None, raw_data: str = "",
                    timeout: int = 30, verify_ssl: bool = True, allow_redirects: bool = True,
                    cookies: str = "{}", proxy_url: str = ""):
        """Make HTTP POST request"""
        
        try:
            # Use session client if provided, otherwise create new one
            if session:
                client = session["client"]
                base_url = session.get("base_url", "")
                if base_url and not url.startswith(("http://", "https://")):
                    url = urljoin(base_url, url)
            else:
                client = HTTPClient()
                client.set_timeout(timeout)
                client.set_ssl_verify(verify_ssl)
                client.allow_redirects = allow_redirects
                
                if proxy_url:
                    client.set_proxy(proxy_url)
            
            # Apply authentication if provided
            if auth:
                HTTPAuth.apply_auth(client, auth)
            
            # Parse headers
            headers_dict = {}
            if headers and headers != "{}":
                try:
                    headers_dict = json.loads(headers)
                    client.set_headers(headers_dict)
                except Exception as e:
                    print(f"Warning: Failed to parse headers: {e}")
            
            # Parse cookies
            if cookies and cookies != "{}":
                try:
                    cookies_dict = json.loads(cookies)
                    client.set_cookies(cookies_dict)
                except Exception as e:
                    print(f"Warning: Failed to parse cookies: {e}")
            
            # Prepare request data based on content type
            request_kwargs = {}
            
            if content_type == "json":
                if json_data and json_data != "{}":
                    try:
                        json_obj = json.loads(json_data)
                        request_kwargs["json_data"] = json_obj
                    except Exception as e:
                        print(f"Warning: Failed to parse JSON data: {e}")
                        request_kwargs["data"] = json_data
            
            elif content_type == "form":
                if json_data and json_data != "{}":
                    try:
                        form_dict = json.loads(json_data)
                        request_kwargs["data"] = form_dict
                    except Exception as e:
                        print(f"Warning: Failed to parse form data: {e}")
                        request_kwargs["data"] = json_data
            
            elif content_type == "raw":
                if raw_data:
                    request_kwargs["data"] = raw_data
                elif json_data and json_data != "{}":
                    request_kwargs["data"] = json_data
            
            elif content_type == "form-data":
                if form_data:
                    files = form_data.get("files", {})
                    data = form_data.get("data", {})
                    if files:
                        request_kwargs["files"] = files
                    if data:
                        request_kwargs["data"] = data
                elif json_data and json_data != "{}":
                    try:
                        form_dict = json.loads(json_data)
                        request_kwargs["data"] = form_dict
                    except Exception as e:
                        print(f"Warning: Failed to parse form data: {e}")
            
            # Make the request
            status_code, response_headers, content = client.post(url, **request_kwargs)
            
            # Convert headers to JSON string
            headers_json = json.dumps(response_headers, indent=2)
            
            # Try to parse content as JSON
            json_content = ""
            try:
                parsed_json = json.loads(content)
                json_content = json.dumps(parsed_json, indent=2)
            except:
                json_content = content
            
            # Close client if not using session
            if not session:
                client.close()
            
            return (status_code, headers_json, content, json_content)
            
        except Exception as e:
            error_msg = f"HTTP POST request failed: {str(e)}"
            print(error_msg)
            return (0, "{}", error_msg, error_msg)