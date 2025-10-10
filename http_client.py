"""
HTTP Client base class for ComfyUI HTTP nodes
Provides core HTTP functionality with session management and authentication
"""

import requests
import json
import time
from typing import Dict, Any, Optional, Union, Tuple
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class HTTPClient:
    """Base HTTP client with session management and authentication support"""
    
    def __init__(self):
        self.session = requests.Session()
        self.timeout = 30
        self.verify_ssl = True
        self.allow_redirects = True
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Set default headers that work well with most servers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def set_headers(self, headers: Dict[str, str]):
        """Set custom headers for requests"""
        if headers:
            self.session.headers.update(headers)
    
    def set_auth(self, auth_type: str, username: str = "", password: str = "", 
                 token: str = "", api_key: str = "", api_key_header: str = "X-API-Key"):
        """Set authentication for requests"""
        if auth_type == "basic" and username and password:
            self.session.auth = (username, password)
        elif auth_type == "bearer" and token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        elif auth_type == "api_key" and api_key:
            self.session.headers.update({api_key_header: api_key})
        elif auth_type == "token" and token:
            self.session.headers.update({"Authorization": f"Token {token}"})
    
    def set_cookies(self, cookies: Dict[str, str]):
        """Set cookies for requests"""
        if cookies:
            self.session.cookies.update(cookies)
    
    def set_timeout(self, timeout: int):
        """Set request timeout"""
        self.timeout = max(1, timeout)
    
    def set_ssl_verify(self, verify: bool):
        """Set SSL verification"""
        self.verify_ssl = verify
    
    def set_proxy(self, proxy_url: str):
        """Set proxy for requests"""
        if proxy_url:
            self.session.proxies.update({
                "http": proxy_url,
                "https": proxy_url
            })
    
    def make_request(self, method: str, url: str, **kwargs) -> Tuple[int, Dict[str, Any], str]:
        """
        Make HTTP request with retry logic
        Returns: (status_code, headers, content)
        """
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('verify', self.verify_ssl)
        kwargs.setdefault('allow_redirects', self.allow_redirects)
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(method.upper(), url, **kwargs)
                
                # Convert response headers to dict
                response_headers = dict(response.headers)
                
                # Get content as text or bytes based on content type
                try:
                    content_type = response_headers.get('content-type', '').lower()
                    if 'image/' in content_type or 'application/octet-stream' in content_type:
                        # Return binary content for images and binary data
                        content = response.content
                    else:
                        # Return text content for other types
                        content = response.text
                except Exception:
                    content = response.content
                
                return response.status_code, response_headers, content
                
            except Exception as e:
                last_exception = e
                logger.warning(f"HTTP request attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                
        # If all retries failed, raise the last exception
        raise last_exception or Exception("HTTP request failed after all retries")
    
    def get_binary(self, url: str, params: Optional[Dict] = None, **kwargs) -> Tuple[int, Dict[str, Any], bytes]:
        """Make GET request and return binary content"""
        if params:
            kwargs['params'] = params
        
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('verify', self.verify_ssl)
        kwargs.setdefault('allow_redirects', self.allow_redirects)
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request('GET', url, **kwargs)
                
                # Convert response headers to dict
                response_headers = dict(response.headers)
                
                # Return binary content
                return response.status_code, response_headers, response.content
                
            except Exception as e:
                last_exception = e
                logger.warning(f"HTTP binary request attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                
        # If all retries failed, raise the last exception
        raise last_exception or Exception("HTTP binary request failed after all retries")
    
    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> Tuple[int, Dict[str, Any], str]:
        """Make GET request"""
        if params:
            kwargs['params'] = params
        return self.make_request('GET', url, **kwargs)
    
    def post(self, url: str, data: Optional[Union[str, Dict]] = None, 
             json_data: Optional[Dict] = None, files: Optional[Dict] = None, **kwargs) -> Tuple[int, Dict[str, Any], str]:
        """Make POST request"""
        if json_data is not None:
            kwargs['json'] = json_data
        elif data is not None:
            kwargs['data'] = data
        if files:
            kwargs['files'] = files
        return self.make_request('POST', url, **kwargs)
    
    def put(self, url: str, data: Optional[Union[str, Dict]] = None, 
            json_data: Optional[Dict] = None, **kwargs) -> Tuple[int, Dict[str, Any], str]:
        """Make PUT request"""
        if json_data is not None:
            kwargs['json'] = json_data
        elif data is not None:
            kwargs['data'] = data
        return self.make_request('PUT', url, **kwargs)
    
    def patch(self, url: str, data: Optional[Union[str, Dict]] = None, 
              json_data: Optional[Dict] = None, **kwargs) -> Tuple[int, Dict[str, Any], str]:
        """Make PATCH request"""
        if json_data is not None:
            kwargs['json'] = json_data
        elif data is not None:
            kwargs['data'] = data
        return self.make_request('PATCH', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Tuple[int, Dict[str, Any], str]:
        """Make DELETE request"""
        return self.make_request('DELETE', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> Tuple[int, Dict[str, Any], str]:
        """Make HEAD request"""
        return self.make_request('HEAD', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> Tuple[int, Dict[str, Any], str]:
        """Make OPTIONS request"""
        return self.make_request('OPTIONS', url, **kwargs)
    
    def close(self):
        """Close the session"""
        self.session.close()