import random
import string
from shortzy import Shortzy
from config import API, URL
import json
import random
import string
from config import LANGUAGE_DIR

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


def load_language(lang_code):
    try:
        with open(f"{LANGUAGE_DIR}/{lang_code}.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return load_language("en")  # Fallback to English


