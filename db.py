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
