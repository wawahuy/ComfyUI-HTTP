"""
HTTP HEAD request node for ComfyUI
Performs HEAD requests to get response headers without body
"""

from typing import Dict, Any, Optional
from .http_client import HTTPClient
from .http_auth import HTTPAuth
from urllib.parse import urljoin
import json

class HTTPHead:
    """HTTP HEAD Request Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "https://api.example.com/data"}),
            },
            "optional": {
                "session": ("HTTP_SESSION",),
                "auth": ("HTTP_AUTH",),
                "headers": ("STRING", {"default": "{}"}),
                "params": ("STRING", {"default": "{}"}),
                "timeout": ("INT", {"default": 30, "min": 1, "max": 300}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
                "allow_redirects": ("BOOLEAN", {"default": True}),
                "cookies": ("STRING", {"default": "{}"}),
                "proxy_url": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("INT", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("status_code", "headers", "content_length", "content_type")
    FUNCTION = "make_request"
    CATEGORY = "HTTP/Methods"
    
    def make_request(self, url: str, session: Optional[Dict] = None, auth: Optional[Dict] = None,
                    headers: str = "{}", params: str = "{}", timeout: int = 30,
                    verify_ssl: bool = True, allow_redirects: bool = True,
                    cookies: str = "{}", proxy_url: str = ""):
        """Make HTTP HEAD request"""
        
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
            
            # Parse query parameters
            params_dict = {}
            if params and params != "{}":
                try:
                    params_dict = json.loads(params)
                except Exception as e:
                    print(f"Warning: Failed to parse params: {e}")
            
            # Prepare request kwargs
            request_kwargs = {}
            if params_dict:
                request_kwargs["params"] = params_dict
            
            # Make the request
            status_code, response_headers, _ = client.head(url, **request_kwargs)
            
            # Convert headers to JSON string
            headers_json = json.dumps(response_headers, indent=2)
            
            # Extract common headers
            content_length = response_headers.get("content-length", response_headers.get("Content-Length", ""))
            content_type = response_headers.get("content-type", response_headers.get("Content-Type", ""))
            
            # Close client if not using session
            if not session:
                client.close()
            
            return (status_code, headers_json, content_length, content_type)
            
        except Exception as e:
            error_msg = f"HTTP HEAD request failed: {str(e)}"
            print(error_msg)
            return (0, "{}", "", "")