"""
HTTP Display Result node for ComfyUI
Displays HTTP response data in a readable format
"""

import json
from typing import Any, Dict, Tuple

class HTTPDisplayResult:
    """HTTP Display Result Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "status_code": ("INT", {"default": 200}),
                "headers": ("STRING", {"default": "{}"}),
                "content": ("STRING", {"default": ""}),
            },
            "optional": {
                "display_mode": (["formatted", "raw", "summary"], {"default": "formatted"}),
                "max_content_length": ("INT", {"default": 1000, "min": 100, "max": 10000}),
                "show_headers": ("BOOLEAN", {"default": True}),
                "show_cookies": ("BOOLEAN", {"default": True}),
                "json_indent": ("INT", {"default": 2, "min": 0, "max": 8}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("display_text", "summary", "status_text", "success")
    FUNCTION = "display_result"
    CATEGORY = "HTTP/Display"
    
    def display_result(self, status_code: int, headers: str, content: str,
                      display_mode: str = "formatted", max_content_length: int = 1000,
                      show_headers: bool = True, show_cookies: bool = True,
                      json_indent: int = 2) -> Tuple[str, str, str, bool]:
        """Display HTTP response in formatted way"""
        
        try:
            # Determine if request was successful
            success = 200 <= status_code < 300
            
            # Create status text
            status_text = f"HTTP {status_code}"
            status_messages = {
                200: "OK",
                201: "Created", 
                202: "Accepted",
                204: "No Content",
                400: "Bad Request",
                401: "Unauthorized",
                403: "Forbidden",
                404: "Not Found",
                405: "Method Not Allowed",
                409: "Conflict",
                422: "Unprocessable Entity",
                429: "Too Many Requests",
                500: "Internal Server Error",
                502: "Bad Gateway",
                503: "Service Unavailable",
                504: "Gateway Timeout"
            }
            
            if status_code in status_messages:
                status_text += f" {status_messages[status_code]}"
            
            # Parse headers
            headers_dict = {}
            try:
                if headers and headers != "{}":
                    headers_dict = json.loads(headers)
            except:
                pass
            
            # Create summary
            content_length = len(content)
            content_type = headers_dict.get("content-type", headers_dict.get("Content-Type", "unknown"))
            
            summary_parts = [
                f"Status: {status_text}",
                f"Content-Type: {content_type}",
                f"Content-Length: {content_length} bytes"
            ]
            
            if headers_dict:
                summary_parts.append(f"Headers: {len(headers_dict)} items")
            
            summary = "\\n".join(summary_parts)
            
            # Create display text based on mode
            if display_mode == "summary":
                display_text = summary
                
            elif display_mode == "raw":
                display_parts = [
                    f"=== HTTP Response ===",
                    f"Status: {status_text}",
                    ""
                ]
                
                if show_headers and headers_dict:
                    display_parts.append("=== Headers ===")
                    for key, value in headers_dict.items():
                        display_parts.append(f"{key}: {value}")
                    display_parts.append("")
                
                display_parts.append("=== Content ===")
                if content_length > max_content_length:
                    display_parts.append(f"{content[:max_content_length]}...")
                    display_parts.append(f"\\n[Content truncated - showing first {max_content_length} of {content_length} characters]")
                else:
                    display_parts.append(content)
                
                display_text = "\\n".join(display_parts)
                
            else:  # formatted
                display_parts = [
                    f"=== HTTP Response ===",
                    f"Status: {status_text}",
                    f"Success: {'✓' if success else '✗'}",
                    ""
                ]
                
                if show_headers and headers_dict:
                    display_parts.append("=== Headers ===")
                    # Format headers nicely
                    for key, value in sorted(headers_dict.items()):
                        if show_cookies or key.lower() not in ['set-cookie', 'cookie']:
                            display_parts.append(f"  {key}: {value}")
                    display_parts.append("")
                
                # Show cookies separately if requested
                if show_cookies:
                    cookie_headers = {k: v for k, v in headers_dict.items() 
                                    if k.lower() in ['set-cookie', 'cookie']}
                    if cookie_headers:
                        display_parts.append("=== Cookies ===")
                        for key, value in cookie_headers.items():
                            display_parts.append(f"  {key}: {value}")
                        display_parts.append("")
                
                display_parts.append("=== Content ===")
                
                # Try to format content as JSON if possible
                try:
                    if content.strip():
                        parsed_content = json.loads(content)
                        formatted_content = json.dumps(parsed_content, indent=json_indent, ensure_ascii=False)
                        
                        if len(formatted_content) > max_content_length:
                            display_parts.append(f"{formatted_content[:max_content_length]}...")
                            display_parts.append(f"\\n[JSON content truncated - showing first {max_content_length} of {len(formatted_content)} characters]")
                        else:
                            display_parts.append(formatted_content)
                    else:
                        display_parts.append("[Empty content]")
                        
                except json.JSONDecodeError:
                    # Not JSON, display as text
                    if content_length > max_content_length:
                        display_parts.append(f"{content[:max_content_length]}...")
                        display_parts.append(f"\\n[Content truncated - showing first {max_content_length} of {content_length} characters]")
                    else:
                        display_parts.append(content if content else "[Empty content]")
                
                display_text = "\\n".join(display_parts)
            
            return (display_text, summary, status_text, success)
            
        except Exception as e:
            error_msg = f"Error displaying result: {str(e)}"
            return (error_msg, error_msg, f"HTTP {status_code}", False)