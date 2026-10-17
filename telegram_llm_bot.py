#!/usr/bin/env python3
"""
DRVYN Telegram Bot - polls Telegram for /ask messages, sends to LLM bridge
Requires: TELEGRAM_BOT_TOKEN env var (from @BotFather)
"""

import os
import sys
import time
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BRIDGE_URL = os.environ.get("BRIDGE_URL", "http://localhost:5008")
BRIDGE_KEY = os.environ.get("DRVYN_BRIDGE_KEY", "drvyn-bridge-2026-10-15-xR8mN2kP")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "DRVYN Local LLM Bot\n\n"
        "Commands:\n"
        "/ask <question> - Research + LLM answer (slower, more accurate)\n"
        "/quick <question> - Direct LLM (faster, no web)\n"
        "/status - Check LLM + bridge status\n"
        "/help - Show this message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(BRIDGE_URL + "/health", timeout=5)
        await update.message.reply_text(f"Bridge: {r.json()}")
    except Exception as e:
        await update.message.reply_text(f"Bridge error: {e}")

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ask <your question>")
        return
    question = " ".join(context.args)
    await update.message.reply_text(f"Researching: {question[:100]}...")
    
    try:
        r = requests.get(BRIDGE_URL + "/ask", 
                        params={"q": question, "key": BRIDGE_KEY},
                        timeout=300)
        data = r.json()
        if "answer" in data:
            answer = data["answer"]
            # Truncate for Telegram (4096 char limit)
            if len(answer) > 3500:
                answer = answer[:3500] + "\n\n[truncated, full answer at bridge]"
            msg = "*Q:* " + question[:200] + "\n\n*A:* " + answer
            # Add sources
            if data.get("sources"):
                msg += "\n\n*Sources:*"
                for i, s in enumerate(data["sources"][:5], 1):
                    msg += f"\n[{i}] {s['title'][:60]}\n  {s['url']}"
            await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await update.message.reply_text(f"Error: {data.get('error', 'unknown')}")
    except Exception as e:
        await update.message.reply_text(f"Bridge error: {e}")

async def quick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /quick <your question>")
        return
    question = " ".join(context.args)
    await update.message.reply_text(f"Thinking: {question[:100]}...")
    
    try:
        r = requests.get(BRIDGE_URL + "/quick", 
                        params={"q": question, "key": BRIDGE_KEY},
                        timeout=180)
        data = r.json()
        if "answer" in data:
            answer = data["answer"]
            if len(answer) > 3500:
                answer = answer[:3500] + "\n\n[truncated]"
            await update.message.reply_text(f"*Q:* {question[:200]}\n\n*A:* {answer}", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"Error: {data.get('error', 'unknown')}")
    except Exception as e:
        await update.message.reply_text(f"Bridge error: {e}")

def main():
    if not BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN env var not set", file=sys.stderr)
        print("To create a bot:", file=sys.stderr)
        print("  1. Open Telegram, search @BotFather", file=sys.stderr)
        print("  2. Send /newbot", file=sys.stderr)
        print("  3. Choose name and username", file=sys.stderr)
        print("  4. Copy the token", file=sys.stderr)
        print("  5. Set TELEGRAM_BOT_TOKEN=<token> and restart", file=sys.stderr)
        sys.exit(1)
    
    print(f"DRVYN Telegram Bot starting")
    print(f"  Bridge: {BRIDGE_URL}")
    print(f"  Bot token: {BOT_TOKEN[:10]}...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("quick", quick_command))
    
    print("Polling for messages...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
