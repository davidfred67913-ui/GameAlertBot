import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
import threading

# ===== CONFIGURATION - CHANGE THIS =====
BOT_TOKEN = "8518702178:AAG1P6k9bfwmV-wL3HG2rEulx9FfA0x6QzA"  # <--- CHANGE THIS!
# =======================================

CHANNEL = "@online_cazino_big"
WEBSITE = "https://cazino-big.com?agent_id=33"
SUPPORT = "https://www.cazino-big.com/article/privacy-policy"

# Setup
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
fail_count = {}

@app.route('/')
def home():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in fail_count:
        del fail_count[user_id]
    
    keyboard = [
        [InlineKeyboardButton("✅ Join Channel", url="https://t.me/online_cazino_big")],
        [InlineKeyboardButton("🔓 I Joined (Unlock)", callback_data="unlock")]
    ]
    await update.message.reply_text(
        "👋 Welcome!\nStep 1/2: Join our channel to unlock.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "unlock":
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
            is_member = member.status in ["member", "administrator", "creator"]
        except:
            is_member = False
        
        if is_member:
            keyboard = [
                [InlineKeyboardButton("🎰 Play Now", url=WEBSITE)],
                [InlineKeyboardButton("🎁 Today's Offer", callback_data="offer")],
                [InlineKeyboardButton("💬 Support", url=SUPPORT)]
            ]
            await query.edit_message_text(
                "🎉 Unlocked! Step 2/2: Continue to site.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            fail_count[user_id] = fail_count.get(user_id, 0) + 1
            keyboard = [
                [InlineKeyboardButton("✅ Join Channel", url="https://t.me/online_cazino_big")],
                [InlineKeyboardButton("🔄 Try Again", callback_data="unlock")]
            ]
            if fail_count[user_id] >= 2:
                keyboard.append([InlineKeyboardButton("❓ Help", url=SUPPORT)])
            
            await query.edit_message_text(
                "❌ Not joined yet! Join channel first:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    elif query.data == "offer":
        keyboard = [
            [InlineKeyboardButton("🎰 Claim Offer", url=WEBSITE)],
            [InlineKeyboardButton("🔙 Back", callback_data="unlock")]
        ]
        await query.edit_message_text(
            "🎁 Welcome Bonus: 100% up to €500 + 50 free spins!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def run_bot():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    app_bot.run_polling()

if __name__ == "__main__":
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
