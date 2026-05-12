from typing import List
from fetcher import Article

CATEGORY_COLORS = {
    "stock": "\033[91m",      # 红
    "finance": "\033[94m",    # 蓝
    "tech": "\033[92m",       # 绿
    "politics": "\033[93m",   # 黄
    "weird": "\033[95m",      # 紫
}
CATEGORY_LABELS = {
    "stock": "股票",
    "finance": "财经",
    "tech": "科技",
    "politics": "时事",
    "weird": "奇闻",
}
RESET = "\033[0m"
BOLD = "\033[1m"


def format_article(article: Article, index: int) -> str:
    color = CATEGORY_COLORS.get(article.category, "")
    label = CATEGORY_LABELS.get(article.category, article.category)
    num = f"{index + 1:2d}"
    tag = f"[{label}]"
    return f"{BOLD}{num}.{RESET} {color}{tag}{RESET} {article.title}  {BOLD}{RESET}\033[90m({article.source})\033[0m"


def display(articles: List[Article], category: str = "all"):
    if category != "all":
        articles = [a for a in articles if a.category == category]

    print(f"\n{BOLD}今日要闻 TOP {len(articles)}{RESET}\n")
    for i, a in enumerate(articles):
        print(format_article(a, i))
    print()
