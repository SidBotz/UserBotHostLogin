import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from db import *
from utils import *
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, CHANNELS, XD, XDAYS
from db import Database
from utils import load_language, generate_token

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = Database()

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    command_args = message.text.split()

    # Register user if not already registered
    if user_id not in db.users:
        db.add_user(user_id)

    user_lang = db.get_language(user_id)
    if not user_lang:
        # Default to English if language not set
        user_lang = "eng"
        db.set_language(user_id, user_lang)
    
    lang = load_language(user_lang)

    if len(command_args) > 1:
        token = command_args[1]

        # Handle referrals or ad tokens
        if token.isdigit():
            referrer_id = int(token)
            if referrer_id != user_id:
                db.add_referral(referrer_id, user_id)
                if db.get_referrals(referrer_id) >= XD:
                    db.add_premium(referrer_id, XDAYS)
                    await client.send_message(
                        referrer_id,
                        lang["referral_success"].format(days=XDAYS, count=XD)
                    )
                await message.reply_text(lang["referral_joined"])
            return

    # Create keyboard based on whether the user has already set their language
    keyboard_buttons = []
    if not db.is_language_set(user_id):
        keyboard_buttons.append([InlineKeyboardButton("Set Language", callback_data="set_language")])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    text = f"{lang['start_message']}\n\n" + "\n".join([f"- {channel}" for channel in CHANNELS])
    await message.reply_text(text, reply_markup=keyboard)

@bot.on_callback_query(filters.regex("set_language"))
async def set_language_button_handler(client, callback_query):
    """Handles the 'Set Language' button click and shows language options."""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("English", callback_data="set_lang_eng"),
            InlineKeyboardButton("Hindi", callback_data="set_lang_hi")
        ],
        [
            InlineKeyboardButton("Tamil", callback_data="set_lang_tam"),
            InlineKeyboardButton("French", callback_data="set_lang_fre")
        ],
        [
            InlineKeyboardButton("Persian", callback_data="set_lang_per"),
            InlineKeyboardButton("Indonesian", callback_data="set_lang_id")
        ]
    ])
    await callback_query.message.edit_text(
        "Please select your language:",
        reply_markup=keyboard
    )


@bot.on_message(filters.command("language") & filters.private)
async def set_language_command(client, message):
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("English", callback_data="set_lang_eng"),
            InlineKeyboardButton("Hindi", callback_data="set_lang_hi")
        ],
        [
            InlineKeyboardButton("Tamil", callback_data="set_lang_tam"),
            InlineKeyboardButton("French", callback_data="set_lang_fre")
        ],
        [
            InlineKeyboardButton("Persian", callback_data="set_lang_per"),
            InlineKeyboardButton("Indonesian", callback_data="set_lang_id")
        ]
    ])
    await message.reply_text("Please select your language:", reply_markup=keyboard)


@bot.on_callback_query(filters.regex(r"set_lang_(\w+)"))
async def set_language_callback(client, callback_query):
    user_id = callback_query.from_user.id
    language_code = callback_query.data.split("_")[-1]

    db.set_language(user_id, language_code)  # Save the selected language to the database
    lang = load_language(language_code)

    await callback_query.answer("Language updated successfully!")
    await callback_query.message.reply_text(lang["start_message"])







@bot.on_message(filters.command("clone") & filters.private)
async def clone_handler(client, message):
    user_id = message.from_user.id
    user_lang = db.get_language(user_id)
    lang = load_language(user_lang)

    if db.is_premium(user_id):
        keyboard = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(lang["phone_option"], callback_data="phone_number"),
                InlineKeyboardButton(lang["session_option"], callback_data="string_session")
            ], [
                InlineKeyboardButton(lang["token_option"], callback_data="bot_token")
            ]]
        )
        await message.reply_text(lang["choose_option"], reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(lang["free_premium"], callback_data="free_premium"),
                InlineKeyboardButton(lang["buy_premium"], callback_data="buy_premium")
            ]]
        )
        await message.reply_text(lang["premium_required"], reply_markup=keyboard)


@bot.on_callback_query(filters.regex("free_premium"))
async def free_premium_handler(client, callback_query):
    user_id = callback_query.from_user.id
    user_lang = db.get_language(user_id)
    lang = load_language(user_lang)

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(lang["referral_option"], callback_data="referral"),
            InlineKeyboardButton(lang["view_ads_option"], callback_data="view_ads")
        ]]
    )
    await callback_query.message.reply_text(lang["free_premium_info"], reply_markup=keyboard)


@bot.on_callback_query(filters.regex("referral"))
async def referral_handler(client, callback_query):
    user_id = callback_query.from_user.id
    user_lang = db.get_language(user_id)
    lang = load_language(user_lang)

    referral_link = f"https://t.me/{bot.username}?start={user_id}"
    await callback_query.message.edit(
        lang["referral_instructions"].format(link=referral_link),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(lang["share_referral"], url=referral_link)]])
    )

@bot.on_callback_query(filters.regex("view_ads"))
async def view_ads_handler(client, callback_query):
    user_id = callback_query.from_user.id
    user_lang = db.get_language(user_id)
    lang = load_language(user_lang)

    token = generate_token()
    AD_TOKENS[token] = user_id
    verification_link = f"https://t.me/{bot.username}?start={token}"
    short_link = await get_shortlink(verification_link)

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(lang["VerifyButton"], url=short_link)],
         [InlineKeyboardButton(lang["HowToVerify?"], url="https://example.com/tutorial")]]  # Replace with actual tutorial URL
    )
    await callback_query.message.edit(
        text=lang["VerifyText"],
        reply_markup=keyboard
    )



if __name__ == "__main__":
    bot.run()

