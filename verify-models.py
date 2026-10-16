#!/usr/bin/env python3
"""Quick verification of model quality after abliteration.

Runs the same test prompt through all 4 models and compares outputs.
Use to verify abliteration didn't damage coherence.
"""
import sys
import os
import time
import json
import urllib.request
from typing import Optional

# Test prompts - one per model's specialty
TEST_PROMPTS = {
    "qwen-coder": {
        "port": 8001,
        "model": "Qwen2.5-Coder-7B-Instruct-abliterated",
        "prompt": "Write a Python function that calculates the simple moving average of a list of numbers. Include a docstring.",
        "expected_keywords": ["def", "return", "moving", "average"]
    },
    "deepseek-r1": {
        "port": 8002,
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B-abliterated",
        "prompt": "If I buy 100 shares of a stock at $50 and sell at $55, but pay $10 in commissions, what's my net profit?",
        "expected_keywords": ["500", "490", "profit", "100"]
    },
    "phi35": {
        "port": 8003,
        "model": "Phi-3.5-mini-instruct-abliterated",
        "prompt": "What is 2 + 2?",
        "expected_keywords": ["4", "four"]
    },
    "llama31": {
        "port": 8004,
        "model": "Llama-3.1-8B-Instruct-abliterated",
        "prompt": "In one sentence, what's the difference between a 9 EMA and a 30 EMA in trading?",
        "expected_keywords": ["9", "30", "ema", "exponential", "moving"]
    }
}


def test_model(name: str, cfg: dict) -> dict:
    """Test a model on its specialty prompt."""
    url = f"http://localhost:{cfg['port']}/v1/chat/completions"
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": cfg["prompt"]}],
        "max_tokens": 500,
        "temperature": 0.3
    }

    start = time.time()
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            elapsed = time.time() - start

        response = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("completion_tokens", 0)
        speed = tokens / elapsed if elapsed > 0 else 0

        # Check expected keywords
        keyword_hits = sum(1 for kw in cfg["expected_keywords"] if kw.lower() in response.lower())
        keyword_score = keyword_hits / len(cfg["expected_keywords"])

        # Check for refusals (should be ~0% after abliteration)
        refusal_markers = ["i cannot", "i can't", "i'm not able", "i won't", "as an ai"]
        has_refusal = any(marker in response.lower() for marker in refusal_markers)

        return {
            "name": name,
            "status": "OK",
            "elapsed_sec": round(elapsed, 2),
            "tokens": tokens,
            "speed_tok_per_sec": round(speed, 1),
            "keyword_score": round(keyword_score, 2),
            "has_refusal": has_refusal,
            "response_preview": response[:200] + "..." if len(response) > 200 else response
        }
    except Exception as e:
        return {
            "name": name,
            "status": f"ERROR: {e}",
            "elapsed_sec": round(time.time() - start, 2)
        }


def main():
    print("=" * 70)
    print("QUANT LAB MODEL VERIFICATION")
    print("=" * 70)
    print()
    print("Make sure each model server is running on its port.")
    print("This script tests all 4 sequentially.")
    print()

    # Test models that are running
    to_test = []
    for name, cfg in TEST_PROMPTS.items():
        url = f"http://localhost:{cfg['port']}/v1/models"
        try:
            urllib.request.urlopen(url, timeout=2)
            to_test.append((name, cfg))
        except Exception:
            print(f"[SKIP] {name} (port {cfg['port']} not responding)")

    if not to_test:
        print("No model servers running. Start them with serve-model.bat first.")
        sys.exit(1)

    print(f"Testing {len(to_test)} model(s)...")
    print()

    results = []
    for name, cfg in to_test:
        print(f"Testing {name}...")
        result = test_model(name, cfg)
        results.append(result)

        if result["status"] == "OK":
            print(f"  Status:     OK")
            print(f"  Time:       {result['elapsed_sec']}s")
            print(f"  Tokens:     {result['tokens']}")
            print(f"  Speed:      {result['speed_tok_per_sec']} tok/s")
            print(f"  Keywords:   {result['keyword_score']*100:.0f}% match")
            print(f"  Refusal:    {'YES (BAD)' if result['has_refusal'] else 'No (good)'}")
            print(f"  Preview:    {result['response_preview']}")
        else:
            print(f"  Status:     {result['status']}")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    ok = sum(1 for r in results if r["status"] == "OK")
    refusals = sum(1 for r in results if r.get("has_refusal"))
    print(f"Models tested:    {len(results)}")
    print(f"Working:          {ok}/{len(results)}")
    print(f"Refusals:         {refusals}/{len(results)} (should be 0)")
    print()

    if refusals > 0:
        print("WARNING: Some models still refuse. Re-abliterate with --method aggressive")


if __name__ == "__main__":
    main()
