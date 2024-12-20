import random
import string
from shortzy import Shortzy
from config import API, URL

def generate_session_name():
    """Generate a random session name."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def generate_token():
    """Generate a random unique token."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=15))

async def get_shortlink(link):
    """Generate a shortlink using Shortzy."""
    shortzy = Shortzy(api_key=API, base_site=URL)
    return await shortzy.convert(link)
