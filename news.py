#!/usr/bin/env python3
import argparse
from fetcher import fetch_all
from ranker import deduplicate
from display import display


def main():
    parser = argparse.ArgumentParser(description="中文新闻聚合器 - 每日要闻 TOP 20")
    parser.add_argument("--category", choices=["stock", "finance", "tech", "politics", "weird", "all"],
                        default="all", help="按类别筛选（默认: all）")
    parser.add_argument("--limit", type=int, default=20, help="显示条数（默认: 20）")
    args = parser.parse_args()

    print("正在聚合新闻...", end="", flush=True)
    articles = fetch_all()
    print(f" 抓取 {len(articles)} 条")

    top = deduplicate(articles)[:args.limit]
    display(top, category=args.category)


if __name__ == "__main__":
    main()
