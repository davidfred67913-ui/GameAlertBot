import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
import threading
import time

# ===== CONFIGURATION - CHANGE THIS =====
BOT_TOKEN = "8518702178:AAG1P6k9bfwmV-wL3HG2rEulx9FfA0x6QzA"  # <--- PASTE YOUR BOT TOKEN!
# =======================================

CHANNEL = "@online_cazino_big"
WEBSITE = "https://cazino-big.com?agent_id=33"
SUPPORT = "https://www.cazino-big.com/article/privacy-policy"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for Render
app = Flask(__name__)
fail_count = {}

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    
    # Reset fail count for new user
    if user_id in fail_count:
        del fail_count[user_id]
    
    # Welcome message
    welcome_text = (
        "👋 Welcome to Game Alerts Hub!\n\n"
        "Get access to exclusive drops + winner alerts.\n"
        "Step 1/2: Join our channel to unlock."
    )
    
    # Buttons
    keyboard = [
        [InlineKeyboardButton("✅ Join Channel", url="https://t.me/online_cazino_big")],
        [InlineKeyboardButton("🔓 I Joined (Unlock)", callback_data="unlock")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "unlock":
        # Check if user joined channel
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
            is_member = member.status in ["member", "administrator", "creator"]
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            is_member = False
        
        if is_member:
            # User joined - show unlocked screen
            keyboard = [
                [InlineKeyboardButton("🎰 Play Now", url=WEBSITE)],
                [InlineKeyboardButton("🎁 Today's Offer", callback_data="offer")],
                [InlineKeyboardButton("💬 Support", url=SUPPORT)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🎉 Access Unlocked! Step 2/2: Continue to the site.",
                reply_markup=reply_markup
            )
            
            # Reset fail count
            if user_id in fail_count:
                del fail_count[user_id]
                
        else:
            # User not joined - show fail message
            fail_count[user_id] = fail_count.get(user_id, 0) + 1
            
            benefits = (
                "✨ Why join?\n"
                "• Exclusive daily drops\n"
                "• Instant winner alerts\n"
                "• Member-only bonuses"
            )
            
            keyboard = [
                [InlineKeyboardButton("✅ Join Channel", url="https://t.me/online_cazino_big")],
                [InlineKeyboardButton("🔄 Try Unlock Again", callback_data="unlock")]
            ]
            
            # Add help button after 2 failures
            if fail_count[user_id] >= 2:
                keyboard.append([InlineKeyboardButton("❓ Need Help?", url=SUPPORT)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"❌ Not subscribed yet!\n\n{benefits}\n\nJoin our channel first:",
                reply_markup=reply_markup
            )
    
    elif query.data == "offer":
        # Show today's offer
        offer_text = (
            "🎁 Today's Special Offer 🎁\n\n"
            "✨ Welcome Bonus Package ✨\n"
            "• 100% match bonus up to €500\n"
            "• 50 free spins\n"
            "• Exclusive cashback\n\n"
            "⏰ Limited time!"
        )
        
        keyboard = [
            [InlineKeyboardButton("🎰 Claim Offer", url=WEBSITE)],
            [InlineKeyboardButton("🔙 Back", callback_data="unlock")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(offer_text, reply_markup=reply_markup)

def run_bot():
    """Run the Telegram bot"""
    try:
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create application
        app_bot = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CallbackQueryHandler(button_handler))
        
        # Start bot
        logger.info("Bot started successfully!")
        app_bot.run_polling()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        time.sleep(5)  # Wait before restarting

if __name__ == "__main__":
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask app
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
