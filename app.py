import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8782617212:AAGEy5Zqez5rz60HzzjNR4DtkEKCd5aAL8I"

logging.basicConfig(level=logging.INFO)

bot_status = {"running": False, "trades": 0, "profit": 0.0}

def main_keyboard():
    toggle_text = "⛔ TSAIDA BOT" if bot_status["running"] else "▶️ KUNNA BOT"
    keyboard = [
        [InlineKeyboardButton(toggle_text, callback_data="toggle")],
        [InlineKeyboardButton("📊 STATUS & STATS", callback_data="stats")],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🤖 *Barka da zuwa Sidra DEX Arbitrage Bot!*\n\n"
        f"Matsayin Bot: *{'🟢 Yana Aiki (RUNNING)' if bot_status['running'] else '🔴 Ya Tsaya (STOPPED)'}*\n"
        "Zaɓi abin da kake so ka yi a ƙasa:"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "toggle":
        bot_status["running"] = not bot_status["running"]
        status_str = "🟢 Bot din ka ya FARA aiki 24/7!" if bot_status["running"] else "🔴 Bot din ka ya TSAYA!"
        await query.edit_message_text(text=f"{status_str}\n\nZaɓi na gaba:", reply_markup=main_keyboard())

    elif query.data == "stats":
        stats_msg = (
            "📊 *SIDRA BOT DASHBOARD STATS*\n\n"
            f"• Status: *{'🟢 ACTIVE' if bot_status['running'] else '🔴 INACTIVE'}*\n"
            f"• Total Trades: *{bot_status['trades']}*\n"
            f"• Total Profit: *{bot_status['profit']} SDA*\n"
            "• Active Pairs: *TRL/SDA, REGS/SDA, All Sidra DEX Pairs*"
        )
        await query.edit_message_text(text=stats_msg, parse_mode="Markdown", reply_markup=main_keyboard())

    elif query.data == "refresh":
        await query.edit_message_text(text="🔄 An sabunta shafin!", reply_markup=main_keyboard())

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is starting...")
    app.run_polling()
  
