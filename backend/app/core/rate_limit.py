from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Initialize Limiter with global default
# Key func: get_remote_address (IP based)
limiter = Limiter(key_func=get_remote_address, default_limits=["100/15minutes"])
