import time
from typing import Dict, List, Tuple
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.last_cleanup = time.time()
    
    def is_allowed(self, identifier: str) -> Tuple[bool, int]:
        """Check if request is allowed for the given identifier"""
        current_time = time.time()
        
        if current_time - self.last_cleanup > 300:
            self._cleanup_expired(current_time)
            self.last_cleanup = current_time
        
        user_requests = self.requests[identifier]
        
        user_requests = [req_time for req_time in user_requests 
                        if current_time - req_time < self.window_seconds]
        
        self.requests[identifier] = user_requests
        
        if len(user_requests) >= self.max_requests:
            return False, 0
        
        user_requests.append(current_time)
        self.requests[identifier] = user_requests
        
        remaining = self.max_requests - len(user_requests)
        return True, remaining
    
    def _cleanup_expired(self, current_time: float):
        """Remove expired entries to prevent memory leaks"""
        expired_identifiers = []
        
        for identifier, requests in self.requests.items():
            valid_requests = [req_time for req_time in requests 
                            if current_time - req_time < self.window_seconds]
            
            if valid_requests:
                self.requests[identifier] = valid_requests
            else:
                expired_identifiers.append(identifier)
        
        for identifier in expired_identifiers:
            del self.requests[identifier]

auth_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)
signup_rate_limiter = RateLimiter(max_requests=3, window_seconds=300)
password_reset_rate_limiter = RateLimiter(max_requests=3, window_seconds=300)