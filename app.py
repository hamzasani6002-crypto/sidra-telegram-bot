import os
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = "8782617212:AAGEy5Zqez5rz60HzzjNR4DtkEKCd5aAL8I"
URL = f"https://api.telegram.org/bot{TOKEN}/"

bot_status = {"running": False, "trades": 0, "profit": 0.0}

# Web Server mai sauƙi don gamsar da Render port check
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

def get_updates(offset=None):
    try:
        url = URL + "getUpdates?timeout=30"
        if offset:
            url += f"&offset={offset}"
        response = requests.get(url, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(URL + "sendMessage", json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

def main_keyboard():
    toggle_text = "STOP BOT" if bot_status["running"] else "START BOT"
    return {
        "inline_keyboard": [
            [{"text": toggle_text, "callback_data": "toggle"}],
            [{"text": "DASHBOARD STATS", "callback_data": "stats"}],
            [{"text": "REFRESH", "callback_data": "refresh"}]
        ]
    }

def handle_update(update):
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]
        if text == "/start":
            status_label = "RUNNING" if bot_status['running'] else "STOPPED"
            msg = (
                "Barka da zuwa Sidra DEX Arbitrage Bot!\n\n"
                f"Status: {status_label}\n"
                "Zabi abin da kake so ka yi a kasa:"
            )
            send_message(chat_id, msg, main_keyboard())

    elif "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data = query["data"]

        if data == "toggle":
            bot_status["running"] = not bot_status["running"]
            status_str = "Bot dinka ya FARA aiki!" if bot_status["running"] else "Bot dinka ya TSAYA!"
            send_message(chat_id, f"{status_str}\n\nZabi na gaba:", main_keyboard())
        elif data == "stats":
            stats_status = "ACTIVE" if bot_status['running'] else "INACTIVE"
            stats_msg = (
                "SIDRA BOT DASHBOARD STATS\n\n"
                f"Status: {stats_status}\n"
                f"Total Trades: {bot_status['trades']}\n"
                f"Total Profit: {bot_status['profit']} SDA\n"
                "Active Pairs: TRL/SDA, REGS/SDA"
            )
            send_message(chat_id, stats_msg, main_keyboard())
        elif data == "refresh":
            send_message(chat_id, "An sabunta shafin!", main_keyboard())

def main():
    # Tayar da Web Server a background don Render
    threading.Thread(target=run_web_server, daemon=True).start()
    
    print("Bot starting via Pure Telegram API...")
    offset = None
    while True:
        updates = get_updates(offset)
        if updates and updates.get("ok"):
            for result in updates.get("result", []):
                offset = result["update_id"] + 1
                handle_update(result)
        time.sleep(1)

if __name__ == "__main__":
    main()
            
