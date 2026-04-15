# Text Stats Ai

> By [MEOK AI Labs](https://meok.ai) — MEOK AI Labs MCP Server

Text Stats AI MCP Server — Text analysis tools.

## Installation

```bash
pip install text-stats-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install text-stats-ai-mcp
```

## Tools

### `word_count`
Comprehensive word, character, sentence, and paragraph counting.

**Parameters:**
- `text` (str)

### `reading_time`
Estimate reading time at given words-per-minute (default 238 adult average).

**Parameters:**
- `text` (str)
- `wpm` (int)

### `keyword_density`
Analyze keyword frequency and density in text.

**Parameters:**
- `text` (str)
- `top_n` (int)
- `min_length` (int)

### `sentiment_score`
Basic sentiment analysis using lexicon-based scoring.

**Parameters:**
- `text` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/text-stats-ai-mcp](https://github.com/CSOAI-ORG/text-stats-ai-mcp)
- **PyPI**: [pypi.org/project/text-stats-ai-mcp](https://pypi.org/project/text-stats-ai-mcp/)

## License

MIT — MEOK AI Labs
