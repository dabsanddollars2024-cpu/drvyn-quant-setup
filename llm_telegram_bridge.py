#!/usr/bin/env python3
"""
DRVYN Telegram-Bot-to-Local-LLM Bridge
- HTTP endpoint accepts questions
- Calls search server + local LLM
- Returns synthesized answer
- Optional: posts to Telegram via bot API
"""

import os
import json
import time
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SEARCH_URL = "http://localhost:5007"
LLM_URL = "http://100.118.115.78:8001"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
API_KEY = os.environ.get("DRVYN_BRIDGE_KEY", "drvyn-bridge-2026-10-15-xR8mN2kP")

def check_api_key(req):
    """Check API key from query param or header"""
    provided = (req.args.get("key", "") or 
                req.headers.get("X-API-Key", "") or
                (req.get_json(force=True, silent=True) or {}).get("api_key", ""))
    return provided == API_KEY

def search_web(query, max_results=8):
    try:
        r = requests.get(SEARCH_URL + "/search",
                        params={"q": query, "max": max_results, "sources": "ddg,wikipedia,reddit"},
                        timeout=45)
        return r.json()
    except Exception as e:
        return {"error": str(e), "results": []}

def fetch_url(url, max_length=5000):
    try:
        r = requests.get(SEARCH_URL + "/fetch",
                        params={"url": url, "max": max_length},
                        timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e), "content": ""}

def call_llm(prompt, max_tokens=2000):
    try:
        r = requests.post(LLM_URL + "/v1/chat/completions",
                         json={
                             "model": "qwen-research",
                             "messages": [{"role": "user", "content": prompt}],
                             "max_tokens": max_tokens,
                             "temperature": 0.7
                         },
                         timeout=300)
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "PC offline or vLLM not running"}
    except Exception as e:
        return {"error": str(e)}

def send_telegram(message):
    """Send a message to Telegram chat"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {"error": "no telegram config"}
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=15
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def research(query, max_results=8, fetch_top=3):
    """Full research pipeline: search + fetch + LLM synthesis"""
    t0 = time.time()
    
    # 1. Search
    search = search_web(query, max_results)
    results = search.get("results", [])
    
    # 2. Fetch top N
    context = []
    for r in results[:fetch_top]:
        fetched = fetch_url(r["url"], 4000)
        if "content" in fetched and fetched.get("content"):
            context.append({
                "title": r["title"],
                "url": r["url"],
                "content": fetched["content"][:3500]
            })
    
    if not context:
        return {"error": "No results fetched", "results": results}
    
    # 3. Build prompt
    prompt_lines = [
        "You are a research assistant. Based ONLY on the following sources, answer the question thoroughly. Cite with [1], [2], [3].",
        "",
        "QUESTION: " + query,
        "",
        "SOURCES:",
    ]
    for i, c in enumerate(context, 1):
        prompt_lines.append("")
        prompt_lines.append("[" + str(i) + "] " + c["title"])
        prompt_lines.append("URL: " + c["url"])
        prompt_lines.append(c["content"])
    prompt_lines.append("")
    prompt_lines.append("Answer clearly with citations. If sources don't contain the answer, say so.")
    prompt = chr(10).join(prompt_lines)
    
    # 4. Call LLM
    llm_response = call_llm(prompt, max_tokens=2000)
    if "choices" in llm_response:
        answer = llm_response["choices"][0]["message"]["content"]
        usage = llm_response.get("usage", {})
        timing = llm_response.get("timing", {})
        return {
            "status": "ok",
            "query": query,
            "answer": answer,
            "sources": [{"title": c["title"], "url": c["url"]} for c in context],
            "tokens": usage,
            "timing_sec": round(time.time() - t0, 2),
            "llm_timing": timing,
        }
    elif "error" in llm_response:
        return {
            "status": "llm_error",
            "error": llm_response["error"],
            "fallback_results": results[:10]
        }
    return {"status": "unexpected", "response": llm_response}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "drvyn-telegram-bridge",
        "llm": LLM_URL,
        "search": SEARCH_URL,
        "telegram_configured": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    })

@app.route("/ask", methods=["POST", "GET"])
def ask():
    """Main endpoint - ask a research question"""
    if not check_api_key(request):
        return jsonify({"error": "invalid api key"}), 401
    if request.method == "GET":
        q = request.args.get("q", "").strip()
        async_mode = request.args.get("async", "false").lower() == "true"
    else:
        body = request.get_json(force=True, silent=True) or {}
        q = body.get("question", body.get("q", "")).strip()
        async_mode = body.get("async", False)
    
    if not q:
        return jsonify({"error": "no question provided"}), 400
    
    if async_mode:
        # Run in background, return immediately
        def run_async():
            result = research(q)
            # Send to Telegram if configured
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                if "answer" in result:
                    msg = f"*Q:* {q}\n\n*A:* {result['answer'][:3500]}"
                else:
                    msg = f"*Q:* {q}\n\n*Error:* {result.get('error', 'unknown')}"
                send_telegram(msg)
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
        return jsonify({"status": "queued", "question": q, "mode": "async"})
    
    result = research(q)
    return jsonify(result)

@app.route("/quick", methods=["POST", "GET"])
def quick_ask():
    """Just ask the LLM directly, no web search"""
    if not check_api_key(request):
        return jsonify({"error": "invalid api key"}), 401
    if request.method == "GET":
        q = request.args.get("q", "").strip()
    else:
        body = request.get_json(force=True, silent=True) or {}
        q = body.get("question", body.get("q", "")).strip()
    
    if not q:
        return jsonify({"error": "no question"}), 400
    
    t0 = time.time()
    result = call_llm(q, max_tokens=1500)
    if "choices" in result:
        answer = result["choices"][0]["message"]["content"]
        return jsonify({
            "status": "ok",
            "question": q,
            "answer": answer,
            "tokens": result.get("usage", {}),
            "timing_sec": round(time.time() - t0, 2)
        })
    return jsonify({"status": "error", "error": result.get("error", "unknown")})

@app.route("/telegram-webhook", methods=["POST"])
def telegram_webhook():
    """Receive messages from Telegram bot"""
    update = request.get_json(force=True)
    message = update.get("message", {})
    text = message.get("text", "").strip()
    chat_id = message.get("chat", {}).get("id", "")
    
    if not text or not chat_id:
        return jsonify({"ok": True})
    
    # Strip /ask prefix if present
    if text.startswith("/ask"):
        text = text[4:].strip()
    elif text.startswith("/"):
        return jsonify({"ok": True})  # ignore other commands
    
    if not text:
        return jsonify({"ok": True})
    
    # Run research async and post back
    def run_and_reply():
        result = research(text, fetch_top=3)
        if "answer" in result:
            reply = "*Q:* " + text + "\n\n*A:* " + result["answer"][:3800]
            if result.get("sources"):
                reply += "\n\n*Sources:*"
                for i, s in enumerate(result["sources"][:5], 1):
                    reply += f"\n[{i}] {s['title'][:80]}"
                    reply += f"\n    {s['url']}"
        else:
            reply = "*Q:* " + text + "\n\n*Error:* " + result.get("error", "unknown")
        
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"},
                timeout=15
            )
        except:
            pass
    
    thread = threading.Thread(target=run_and_reply, daemon=True)
    thread.start()
    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5008))
    print(f"DRVYN Telegram-Bot-to-LLM Bridge on port {port}")
    print(f"  LLM: {LLM_URL}")
    print(f"  Search: {SEARCH_URL}")
    print(f"  Telegram bot configured: {bool(TELEGRAM_BOT_TOKEN)}")
    app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
