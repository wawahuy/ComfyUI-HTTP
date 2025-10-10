"""
HTTP Authentication node for ComfyUI
Handles various authentication methods for HTTP requests
"""

from typing import Dict, Any, Tuple

class HTTPAuth:
    """HTTP Authentication Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "auth_type": (["none", "basic", "bearer", "api_key", "token", "oauth2"], {"default": "none"}),
            },
            "optional": {
                "username": ("STRING", {"default": ""}),
                "password": ("STRING", {"default": ""}),
                "token": ("STRING", {"default": ""}),
                "api_key": ("STRING", {"default": ""}),
                "api_key_header": ("STRING", {"default": "X-API-Key"}),
                "client_id": ("STRING", {"default": ""}),
                "client_secret": ("STRING", {"default": ""}),
                "oauth_token_url": ("STRING", {"default": ""}),
                "scope": ("STRING", {"default": ""}),
                "custom_headers": ("STRING", {"default": "{}"}),
            }
        }
    
    RETURN_TYPES = ("HTTP_AUTH",)
    RETURN_NAMES = ("auth_config",)
    FUNCTION = "create_auth"
    CATEGORY = "HTTP/Authentication"
    
    def create_auth(self, auth_type: str, username: str = "", password: str = "",
                   token: str = "", api_key: str = "", api_key_header: str = "X-API-Key",
                   client_id: str = "", client_secret: str = "", oauth_token_url: str = "",
                   scope: str = "", custom_headers: str = "{}"):
        """Create authentication configuration"""
        
        auth_config = {
            "type": auth_type,
            "username": username,
            "password": password,
            "token": token,
            "api_key": api_key,
            "api_key_header": api_key_header,
            "client_id": client_id,
            "client_secret": client_secret,
            "oauth_token_url": oauth_token_url,
            "scope": scope,
            "custom_headers": custom_headers
        }
        
        return (auth_config,)
    
    @staticmethod
    def apply_auth(client, auth_config: Dict[str, Any]):
        """Apply authentication configuration to HTTP client"""
        auth_type = auth_config.get("type", "none")
        
        if auth_type == "basic":
            username = auth_config.get("username", "")
            password = auth_config.get("password", "")
            if username and password:
                client.set_auth("basic", username=username, password=password)
        
        elif auth_type == "bearer":
            token = auth_config.get("token", "")
            if token:
                client.set_auth("bearer", token=token)
        
        elif auth_type == "api_key":
            api_key = auth_config.get("api_key", "")
            api_key_header = auth_config.get("api_key_header", "X-API-Key")
            if api_key:
                client.set_auth("api_key", api_key=api_key, api_key_header=api_key_header)
        
        elif auth_type == "token":
            token = auth_config.get("token", "")
            if token:
                client.set_auth("token", token=token)
        
        elif auth_type == "oauth2":
            # OAuth2 implementation would require additional OAuth2 flow
            # For now, we'll just set the token if provided
            token = auth_config.get("token", "")
            if token:
                client.set_auth("bearer", token=token)
        
        # Apply custom headers
        custom_headers = auth_config.get("custom_headers", "{}")
        if custom_headers and custom_headers != "{}":
            try:
                import json
                headers_dict = json.loads(custom_headers)
                client.set_headers(headers_dict)
            except Exception:
                pass
    
    @staticmethod
    def get_oauth2_token(client_id: str, client_secret: str, token_url: str, 
                        scope: str = "") -> Tuple[bool, str]:
        """Get OAuth2 token using client credentials flow"""
        try:
            import requests
            
            data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            }
            
            if scope:
                data["scope"] = scope
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                return True, access_token
            else:
                return False, "No access token in response"
                
        except Exception as e:
            return False, f"OAuth2 token request failed: {str(e)}"