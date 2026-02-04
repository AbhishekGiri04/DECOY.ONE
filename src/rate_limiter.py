"""
Rate Limiter for API Protection
Prevents abuse and DDoS attacks
"""

import time
from collections import defaultdict
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        current_time = time.time()
        
        # Check if blocked
        if identifier in self.blocked_ips:
            if current_time < self.blocked_ips[identifier]:
                return False
            else:
                del self.blocked_ips[identifier]
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            # Block for 5 minutes
            self.blocked_ips[identifier] = current_time + 300
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add request
        self.requests[identifier].append(current_time)
        return True
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests"""
        current_time = time.time()
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < 60
        ]
        return max(0, self.requests_per_minute - len(self.requests[identifier]))

# Global rate limiter
rate_limiter = RateLimiter(requests_per_minute=100)
