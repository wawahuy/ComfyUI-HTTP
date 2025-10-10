"""
HTTP OPTIONS request node for ComfyUI
Performs OPTIONS requests to get allowed methods and CORS information
"""

from typing import Dict, Any, Optional
from .http_client import HTTPClient
from .http_auth import HTTPAuth
from urllib.parse import urljoin
import json

class HTTPOptions:
    """HTTP OPTIONS Request Node for ComfyUI"""
    
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
                "timeout": ("INT", {"default": 30, "min": 1, "max": 300}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
                "allow_redirects": ("BOOLEAN", {"default": True}),
                "cookies": ("STRING", {"default": "{}"}),
                "proxy_url": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("INT", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("status_code", "headers", "allowed_methods", "cors_headers", "content")
    FUNCTION = "make_request"
    CATEGORY = "HTTP/Methods"
    
    def make_request(self, url: str, session: Optional[Dict] = None, auth: Optional[Dict] = None,
                    headers: str = "{}", timeout: int = 30, verify_ssl: bool = True, 
                    allow_redirects: bool = True, cookies: str = "{}", proxy_url: str = ""):
        """Make HTTP OPTIONS request"""
        
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
            
            # Make the request
            status_code, response_headers, content = client.options(url)
            
            # Convert headers to JSON string
            headers_json = json.dumps(response_headers, indent=2)
            
            # Extract allowed methods
            allowed_methods = response_headers.get("allow", response_headers.get("Allow", ""))
            
            # Extract CORS headers
            cors_headers = {}
            cors_keys = [
                "access-control-allow-origin",
                "access-control-allow-methods", 
                "access-control-allow-headers",
                "access-control-allow-credentials",
                "access-control-max-age",
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers", 
                "Access-Control-Allow-Credentials",
                "Access-Control-Max-Age"
            ]
            
            for key in cors_keys:
                if key in response_headers:
                    cors_headers[key] = response_headers[key]
            
            cors_headers_json = json.dumps(cors_headers, indent=2)
            
            # Close client if not using session
            if not session:
                client.close()
            
            return (status_code, headers_json, allowed_methods, cors_headers_json, content)
            
        except Exception as e:
            error_msg = f"HTTP OPTIONS request failed: {str(e)}"
            print(error_msg)
            return (0, "{}", "", "{}", error_msg)