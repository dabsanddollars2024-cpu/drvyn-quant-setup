#!/usr/bin/env python3
"""
DRVYN Research Web Search Agent
"""

import os
import json
import time
import requests
import re
import itertools
import urllib.parse
from flask import Flask, request, jsonify
from urllib.parse import quote_plus

app = Flask(__name__)

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# Rotating user agents to avoid DDG rate limiting
DDG_HEADERS_LIST = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
]
_ddg_ua_cycle = itertools.cycle(DDG_HEADERS_LIST)

def get_ddg_headers():
    ua = next(_ddg_ua_cycle)
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

def duckduckgo_search(query, max_results=10):
    """Search DuckDuckGo via POST with rotating UAs"""
    for attempt in range(3):
        try:
            headers = get_ddg_headers()
            r = requests.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query, "kl": "us-en"},
                headers=headers,
                timeout=15
            )
            if r.status_code == 200 and len(r.text) > 5000:
                # Parse title+url pairs and snippets separately
                title_url_pattern = r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
                snippet_pattern = r'class="result__snippet"[^>]*>(.*?)</a>'
                url_titles = re.findall(title_url_pattern, r.text, re.DOTALL)
                snippets = re.findall(snippet_pattern, r.text, re.DOTALL)
                results = []
                for i, (url, title) in enumerate(url_titles[:max_results]):
                    if "uddg=" in url:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                        if "uddg" in parsed:
                            url = parsed["uddg"][0]
                    title_clean = re.sub(r'<[^>]+>', '', title).strip()[:200]
                    snippet = ""
                    if i < len(snippets):
                        snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:500]
                    results.append({
                        "url": url,
                        "title": title_clean,
                        "snippet": snippet
                    })
                if results:
                    return results
        except Exception as e:
            if attempt == 2:
                return [{"error": f"DDG failed: {str(e)}"}]
        time.sleep(1)
    return []

def tavily_search(query, max_results=5):
    """Search via Tavily API"""
    if not TAVILY_API_KEY:
        return None
    try:
        r = requests.post("https://api.tavily.com/search", json={
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": max_results,
            "include_answer": True
        }, timeout=20)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def wikipedia_search(query, max_results=3):
    """Search Wikipedia REST API"""
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": max_results
            },
            headers={"User-Agent": "DRVYN-Research/1.0"},
            timeout=10
        )
        data = r.json()
        results = []
        for hit in data.get("query", {}).get("search", []):
            results.append({
                "url": "https://en.wikipedia.org/wiki/" + hit["title"].replace(" ", "_"),
                "title": hit["title"],
                "snippet": re.sub(r'<[^>]+>', '', hit.get("snippet", ""))[:500]
            })
        return results
    except Exception as e:
        return []

def reddit_search(query, max_results=5):
    """Search Reddit via JSON API"""
    try:
        r = requests.get(
            f"https://www.reddit.com/search.json?q={quote_plus(query)}&limit={max_results}",
            headers={"User-Agent": "DRVYN-Research/1.0"},
            timeout=15
        )
        data = r.json()
        results = []
        for post in data.get("data", {}).get("children", []):
            d = post.get("data", {})
            results.append({
                "url": "https://reddit.com" + d.get("permalink", ""),
                "title": d.get("title", ""),
                "snippet": d.get("selftext", "")[:500],
                "score": d.get("score", 0),
                "subreddit": d.get("subreddit", "")
            })
        return results
    except Exception as e:
        return []

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "tavily": bool(TAVILY_API_KEY)})

@app.route("/search", methods=["POST", "GET"])
def search():
    sources = ["ddg"]
    if request.method == "GET":
        q = request.args.get("q", "")
        max_r = int(request.args.get("max", 10))
        sources = request.args.get("sources", "ddg").split(",")
    else:
        body = request.get_json(force=True, silent=True) or {}
        q = body.get("query", body.get("q", ""))
        max_r = int(body.get("max_results", body.get("max", 10)))
        sources = body.get("sources", ["ddg"])
        if isinstance(sources, str):
            sources = sources.split(",")
    if not q:
        return jsonify({"error": "no query"}), 400
    
    out = {"query": q, "sources_used": [], "results": []}
    
    if "tavily" in sources and TAVILY_API_KEY:
        tav = tavily_search(q, max_r)
        if tav and "results" in tav:
            out["sources_used"].append("tavily")
            out["results"].extend(tav["results"])
            out["tavily_answer"] = tav.get("answer", "")
    
    if "ddg" in sources:
        ddg = duckduckgo_search(q, max_r)
        if ddg and not any("error" in r for r in ddg if isinstance(r, dict)):
            out["sources_used"].append("ddg")
            out["results"].extend(ddg)
    
    if "wikipedia" in sources:
        wiki = wikipedia_search(q, min(max_r, 5))
        if wiki:
            out["sources_used"].append("wikipedia")
            out["results"].extend(wiki)
    
    if "reddit" in sources:
        red = reddit_search(q, min(max_r, 5))
        if red:
            out["sources_used"].append("reddit")
            out["results"].extend(red)
    
    out["count"] = len(out["results"])
    return jsonify(out)

@app.route("/fetch", methods=["POST", "GET"])
def fetch_url():
    if request.method == "GET":
        url = request.args.get("url", "")
        max_len = int(request.args.get("max", 15000))
    else:
        body = request.get_json(force=True, silent=True) or {}
        url = body.get("url", "")
        max_len = int(body.get("max_length", 15000))
    if not url:
        return jsonify({"error": "no url"}), 400
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"},
            timeout=20
        )
        from html.parser import HTMLParser
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.skip = False
            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style", "nav", "footer", "header"):
                    self.skip = True
            def handle_endtag(self, tag):
                if tag in ("script", "style", "nav", "footer", "header"):
                    self.skip = False
            def handle_data(self, data):
                if not self.skip:
                    text = data.strip()
                    if text:
                        self.text.append(text)
        ext = TextExtractor()
        ext.feed(r.text)
        clean = " ".join(ext.text)
        clean = re.sub(r"\s+", " ", clean)
        return jsonify({
            "url": url,
            "status": r.status_code,
            "content_length": len(clean),
            "content": clean[:max_len]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5007))
    print(f"DRVYN Research Search Agent starting on port {port}")
    print(f"Tavily enabled: {bool(TAVILY_API_KEY)}")
    app.run(host="0.0.0.0", port=port, debug=False)
