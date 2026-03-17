import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
TOKEN = "YOUR_BOT_TOKEN_HERE"
CHANNEL_ID = "@online_cazino_big"  # Ensure bot is admin in this channel
WEBSITE_URL = "https://cazino-big.com?agent_id=33"
SUPPORT_URL = "https://www.cazino-big.com/article/privacy-policy"

# --- FLASK SERVER FOR RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# --- BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            # SUCCESS SCREEN
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
            # FAIL SCREEN
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
    except Exception as e:
        await query.edit_message_text("Error checking membership. Please ensure you have joined the channel.")

async def show_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🎰 Play Now", url=WEBSITE_URL)]]
    await query.message.reply_text(
        "🔥 Exclusive Today: 100% Match Bonus.\nClick below to claim before it expires!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    # Start Flask in a separate thread
    Thread(target=run_flask).start()

    # Start Telegram Bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))
    application.add_handler(CallbackQueryHandler(show_offer, pattern="show_offer"))
    
    application.run_polling()

if __name__ == '__main__':
    main()
