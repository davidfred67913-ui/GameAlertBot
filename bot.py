import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
# Ensure 'BOT_TOKEN' is set in your Render Environment Variables
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_FALLBACK_TOKEN_HERE")

# Client Specific Links
CHANNEL_ID = "@online_cazino_big" 
WEBSITE_URL = "https://cazino-big.com?agent_id=33"
SUPPORT_URL = "https://www.cazino-big.com/article/faq"

# --- FLASK SERVER (For Render Health Checks) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Status: Active", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- BOT LOGIC ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: User sees the 'Join' gate first."""
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
    """Verifies membership before showing the site link."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        
        if member.status in ['member', 'administrator', 'creator']:
            # Success Screen
            keyboard = [
                [InlineKeyboardButton("🎰 Play Now", url=WEBSITE_URL)],
                [InlineKeyboardButton("🎁 Today’s Offer", callback_data="show_offer")],
                [InlineKeyboardButton("💬 Help & FAQ", url=SUPPORT_URL)]
            ]
            await query.edit_message_text(
                "Unlocked 🎉\n\nStep 2/2: Continue to the site.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Re-join Screen
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
        await query.edit_message_text(
            "⚠️ Connection error. Please ensure the bot is an admin in the channel and try again.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")]])
        )

async def show_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Optional offer message."""
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🎰 Play Now", url=WEBSITE_URL)]]
    await query.message.reply_text(
        "🔥 Exclusive Today: 100% Match Bonus.\nClick below to claim before it expires!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def run_bot():
    """Starts the Telegram application inside the asyncio loop."""
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))
    application.add_handler(CallbackQueryHandler(show_offer, pattern="show_offer"))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep the async loop alive
    while True:
        await asyncio.sleep(3600)

def main():
    # Start Flask in background
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start Bot using the modern asyncio runner
    print("Bot is starting...")
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        print("Bot process stopped.")

if __name__ == '__main__':
    main()
