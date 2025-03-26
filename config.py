from fake_useragent import UserAgent
import random

# User Agent Rotation
ua = UserAgent()

# Proxy Configuration (replace with your proxies)
PROXIES = [
    "http://user:pass@proxy1:port",
    "http://user:pass@proxy2:port",
    "http://user:pass@proxy3:port"
]

# Request Configuration
HEADERS = {
    "Accept-Language": "en-CA,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1"
}

DELAY = random.uniform(3, 7)  # Increased delay range
RETRIES = 1
TIMEOUT = 20

def get_random_user_agent():
    return ua.chrome

def get_random_proxy():
    return random.choice(PROXIES) if PROXIES else None