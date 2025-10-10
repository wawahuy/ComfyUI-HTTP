"""
HTTP Session Manager for ComfyUI
Manages persistent HTTP sessions with configuration and state
"""

from typing import Dict, Any, Optional
from .http_client import HTTPClient

class HTTPSessionManager:
    """HTTP Session Manager Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "session_name": ("STRING", {"default": "default_session"}),
                "base_url": ("STRING", {"default": ""}),
                "timeout": ("INT", {"default": 30, "min": 1, "max": 300}),
            },
            "optional": {
                "headers": ("STRING", {"default": "{}"}),
                "cookies": ("STRING", {"default": "{}"}),
                "auth_type": (["none", "basic", "bearer", "api_key", "token"], {"default": "none"}),
                "username": ("STRING", {"default": ""}),
                "password": ("STRING", {"default": ""}),
                "token": ("STRING", {"default": ""}),
                "api_key": ("STRING", {"default": ""}),
                "api_key_header": ("STRING", {"default": "X-API-Key"}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
                "proxy_url": ("STRING", {"default": ""}),
                "max_retries": ("INT", {"default": 3, "min": 1, "max": 10}),
                "retry_delay": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0}),
            }
        }
    
    RETURN_TYPES = ("HTTP_SESSION",)
    RETURN_NAMES = ("session",)
    FUNCTION = "create_session"
    CATEGORY = "HTTP/Session"
    
    # Global session storage
    _sessions: Dict[str, HTTPClient] = {}
    
    def create_session(self, session_name: str, base_url: str, timeout: int,
                      headers: str = "{}", cookies: str = "{}", auth_type: str = "none",
                      username: str = "", password: str = "", token: str = "", 
                      api_key: str = "", api_key_header: str = "X-API-Key",
                      verify_ssl: bool = True, proxy_url: str = "",
                      max_retries: int = 3, retry_delay: float = 1.0):
        """Create or get existing HTTP session"""
        
        # Create new client or get existing one
        if session_name not in self._sessions:
            self._sessions[session_name] = HTTPClient()
        
        client = self._sessions[session_name]
        
        # Configure client
        client.set_timeout(timeout)
        client.set_ssl_verify(verify_ssl)
        client.max_retries = max_retries
        client.retry_delay = retry_delay
        
        # Set proxy if provided
        if proxy_url:
            client.set_proxy(proxy_url)
        
        # Parse and set headers
        try:
            import json
            headers_dict = json.loads(headers) if headers and headers != "{}" else {}
            if headers_dict:
                client.set_headers(headers_dict)
        except Exception:
            pass
        
        # Parse and set cookies
        try:
            import json
            cookies_dict = json.loads(cookies) if cookies and cookies != "{}" else {}
            if cookies_dict:
                client.set_cookies(cookies_dict)
        except Exception:
            pass
        
        # Set authentication
        if auth_type != "none":
            client.set_auth(auth_type, username, password, token, api_key, api_key_header)
        
        # Store session configuration
        session_config = {
            "client": client,
            "base_url": base_url,
            "session_name": session_name,
            "timeout": timeout,
            "verify_ssl": verify_ssl,
            "max_retries": max_retries,
            "retry_delay": retry_delay
        }
        
        return (session_config,)
    
    @classmethod
    def get_session(cls, session_name: str) -> Optional[HTTPClient]:
        """Get existing session by name"""
        return cls._sessions.get(session_name)
    
    @classmethod
    def close_session(cls, session_name: str):
        """Close and remove session"""
        if session_name in cls._sessions:
            cls._sessions[session_name].close()
            del cls._sessions[session_name]
    
    @classmethod
    def close_all_sessions(cls):
        """Close all sessions"""
        for client in cls._sessions.values():
            client.close()
        cls._sessions.clear()