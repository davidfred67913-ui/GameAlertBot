import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
# This pulls the token from Render's "Environment Variables" section
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_FALLBACK_TOKEN_HERE")

# Client's Specific Links
CHANNEL_ID = "@online_cazino_big" 
WEBSITE_URL = "https://cazino-big.com?agent_id=33"
SUPPORT_URL = "https://www.cazino-big.com/article/privacy-policy"

# --- FLASK SERVER (For Render Health Checks) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Service Online", 200

def run_flask():
    # Render automatically assigns a PORT; this line captures it correctly
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT LOGIC ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initial screen with the Channel Gate"""
    keyboard = [
        [InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
        [InlineKeyboardButton("🔓 I Joined (Unlock)", callback_data="check_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome 👋 Get access to exclusive drops + winner alerts.\n\n"
        "Step 1/2: Join our channel to unlock.",
        reply_markup=reply_markup
    )

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks if user is actually in the channel before unlocking"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        
        # Valid statuses that mean the user is 'In' the channel
        if member.status in ['member', 'administrator', 'creator']:
            keyboard = [
                [InlineKeyboardButton("🎰 Play Now", url=WEBSITE_URL)],
                [InlineKeyboardButton("🎁 Today’s Offer", callback_data="show_offer")],
                [InlineKeyboardButton("💬 Support", url=SUPPORT_URL)]
            ]
            await query.edit_message_text(
                "Unlocked 🎉\n\nStep 2/2: Continue to the site.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Re-show the join requirement if they haven't joined yet
            keyboard = [
                [InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
                [InlineKeyboardButton("🔓 Try Unlock Again", callback_data="check_membership")]
            ]
            await query.edit_message_text(
                "Not subscribed yet—join to unlock access.\n\n"
                "• Get instant drop alerts\n"
                "• Access member-only links",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception:
        # Fallback if bot isn't admin or channel is private/wrong ID
        await query.edit_message_text(
            "⚠️ Error: Please ensure you have joined the channel first.\n"
            "If you have joined and still see this, contact support.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")]])
        )

async def show_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """The optional secondary offer card"""
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🎰 Play Now", url=WEBSITE_URL)]]
    await query.message.reply_text(
        "🔥 Exclusive Today: 100% Match Bonus.\nClick below to claim before it expires!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    """Main entry point to run Flask and the Bot together"""
    # 1. Start Flask in a background thread so it doesn't block the bot
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. Build and start the Telegram Bot
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))
    application.add_handler(CallbackQueryHandler(show_offer, pattern="show_offer"))
    
    # Run bot polling
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
