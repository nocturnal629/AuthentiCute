from fastapi import Request
from typing import Optional

def get_client_ip(request: Request) -> str:
    """Get the client IP address from the request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    client_host = request.client.host if request.client else "unknown"
    return client_host

def get_rate_limit_identifier(request: Request, user_email: Optional[str] = None) -> str:
    """Get a unique identifier for rate limiting"""
    client_ip = get_client_ip(request)
    
    if user_email:
        return f"{user_email}:{client_ip}"
    
    return client_ip 