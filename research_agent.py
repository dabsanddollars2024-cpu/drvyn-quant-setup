#!/usr/bin/env python3
"""DRVYN Research Agent - search + LLM synthesis"""

import os
import json
import sys
import requests
import argparse

SEARCH_URL = "http://localhost:5007"
LLM_URL = "http://100.118.115.78:8001"

def search_web(query, max_results=5, sources="ddg,wikipedia"):
    try:
        r = requests.get(SEARCH_URL + "/search",
                        params={"q": query, "max": max_results, "sources": sources},
                        timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e), "results": []}

def fetch_url(url, max_length=8000):
    try:
        r = requests.get(SEARCH_URL + "/fetch",
                        params={"url": url, "max": max_length},
                        timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e), "content": ""}

def call_llm(prompt, model="qwen-research", max_tokens=2000):
    try:
        r = requests.post(LLM_URL + "/v1/chat/completions",
                         json={
                             "model": model,
                             "messages": [{"role": "user", "content": prompt}],
                             "max_tokens": max_tokens,
                             "temperature": 0.7
                         },
                         timeout=120)
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "LLM not available (PC offline or vLLM not running)"}
    except Exception as e:
        return {"error": str(e)}

def research_with_llm(query):
    print("Searching: " + query, file=sys.stderr)
    search = search_web(query, max_results=8, sources="ddg,wikipedia,reddit")
    results = search.get("results", [])
    print("   Found " + str(len(results)) + " results", file=sys.stderr)
    if not results:
        return "No results found. Try a different query."

    context = []
    for i, r in enumerate(results[:3]):
        print("Fetching [" + str(i+1) + "/3]: " + r["title"][:60], file=sys.stderr)
        fetched = fetch_url(r["url"], max_length=5000)
        if "content" in fetched and fetched.get("content"):
            context.append({
                "title": r["title"],
                "url": r["url"],
                "content": fetched["content"][:4000]
            })

    if not context:
        return "Could not fetch any results. Try again or check the search server."

    print("Asking local LLM to synthesize...", file=sys.stderr)
    prompt_lines = [
        "You are a research assistant. Based ONLY on the following sources, answer the question thoroughly. Cite sources with [1], [2], [3] notation.",
        "",
        "QUESTION: " + query,
        "",
        "SOURCES:",
    ]
    for i, c in enumerate(context, 1):
        prompt_lines.append("")
        prompt_lines.append("[" + str(i) + "] " + c["title"] + " (" + c["url"] + ")")
        prompt_lines.append(c["content"])
    prompt_lines.append("")
    prompt_lines.append("Provide a clear, factual answer based on these sources. If the sources do not contain the answer, say so. Include citations.")
    prompt = chr(10).join(prompt_lines)

    llm_response = call_llm(prompt, max_tokens=2000)
    if "choices" in llm_response:
        return llm_response["choices"][0]["message"]["content"]
    elif "error" in llm_response:
        return "LLM unavailable: " + llm_response["error"] + chr(10) + chr(10) + "--- Raw search results ---" + chr(10) + format_results(results[:10])
    return "LLM returned unexpected response"

def format_results(results):
    if not results:
        return "No results."
    out = []
    for i, r in enumerate(results, 1):
        out.append("")
        out.append("[" + str(i) + "] " + r.get("title", "No title"))
        out.append("    " + r.get("url", ""))
        if r.get("snippet"):
            out.append("    " + r["snippet"][:300])
    return chr(10).join(out)

def main():
    parser = argparse.ArgumentParser(description="DRVYN Research Agent")
    parser.add_argument("query", nargs="*", help="Research question")
    parser.add_argument("--max", type=int, default=8, help="Max search results")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM synthesis, just return search results")
    parser.add_argument("--raw", action="store_true", help="Just search, no fetching")
    args = parser.parse_args()
    if not args.query:
        parser.print_help()
        sys.exit(1)
    query = " ".join(args.query)
    if args.raw:
        result = search_web(query, max_results=args.max)
        print(json.dumps(result, indent=2))
        return
    if args.no_llm:
        result = search_web(query, max_results=args.max)
        print("Query: " + query + chr(10))
        print(format_results(result.get("results", [])))
        return
    answer = research_with_llm(query)
    print(chr(10) + "="*60)
    print(answer)
    print("="*60)

if __name__ == "__main__":
    main()
