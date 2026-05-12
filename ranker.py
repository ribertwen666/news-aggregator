import re
from difflib import SequenceMatcher
from typing import List
from fetcher import Article


def normalize_title(title: str) -> str:
    result = re.sub(r"[，。！？、；：""''《》（）\s,.!?;:\"'\n\r\t]", "", title)
    return result.strip().lower()


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def deduplicate(articles: List[Article], threshold: float = 0.7) -> List[Article]:
    if not articles:
        return []
    sorted_articles = sorted(articles, key=lambda x: x.score, reverse=True)
    normalized = [normalize_title(a.title) for a in sorted_articles]
    seen: List[int] = []
    result: List[Article] = []

    for i, a in enumerate(sorted_articles):
        is_dup = False
        for j in seen:
            if _similarity(normalized[i], normalized[j]) >= threshold:
                is_dup = True
                break
        if not is_dup:
            seen.append(i)
            result.append(a)

    return result
