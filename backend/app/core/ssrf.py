import socket
import ipaddress
import urllib.parse
from typing import Tuple

BLOCKED_HOSTNAMES = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "metadata.google.internal",
    "169.254.169.254", # AWS / GCP / Azure metadata
    "instance-data",
}

ALLOWED_SCHEMES = {"http", "https"}

def is_private_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        )
    except ValueError:
        return False

def validate_url_for_ssrf(url_str: str) -> Tuple[bool, str]:
    """
    Validates a URL against SSRF vulnerabilities.
    Returns (is_safe, reason_or_clean_url)
    """
    if not url_str or not isinstance(url_str, str):
        return False, "Empty or invalid URL"
    
    url_str = url_str.strip()
    
    try:
        parsed = urllib.parse.urlparse(url_str)
    except Exception as e:
        return False, f"Failed to parse URL: {str(e)}"
        
    # Check scheme
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False, f"Unsupported scheme '{parsed.scheme}'. Only http and https are permitted."
        
    # Check credentials in URL (e.g. http://user:pass@host)
    if parsed.username or parsed.password:
        return False, "Credentials inside URLs are prohibited."
        
    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in URL."
        
    hostname = hostname.lower().strip()
    
    # Check blocked hostnames
    if hostname in BLOCKED_HOSTNAMES or hostname.endswith(".local") or hostname.endswith(".internal"):
        return False, f"Access to hostname '{hostname}' is blocked."
        
    # Resolve DNS to check if it points to internal/private IPs
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for entry in addr_info:
            ip = entry[4][0]
            if is_private_ip(ip):
                return False, f"Hostname resolves to private/internal IP address '{ip}'."
    except socket.gaierror:
        # If DNS cannot be resolved, allow crawler to attempt or handle standard DNS error gracefully
        pass
    except Exception:
        pass
        
    return True, url_str

def is_safe_url(url_str: str) -> bool:
    is_safe, _ = validate_url_for_ssrf(url_str)
    return is_safe
