PREMIUM_USERS = {}
REFERRALS = {}
AD_TOKENS = {}

def add_premium_user(user_id, days=1):
    """Add a user to the premium list with expiration."""
    PREMIUM_USERS[user_id] = {"days": days, "expires": asyncio.get_event_loop().time() + (days * 86400)}

def is_premium_user(user_id):
    """Check if a user is premium and their status is still valid."""
    if user_id in PREMIUM_USERS:
        user_data = PREMIUM_USERS[user_id]
        if asyncio.get_event_loop().time() < user_data["expires"]:
            return True
        else:
            del PREMIUM_USERS[user_id]  # Remove expired user
    return False

def get_referral_count(user_id):
    """Get the number of referrals for a user."""
    return REFERRALS.get(user_id, {}).get("count", 0)

def increment_referral_count(user_id):
    """Increment the referral count for a user."""
    if user_id not in REFERRALS:
        REFERRALS[user_id] = {"count": 0}
    REFERRALS[user_id]["count"] += 1

def is_valid_ad_token(token):
    """Check if the ad token is valid."""
    return token in AD_TOKENS

def consume_ad_token(token):
    """Consume and remove an ad token from the database."""
    return AD_TOKENS.pop(token, None)
    
import time



import time

class Database:
    def __init__(self):
        # Initialize in-memory storage for users, referrals, and ad tokens
        self.users = {}  # {user_id: {"language": "en", "premium_expires": 0, "referrals": 0}}
        self.referrals = {}  # {referrer_id: [list_of_referred_users]}
        self.ad_tokens = {}  # For ad verification

    def add_user(self, user_id, language="en"):
        """Add a new user to the database with a default language (English)."""
        if user_id not in self.users:
            self.users[user_id] = {"language": language, "premium_expires": 0, "referrals": 0}

    def set_language(self, user_id, language_code):
        """Save the user's language preference."""
        if user_id in self.users:
            self.users[user_id]["language"] = language_code

    def get_language(self, user_id):
        """Retrieve the user's current language preference."""
        return self.users[user_id].get("language", "en")  # Default to "en" if no language is set

    def is_language_set(self, user_id):
        """Check if the user has set a language."""
        return user_id in self.users and "language" in self.users[user_id] and self.users[user_id]["language"] != "en"

    def add_premium(self, user_id, days):
        """Add premium status to the user for a certain number of days."""
        if user_id not in self.users:
            return  # User not found, don't process

        expires = self.users[user_id].get("premium_expires", 0)
        # Set premium expiration to the max of the current time or the existing expiration time, plus the new premium days
        self.users[user_id]["premium_expires"] = max(time.time(), expires) + (days * 86400)

    def is_premium(self, user_id):
        """Check if the user has an active premium status."""
        if user_id not in self.users:
            return False
        return self.users[user_id]["premium_expires"] > time.time()

    def add_referral(self, referrer_id, referred_id):
        """Add a referral from one user to another."""
        if referrer_id not in self.referrals:
            self.referrals[referrer_id] = []

        # Ensure the referred user isn't already referred by the same person
        if referred_id not in self.referrals[referrer_id]:
            self.referrals[referrer_id].append(referred_id)
            self.users[referrer_id]["referrals"] += 1

    def get_referrals(self, referrer_id):
        """Get the total number of referrals made by the user."""
        return self.users[referrer_id].get("referrals", 0)

    def add_ad_token(self, token, user_id):
        """Store an ad token for ad verification purposes."""
        self.ad_tokens[token] = user_id

    def get_ad_token_user(self, token):
        """Get the user associated with an ad token."""
        return self.ad_tokens.get(token)
