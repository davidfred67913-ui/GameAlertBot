import os
import asyncio
from flask import Flask
from threading import Thread
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_FALLBACK_TOKEN_HERE")
CHANNEL_ID = "@online_cazino_big" 
WEBSITE_URL = "https://cazino-big.com?agent_id=33"
SUPPORT_URL = "https://www.cazino-big.com/article/faq"
USER_DATA_FILE = "users.txt"

# --- USER TRACKING LOGIC ---
def log_user(user_id):
    """Logs the user ID and current month to a file for MAU tracking."""
    current_month = datetime.now().strftime("%Y-%m")
    entry = f"{user_id},{current_month}\n"
    
    existing_entries = []
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            existing_entries = f.readlines()
            
    if entry not in existing_entries:
        with open(USER_DATA_FILE, "a") as f:
            f.write(entry)

def get_monthly_count():
    """Calculates unique users for the current calendar month."""
    if not os.path.exists(USER_DATA_FILE):
        return 0
    
    current_month = datetime.now().strftime("%Y-%m")
    unique_users = set()
    
    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            if "," in line:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    uid, month = parts
                    if month == current_month:
                        unique_users.add(uid)
    
    return len(unique_users)

# --- FLASK SERVER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Status: Active", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- BOT LOGIC ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_user(user_id)
    user_count = get_monthly_count()
    
    keyboard = [
        [InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
        [InlineKeyboardButton("🔓 I Joined (Unlock)", callback_data="check_membership")]
    ]
    
    await update.message.reply_text(
        f"Welcome 👋 Join {user_count}+ active users this month receiving exclusive drops!\n\n"
        "Step 1/2: Join our channel to unlock."
    )
    await update.message.reply_text(
        "Click below to verify membership:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    log_user(user_id)

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
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
        await query.edit_message_text("⚠️ Error: Please ensure you have joined the channel first.")

async def show_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Updated with the €1500 Welcome Bonus text."""
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🎰 Play Now", url=WEBSITE_URL)]]
    await query.message.reply_text(
        "🔥 Exclusive Today: Up to €1500 Welcome Bonus.\n"
        "Click below to claim before it expires!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_membership, pattern="check_membership"))
    application.add_handler(CallbackQueryHandler(show_offer, pattern="show_offer"))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    while True:
        await asyncio.sleep(3600)

def main():
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Bot is starting...")
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    main()
