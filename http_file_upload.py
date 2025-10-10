"""
HTTP File Upload node for ComfyUI
Handles file uploads with various formats and options
"""

from typing import Dict, Any, Optional
from .http_client import HTTPClient
from .http_auth import HTTPAuth
from urllib.parse import urljoin
import json
import os

class HTTPFileUpload:
    """HTTP File Upload Node for ComfyUI"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "https://api.example.com/upload"}),
                "file_path": ("STRING", {"default": "/path/to/file.txt"}),
                "field_name": ("STRING", {"default": "file"}),
            },
            "optional": {
                "session": ("HTTP_SESSION",),
                "auth": ("HTTP_AUTH",),
                "headers": ("STRING", {"default": "{}"}),
                "additional_data": ("STRING", {"default": "{}"}),
                "filename": ("STRING", {"default": ""}),
                "content_type": ("STRING", {"default": ""}),
                "timeout": ("INT", {"default": 60, "min": 1, "max": 300}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
                "allow_redirects": ("BOOLEAN", {"default": True}),
                "cookies": ("STRING", {"default": "{}"}),
                "proxy_url": ("STRING", {"default": ""}),
                "chunk_size": ("INT", {"default": 8192, "min": 1024, "max": 1048576}),
            }
        }
    
    RETURN_TYPES = ("INT", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("status_code", "headers", "content", "json")
    FUNCTION = "upload_file"
    CATEGORY = "HTTP/File Operations"
    
    def upload_file(self, url: str, file_path: str, field_name: str,
                   session: Optional[Dict] = None, auth: Optional[Dict] = None,
                   headers: str = "{}", additional_data: str = "{}", filename: str = "",
                   content_type: str = "", timeout: int = 60, verify_ssl: bool = True,
                   allow_redirects: bool = True, cookies: str = "{}", proxy_url: str = "",
                   chunk_size: int = 8192):
        """Upload file via HTTP POST with multipart form data"""
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                return (0, "{}", error_msg, error_msg)
            
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
            
            # Parse additional form data
            form_data = {}
            if additional_data and additional_data != "{}":
                try:
                    form_data = json.loads(additional_data)
                except Exception as e:
                    print(f"Warning: Failed to parse additional data: {e}")
            
            # Auto-detect filename if not provided
            if not filename:
                filename = os.path.basename(file_path)
            
            # Auto-detect content type if not provided
            if not content_type:
                ext = os.path.splitext(file_path)[1].lower()
                content_type_map = {
                    '.txt': 'text/plain',
                    '.json': 'application/json',
                    '.xml': 'application/xml',
                    '.pdf': 'application/pdf',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp',
                    '.webp': 'image/webp',
                    '.mp4': 'video/mp4',
                    '.avi': 'video/avi',
                    '.mp3': 'audio/mpeg',
                    '.wav': 'audio/wav',
                }
                content_type = content_type_map.get(ext, 'application/octet-stream')
            
            # Read file data
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
            except Exception as e:
                error_msg = f"Error reading file: {str(e)}"
                return (0, "{}", error_msg, error_msg)
            
            # Prepare files for upload
            files = {
                field_name: (filename, file_data, content_type)
            }
            
            # Make the request
            status_code, response_headers, content = client.post(
                url, data=form_data if form_data else None, files=files
            )
            
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
            error_msg = f"File upload failed: {str(e)}"
            print(error_msg)
            return (0, "{}", error_msg, error_msg)