# Claude Code + Local LLM Integration

Wires the abliterated models into Claude Code as a **fallback model** for trading queries. When Claude Code sees a query matching trading patterns, it routes to your local vLLM server.

## What This Does

```
You → Claude Code
  ↓
  [Pattern match on query]
  ↓
  ┌─────────────────────────────────┐
  │  Trading?  → Local vLLM         │  ← Stays on PC, no data leaves
  │  Coding?  → Local vLLM (Coder)  │  ← No API cost
  │  Other?   → Claude API          │  ← Best quality
  └─────────────────────────────────┘
```

## Setup Steps

### 1. Start the Coder Model Server

```cmd
cd %USERPROFILE%\quant-lab-llms
serve-model.bat qwen-coder
```

Server runs on `http://localhost:8001`. Leave it running in a terminal.

### 2. Configure Claude Code MCP

Edit your Claude Code MCP config (usually at `%USERPROFILE%\.claude\.mcp.json` or similar — check Claude Code docs for exact path).

Add this:

```json
{
  "mcpServers": {
    "local-coder": {
      "type": "sse",
      "url": "http://localhost:8001/v1"
    }
  }
}
```

### 3. Test From Claude Code

In any Claude Code session:

> "Use the local-coder tool to write a Pine Script EMA crossover"

Claude Code should route to your local model.

## Optional: Auto-Routing Script

Create `~/.claude/hooks/route-trading-queries.py` (or wherever Claude Code expects hooks):

```python
#!/usr/bin/env python3
"""Route trading queries to local vLLM instead of Claude API."""
import sys
import json
import re

TRADING_PATTERNS = [
    r"\bpine\b", r"\bbacktest\b", r"\bema\b", r"\bsma\b",
    r"\brsi\b", r"\bmacd\b", r"\b(strategy|strategies)\b",
    r"\bquant\b", r"\btrading\b", r"\bindicator\b",
    r"\b(NQ|ES|CL|GC)\b",  # futures tickers
]

def is_trading_query(prompt):
    p = prompt.lower()
    return any(re.search(pat, p) for pat in TRADING_PATTERNS)

# ... (custom routing logic)
```

This is a more advanced setup. For now, just call the local model manually with a system prompt:

> "You are a trading strategy expert. Use the local-coder tool to: ..."

## Use Cases

### Pine Script Generation

> "Write a Pine Script v5 strategy that goes long on 9/30 EMA crossover with a volume filter, exits on ATR trailing stop."

Routes to Qwen2.5-Coder-7B (good at code).

### Strategy Logic

> "Why would a 9/30 EMA crossover be effective in trending markets but choppy in ranges?"

Routes to DeepSeek-R1 (chain-of-thought reasoning).

### Quick Indicator Parsing

> "Parse this TradingView alert: 'ES1! 9 EMA crossed above 30 EMA on 5min' — what's the setup?"

Routes to Phi-3.5-mini (fast, lightweight).

### Research Synthesis

> "Summarize the recent NQ volume profile research from these 3 papers..."

Routes to Llama 3.1-8B (general synthesis).

## Cost Savings

- **Before:** Every Claude API call = $$ per token
- **After:** Trading queries stay local = $0
- **Quality:** Trading-specific 7B models are competitive with Claude for these tasks

## Security

- All processing stays on your PC
- Trading strategies never leave the local network
- No API logs of your trading ideas
- vLLM runs on `localhost` only (not exposed externally)

## Performance

- First query: 2-5 sec (model loads context)
- Subsequent: ~25-40 tok/s (depends on model)
- Quant research loops can run 100% locally
