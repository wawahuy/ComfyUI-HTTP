"""
HTTP Utilities node for ComfyUI
Provides various HTTP utility functions
"""

import json
import urllib.parse
from typing import Dict, Any, Tuple
import re
import base64
import hashlib
import hmac
import time

class HTTPUtils:
    """HTTP Utilities Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "operation": ([
                    "url_encode", "url_decode", "base64_encode", "base64_decode",
                    "json_escape", "json_unescape", "html_escape", "html_unescape",
                    "generate_timestamp", "generate_uuid", "generate_signature",
                    "parse_url", "build_url", "extract_domain", "validate_email",
                    "generate_bearer_token", "create_basic_auth"
                ], {"default": "url_encode"}),
                "input_data": ("STRING", {"default": ""}),
            },
            "optional": {
                "secret_key": ("STRING", {"default": ""}),
                "algorithm": (["sha1", "sha256", "md5"], {"default": "sha256"}),
                "url_base": ("STRING", {"default": "https://api.example.com"}),
                "url_path": ("STRING", {"default": "/endpoint"}),
                "url_params": ("STRING", {"default": "{}"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("result", "info", "success")
    FUNCTION = "execute_utility"
    CATEGORY = "HTTP/Utilities"
    
    def execute_utility(self, operation: str, input_data: str, secret_key: str = "",
                       algorithm: str = "sha256", url_base: str = "https://api.example.com",
                       url_path: str = "/endpoint", url_params: str = "{}") -> Tuple[str, str, bool]:
        """Execute various HTTP utility operations"""
        
        try:
            if operation == "url_encode":
                result = urllib.parse.quote(input_data, safe='')
                info = f"URL encoded {len(input_data)} characters"
                return (result, info, True)
            
            elif operation == "url_decode":
                result = urllib.parse.unquote(input_data)
                info = f"URL decoded to {len(result)} characters"
                return (result, info, True)
            
            elif operation == "base64_encode":
                encoded = base64.b64encode(input_data.encode('utf-8')).decode('utf-8')
                info = f"Base64 encoded {len(input_data)} characters to {len(encoded)} characters"
                return (encoded, info, True)
            
            elif operation == "base64_decode":
                try:
                    decoded = base64.b64decode(input_data).decode('utf-8')
                    info = f"Base64 decoded {len(input_data)} characters to {len(decoded)} characters"
                    return (decoded, info, True)
                except Exception as e:
                    return (f"Decode error: {str(e)}", f"Base64 decode failed", False)
            
            elif operation == "json_escape":
                escaped = json.dumps(input_data)
                info = f"JSON escaped string"
                return (escaped, info, True)
            
            elif operation == "json_unescape":
                try:
                    unescaped = json.loads(input_data)
                    info = f"JSON unescaped string"
                    return (str(unescaped), info, True)
                except Exception as e:
                    return (f"Unescape error: {str(e)}", f"JSON unescape failed", False)
            
            elif operation == "html_escape":
                import html
                escaped = html.escape(input_data)
                info = f"HTML escaped {len(input_data)} characters"
                return (escaped, info, True)
            
            elif operation == "html_unescape":
                import html
                unescaped = html.unescape(input_data)
                info = f"HTML unescaped {len(input_data)} characters"
                return (unescaped, info, True)
            
            elif operation == "generate_timestamp":
                timestamp = str(int(time.time()))
                iso_timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                info = f"Generated timestamp: {iso_timestamp}"
                return (timestamp, info, True)
            
            elif operation == "generate_uuid":
                import uuid
                generated_uuid = str(uuid.uuid4())
                info = f"Generated UUID v4"
                return (generated_uuid, info, True)
            
            elif operation == "generate_signature":
                if not secret_key:
                    return ("Error: Secret key required", "Missing secret key", False)
                
                if algorithm == "sha1":
                    signature = hmac.new(secret_key.encode(), input_data.encode(), hashlib.sha1).hexdigest()
                elif algorithm == "sha256":
                    signature = hmac.new(secret_key.encode(), input_data.encode(), hashlib.sha256).hexdigest()
                elif algorithm == "md5":
                    signature = hmac.new(secret_key.encode(), input_data.encode(), hashlib.md5).hexdigest()
                else:
                    return ("Error: Unsupported algorithm", "Invalid algorithm", False)
                
                info = f"Generated {algorithm.upper()} HMAC signature"
                return (signature, info, True)
            
            elif operation == "parse_url":
                try:
                    parsed = urllib.parse.urlparse(input_data)
                    result = json.dumps({
                        "scheme": parsed.scheme,
                        "netloc": parsed.netloc,
                        "path": parsed.path,
                        "params": parsed.params,
                        "query": parsed.query,
                        "fragment": parsed.fragment,
                        "hostname": parsed.hostname,
                        "port": parsed.port,
                        "username": parsed.username,
                        "password": parsed.password
                    }, indent=2)
                    info = f"Parsed URL components"
                    return (result, info, True)
                except Exception as e:
                    return (f"Parse error: {str(e)}", "URL parsing failed", False)
            
            elif operation == "build_url":
                try:
                    params_dict = json.loads(url_params) if url_params and url_params != "{}" else {}
                    
                    # Build base URL
                    base = url_base.rstrip('/')
                    path = url_path.lstrip('/')
                    full_url = f"{base}/{path}"
                    
                    # Add query parameters if any
                    if params_dict:
                        query_string = urllib.parse.urlencode(params_dict)
                        full_url += f"?{query_string}"
                    
                    info = f"Built URL with {len(params_dict)} parameters"
                    return (full_url, info, True)
                except Exception as e:
                    return (f"Build error: {str(e)}", "URL building failed", False)
            
            elif operation == "extract_domain":
                try:
                    parsed = urllib.parse.urlparse(input_data)
                    domain = parsed.netloc or parsed.path.split('/')[0]
                    # Remove port if present
                    domain = domain.split(':')[0]
                    info = f"Extracted domain from URL"
                    return (domain, info, True)
                except Exception as e:
                    return (f"Extract error: {str(e)}", "Domain extraction failed", False)
            
            elif operation == "validate_email":
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
                is_valid = bool(re.match(email_pattern, input_data))
                info = f"Email validation: {'valid' if is_valid else 'invalid'}"
                return (str(is_valid).lower(), info, is_valid)
            
            elif operation == "generate_bearer_token":
                # Simple bearer token generation (in practice, use proper JWT or OAuth)
                token_data = f"{input_data}:{int(time.time())}"
                token = base64.b64encode(token_data.encode()).decode()
                bearer_token = f"Bearer {token}"
                info = f"Generated bearer token"
                return (bearer_token, info, True)
            
            elif operation == "create_basic_auth":
                # Create basic auth header from username:password
                if ':' not in input_data:
                    return ("Error: Input should be 'username:password'", "Invalid format", False)
                
                encoded = base64.b64encode(input_data.encode()).decode()
                basic_auth = f"Basic {encoded}"
                info = f"Created basic auth header"
                return (basic_auth, info, True)
            
            else:
                return (f"Unknown operation: {operation}", "Invalid operation", False)
        
        except Exception as e:
            error_msg = f"Utility operation failed: {str(e)}"
            return (error_msg, error_msg, False)