"""Text Stats AI MCP Server — Text analysis tools."""
import math
import re
import time
from collections import Counter
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("text-stats-ai-mcp")
_calls: dict[str, list[float]] = {}
DAILY_LIMIT = 50

def _rate_check(tool: str) -> bool:
    now = time.time()
    _calls.setdefault(tool, [])
    _calls[tool] = [t for t in _calls[tool] if t > now - 86400]
    if len(_calls[tool]) >= DAILY_LIMIT:
        return False
    _calls[tool].append(now)
    return True

@mcp.tool()
def word_count(text: str) -> dict[str, Any]:
    """Comprehensive word, character, sentence, and paragraph counting."""
    if not _rate_check("word_count"):
        return {"error": "Rate limit exceeded (50/day)"}
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    unique_words = set(w.lower().strip(".,!?;:\"'()[]{}") for w in words)
    avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
    return {
        "words": len(words), "characters": len(text), "characters_no_spaces": len(text.replace(" ", "")),
        "sentences": len(sentences), "paragraphs": len(paragraphs),
        "unique_words": len(unique_words), "avg_word_length": round(avg_word_len, 1),
        "avg_sentence_length": round(len(words) / max(len(sentences), 1), 1),
        "lines": len(text.split("\n"))
    }

@mcp.tool()
def reading_time(text: str, wpm: int = 238) -> dict[str, Any]:
    """Estimate reading time at given words-per-minute (default 238 adult average)."""
    if not _rate_check("reading_time"):
        return {"error": "Rate limit exceeded (50/day)"}
    words = len(text.split())
    minutes = words / max(wpm, 1)
    # Flesch-Kincaid readability
    sentences = len(re.split(r'[.!?]+', text))
    sentences = max(sentences, 1)
    syllables = 0
    for word in text.split():
        word = word.lower().strip(".,!?;:\"'()[]{}")
        vowels = len(re.findall(r'[aeiouy]+', word))
        syllables += max(vowels, 1)
    fk_grade = 0.39 * (words / sentences) + 11.8 * (syllables / max(words, 1)) - 15.59
    flesch = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / max(words, 1))
    if minutes < 1:
        human = f"{round(minutes * 60)} seconds"
    else:
        human = f"{math.ceil(minutes)} min"
    return {
        "word_count": words, "reading_time_minutes": round(minutes, 1),
        "human_readable": human, "wpm_used": wpm,
        "flesch_kincaid_grade": round(max(0, fk_grade), 1),
        "flesch_reading_ease": round(max(0, min(100, flesch)), 1),
        "difficulty": "Easy" if flesch > 60 else "Moderate" if flesch > 30 else "Difficult"
    }

@mcp.tool()
def keyword_density(text: str, top_n: int = 20, min_length: int = 3) -> dict[str, Any]:
    """Analyze keyword frequency and density in text."""
    if not _rate_check("keyword_density"):
        return {"error": "Rate limit exceeded (50/day)"}
    words = [w.lower().strip(".,!?;:\"'()[]{}") for w in text.split()]
    words = [w for w in words if len(w) >= min_length]
    total = len(words)
    if total == 0:
        return {"error": "No words found meeting minimum length"}
    stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her",
                  "was", "one", "our", "out", "has", "have", "been", "from", "this", "that",
                  "with", "they", "will", "each", "make", "like", "long", "very", "when", "what"}
    filtered = [w for w in words if w not in stop_words]
    counter = Counter(filtered)
    top = counter.most_common(top_n)
    keywords = [{"word": w, "count": c, "density_pct": round(c / total * 100, 2)} for w, c in top]
    # Bigrams
    bigrams = [f"{filtered[i]} {filtered[i+1]}" for i in range(len(filtered) - 1)]
    bi_counter = Counter(bigrams)
    top_bigrams = [{"phrase": p, "count": c} for p, c in bi_counter.most_common(10)]
    return {"keywords": keywords, "bigrams": top_bigrams, "total_words": total, "unique_words": len(set(filtered))}

@mcp.tool()
def sentiment_score(text: str) -> dict[str, Any]:
    """Basic sentiment analysis using lexicon-based scoring."""
    if not _rate_check("sentiment_score"):
        return {"error": "Rate limit exceeded (50/day)"}
    positive = {"good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "happy",
                "best", "beautiful", "perfect", "awesome", "brilliant", "outstanding", "superb",
                "enjoy", "pleased", "delighted", "impressive", "remarkable", "success", "win",
                "exciting", "nice", "positive", "helpful", "easy", "fast", "clean", "strong"}
    negative = {"bad", "terrible", "awful", "horrible", "hate", "worst", "ugly", "poor", "fail",
                "broken", "wrong", "error", "slow", "hard", "difficult", "annoying", "frustrating",
                "disappointing", "useless", "painful", "confused", "angry", "sad", "weak", "stupid",
                "bug", "crash", "problem", "issue", "negative", "complex", "mess", "damage"}
    intensifiers = {"very", "extremely", "really", "absolutely", "totally", "incredibly"}
    negators = {"not", "no", "never", "neither", "nobody", "nothing", "nowhere", "nor", "cannot", "don't", "doesn't", "won't"}
    words = [w.lower().strip(".,!?;:\"'()[]{}") for w in text.split()]
    pos_count = neg_count = 0
    pos_words, neg_words = [], []
    for i, w in enumerate(words):
        multiplier = 1.5 if i > 0 and words[i-1] in intensifiers else 1.0
        negated = i > 0 and words[i-1] in negators
        if w in positive:
            if negated:
                neg_count += multiplier
                neg_words.append(f"not {w}")
            else:
                pos_count += multiplier
                pos_words.append(w)
        elif w in negative:
            if negated:
                pos_count += multiplier
                pos_words.append(f"not {w}")
            else:
                neg_count += multiplier
                neg_words.append(w)
    total = pos_count + neg_count
    if total == 0:
        score = 0.0
        label = "Neutral"
    else:
        score = (pos_count - neg_count) / total
        label = "Positive" if score > 0.2 else "Negative" if score < -0.2 else "Neutral"
    return {
        "score": round(score, 3), "label": label,
        "positive_count": round(pos_count, 1), "negative_count": round(neg_count, 1),
        "positive_words": pos_words[:10], "negative_words": neg_words[:10],
        "confidence": round(min(total / max(len(words), 1), 1.0), 2)
    }

if __name__ == "__main__":
    mcp.run()
