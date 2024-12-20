import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from db import *
from utils import *

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    command_args = message.text.split()

    if len(command_args) > 1:
        token = command_args[1]

        if is_valid_ad_token(token):
            ad_user_id = consume_ad_token(token)
            add_premium_user(user_id, 1)
            await client.send_message(user_id, "✅ Your Premium has been activated for 24 hours!")
            return

        if token.isdigit():
            referrer_id = int(token)
            if referrer_id != user_id:  # Prevent self-referral
                increment_referral_count(referrer_id)

                if get_referral_count(referrer_id) >= XD:
                    add_premium_user(referrer_id, XDAYS)
                    await client.send_message(
                        referrer_id,
                        f"🎉 You have successfully referred {XD} users and earned Premium for {XDAYS} days!"
                    )

            await message.reply_text("✅ You joined using a referral link. Thank you for supporting your referrer!")
            return

    # Normal start without any token
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Joined", callback_data="check_join")]])
    text = f"{START_MESSAGE}\n\n" + "\n".join([f"- {channel}" for channel in CHANNELS])
    await message.reply_text(text, reply_markup=keyboard)

@bot.on_callback_query(filters.regex("free_premium"))
async def free_premium_handler(client, callback_query):
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Referral", callback_data="referral"),
            InlineKeyboardButton("View Ads", callback_data="view_ads")
        ]]
    )
    await callback_query.message.reply_text(
        "You can get Premium for free using these methods:\n\n"
        "1. **Referral**: Invite others to earn Premium.\n"
        "2. **View Ads**: Watch an ad to get 24-hour Premium.\n\n"
        "Select an option to learn more.",
        reply_markup=keyboard
    )

@bot.on_callback_query(filters.regex("referral"))
async def referral_handler(client, callback_query):
    user_id = callback_query.from_user.id
    referral_link = f"https://t.me/{bot.username}?start={user_id}"

    await callback_query.message.reply_text(
        f"Refer {XD} users to get Premium for {XDAYS} days.\n\n"
        f"Your referral link:\n{referral_link}\n\n"
        "Share your link and ask your friends to start the bot.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Share Referral Link", url=referral_link)]])
    )

@bot.on_callback_query(filters.regex("view_ads"))
async def view_ads_handler(client, callback_query):
    user_id = callback_query.from_user.id
    token = generate_token()
    AD_TOKENS[token] = user_id
    verification_link = f"https://t.me/{bot.username}?start={token}"
    short_link = await get_shortlink(verification_link)

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Verify And Get Premium", url=short_link)],
         [InlineKeyboardButton("How to Verify?", url="https://example.com/tutorial")]]  # Replace with actual tutorial URL
    )
    await callback_query.message.reply_text(
        f"Watch the ad using the button below. Once done, return and start the bot using this link to verify:\n\n"
        f"{short_link}",
        reply_markup=keyboard
    )

if __name__ == "__main__":
    bot.run()
