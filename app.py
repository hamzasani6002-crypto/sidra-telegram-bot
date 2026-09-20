            
# app.py
# Telegram EVM Copy Trading Bot
# SAFE MODE:
# - Detects transactions from a target wallet
# - Identifies likely BUY/SELL swap transactions
# - Sends copy-trade notifications to Telegram
# - Does NOT execute real trades until DEX router/ABI is configured

import os
import asyncio
import logging
from decimal import Decimal
from dotenv import load_dotenv
from web3 import Web3
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
RPC_URL = os.getenv(
    "RPC_URL",
    "https://node.sidrachain.com/"
)

TARGET_WALLET = os.getenv("TARGET_WALLET", "")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "3"))

# False = monitor only
# True  = allow execution after router configuration
LIVE_TRADING = False

# Maximum amount to use for a copy trade
MAX_COPY_AMOUNT = Decimal(
    os.getenv("MAX_COPY_AMOUNT", "0.1")
)

SLIPPAGE = Decimal(
    os.getenv("SLIPPAGE", "1")
)

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ============================================================
# WEB3
# ============================================================

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    logger.warning("RPC connection failed")

# ============================================================
# STATE
# ============================================================

bot_running = False
last_block = None

tracked_wallet = TARGET_WALLET.lower() if TARGET_WALLET else ""

subscribers = set()

# ============================================================
# TELEGRAM COMMANDS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    subscribers.add(user_id)

    message = """
🤖 EVM COPY TRADING BOT

Welcome!

Available commands:

/start
/status
/setwallet <address>
/wallet
/startcopy
/stopcopy
/settings
/help

Current mode:
MONITORING / SAFE MODE

The bot will detect transactions from the
wallet you choose.

Real trading is disabled until the DEX
router and ABI are configured.
"""

    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
📚 COMMANDS

/start
Start the bot.

/status
Show bot status.

/setwallet 0x...
Set the wallet to copy.

/ wallet
Show target wallet.

/startcopy
Start monitoring.

/stopcopy
Stop monitoring.

/settings
Show trading settings.
""".replace("/ wallet", "/wallet")
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    connection = w3.is_connected()

    status_text = "🟢 RUNNING" if bot_running else "🔴 STOPPED"

    await update.message.reply_text(
        f"""
📊 BOT STATUS

Bot: {status_text}

RPC:
{"🟢 Connected" if connection else "🔴 Disconnected"}

Network Chain ID:
{w3.eth.chain_id if connection else "Unknown"}

Target wallet:
{tracked_wallet or "Not configured"}

Live trading:
{"🟢 ENABLED" if LIVE_TRADING else "🔴 DISABLED"}

Slippage:
{SLIPPAGE}%

Max copy amount:
{MAX_COPY_AMOUNT}
"""
    )


async def set_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global tracked_wallet

    if not context.args:

        await update.message.reply_text(
            "Usage:\n/setwallet 0xYourWalletAddress"
        )

        return

    address = context.args[0]

    if not Web3.is_address(address):

        await update.message.reply_text(
            "❌ Invalid EVM wallet address."
        )

        return

    tracked_wallet = Web3.to_checksum_address(address).lower()

    await update.message.reply_text(
        f"""
✅ TARGET WALLET SET

{tracked_wallet}

The bot will now monitor this wallet.
"""
    )


async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not tracked_wallet:

        await update.message.reply_text(
            "❌ No target wallet configured."
        )

        return

    await update.message.reply_text(
        f"👛 Target wallet:\n{tracked_wallet}"
    )


async def start_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global bot_running

    if not tracked_wallet:

        await update.message.reply_text(
            "❌ Set a wallet first:\n/setwallet 0x..."
        )

        return

    bot_running = True

    await update.message.reply_text(
        """
🟢 COPY TRADING MONITOR STARTED

The bot is watching the target wallet.

⚠️ Real trading is currently disabled.
"""
    )


async def stop_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global bot_running

    bot_running = False

    await update.message.reply_text(
        "🔴 COPY TRADING MONITOR STOPPED"
    )


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"""
⚙️ SETTINGS

Slippage: {SLIPPAGE}%

Maximum copy amount:
{MAX_COPY_AMOUNT}

Check interval:
{CHECK_INTERVAL}s

Live trading:
{"ON" if LIVE_TRADING else "OFF"}

RPC:
{RPC_URL}
"""
    )


# ============================================================
# TRANSACTION ANALYSIS
# ============================================================

def get_transaction(tx_hash):

    try:

        return w3.eth.get_transaction(tx_hash)

    except Exception as e:

        logger.error(
            f"Transaction error: {e}"
        )

        return None


def analyze_transaction(tx):

    if not tx:

        return None

    result = {
        "hash": tx["hash"].hex(),
        "from": tx["from"],
        "to": tx["to"],
        "value": Decimal(
            w3.from_wei(tx["value"], "ether")
        ),
        "type": "UNKNOWN"
    }

    # A real DEX parser should decode the router
    # calldata here using the actual Sidra DEX ABI.

    if tx["input"] and tx["input"] != "0x":

        result["type"] = "DEX_TRANSACTION"

    return result


# ============================================================
# COPY TRADE ENGINE
# ============================================================

async def execute_copy_trade(trade):

    """
    This function is intentionally disabled.

    Once the correct Sidra DEX Router ABI and address
    are confirmed, this function can construct:

        approve()
        swapExactTokensForTokens()
        swapExactETHForTokens()
        swapTokensForExactTokens()

    etc.
    """

    if not LIVE_TRADING:

        logger.info(
            "Copy trade detected but LIVE_TRADING=False"
        )

        return False

    # ========================================================
    # REAL DEX EXECUTION WILL GO HERE
    # ========================================================

    logger.warning(
        "LIVE TRADING requested but DEX executor "
        "has not been configured."
    )

    return False


# ============================================================
# TELEGRAM NOTIFICATION
# ============================================================

async def notify_trade(application, trade):

    text = f"""
🚨 COPY TRADE DETECTED

Type:
{trade["type"]}

Wallet:
{trade["from"]}

Contract:
{trade["to"]}

Native value:
{trade["value"]}

Transaction:
{trade["hash"]}

⚠️ Detection only.
"""

    for user_id in list(subscribers):

        try:

            await application.bot.send_message(
                chat_id=user_id,
                text=text
            )

        except Exception as e:

            logger.error(
                f"Telegram notification error: {e}"
            )


# ============================================================
# BLOCKCHAIN MONITOR
# ============================================================

async def monitor_wallet(application):

    global last_block

    logger.info(
        "Blockchain monitor started."
    )

    while True:

        try:

            if not bot_running or not tracked_wallet:

                await asyncio.sleep(CHECK_INTERVAL)

                continue

            current_block = w3.eth.block_number

            if last_block is None:

                last_block = current_block

                await asyncio.sleep(CHECK_INTERVAL)

                continue

            if current_block <= last_block:

                await asyncio.sleep(CHECK_INTERVAL)

                continue

            for block_number in range(
                last_block + 1,
                current_block + 1
            ):

                block = w3.eth.get_block(
                    block_number,
                    full_transactions=True
                )

                for tx in block["transactions"]:

                    sender = tx["from"].lower()

                    if sender != tracked_wallet:

                        continue

                    trade = analyze_transaction(tx)

                    if not trade:

                        continue

                    logger.info(
                        f"Detected transaction: "
                        f"{trade['hash']}"
                    )

                    await notify_trade(
                        application,
                        trade
                    )

                    await execute_copy_trade(
                        trade
                    )

            last_block = current_block

        except Exception as e:

            logger.error(
                f"Monitor error: {e}"
            )

        await asyncio.sleep(CHECK_INTERVAL)


# ============================================================
# APPLICATION STARTUP
# ============================================================

async def post_init(application):

    asyncio.create_task(
        monitor_wallet(application)
    )

    logger.info(
        "Copy trading monitor task created."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    if not TELEGRAM_TOKEN:

        raise RuntimeError(
            "TELEGRAM_TOKEN is missing."
        )

    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    application.add_handler(
        CommandHandler(
            "status",
            status
        )
    )

    application.add_handler(
        CommandHandler(
            "setwallet",
            set_wallet
        )
    )

    application.add_handler(
        CommandHandler(
            "wallet",
            wallet
        )
    )

    application.add_handler(
        CommandHandler(
            "startcopy",
            start_copy
        )
    )

    application.add_handler(
        CommandHandler(
            "stopcopy",
            stop_copy
        )
    )

    application.add_handler(
        CommandHandler(
            "settings",
            settings
        )
    )

    logger.info(
        "Telegram Copy Trading Bot starting..."
    )

    application.run_polling()


if __name__ == "__main__":

    main()
