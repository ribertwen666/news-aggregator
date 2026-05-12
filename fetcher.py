from dataclasses import dataclass
from typing import List
import requests
import feedparser
import json
import re


@dataclass
class Article:
    title: str
    url: str
    source: str
    category: str
    score: float = 50.0


STOCK_KW = ["股", "涨", "跌", "A股", "沪指", "深指", "创业板", "科创", "板块", "涨停",
             "跌停", "市值", "分红", "营收", "净利", "业绩", "回购", "减持", "上市"]
FINANCE_KW = ["GDP", "央行", "利率", "汇率", "通胀", "CPI", "PPI", "人民币", "美元",
               "欧元", "加息", "降息", "债券", "基金", "理财", "保险", "银行", "房贷",
               "楼", "房价", "税", "补贴", "预算", "赤字", "贸易", "进口", "出口"]
TECH_KW = ["AI", "人工智能", "芯片", "半导体", "5G", "6G", "华为", "苹果", "特斯拉",
            "新能源", "电池", "手机", "电脑", "互联网", "算法", "机器人", "无人机",
            "卫星", "火箭", "SpaceX", "OpenAI", "GPT", "大模型", "自动驾驶"]
POLITICS_KW = ["习近平", "总理", "外交部", "国防", "军队", "台湾", "香港", "南海",
                "中美", "中欧", "中日", "中俄", "联合国", "制裁", "法案", "选举",
                "总统", "议会", "白宫", "北约", "欧盟", "俄罗斯", "乌克兰"]


def classify_by_keywords(title: str) -> str:
    t = title
    stock_score = sum(1 for kw in STOCK_KW if kw in t)
    finance_score = sum(1 for kw in FINANCE_KW if kw in t)
    tech_score = sum(1 for kw in TECH_KW if kw in t)
    politics_score = sum(1 for kw in POLITICS_KW if kw in t)

    scores = {"stock": stock_score, "finance": finance_score,
              "tech": tech_score, "politics": politics_score,
              "weird": 0}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "weird"


def _rss_fetch(url: str, source: str, category: str,
               limit: int = 10, base_score: float = 60.0) -> List[Article]:
    articles: List[Article] = []
    try:
        feed = feedparser.parse(url)
        for i, entry in enumerate(feed.entries[:limit]):
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            if title:
                cat = classify_by_keywords(title) if category == "auto" else category
                articles.append(Article(
                    title=title, url=link, source=source,
                    category=cat, score=base_score - i
                ))
    except Exception:
        pass
    return articles


def _api_fetch(url: str, source: str, category: str,
               items_path: List[str], title_key: str, url_key: str,
               limit: int = 10, base_score: float = 65.0,
               url_prefix: str = "") -> List[Article]:
    articles: List[Article] = []
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = resp.json()
        items = data
        for key in items_path:
            items = items.get(key, []) if isinstance(items, dict) else items
        if isinstance(items, dict):
            items = list(items.values())
        for i, item in enumerate(items[:limit]):
            if not isinstance(item, dict):
                continue
            title = item.get(title_key, "").strip()
            u = item.get(url_key, "")
            if url_prefix:
                u = url_prefix + str(u)
            if title:
                cat = classify_by_keywords(title) if category == "auto" else category
                articles.append(Article(
                    title=title, url=u, source=source,
                    category=cat, score=base_score - i
                ))
    except Exception:
        pass
    return articles


def fetch_36kr() -> List[Article]:
    return _rss_fetch("https://36kr.com/feed", "36氪", "tech", limit=10, base_score=70.0)


def fetch_sina_finance() -> List[Article]:
    return _api_fetch(
        "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2513&k=&num=10&page=1",
        "新浪财经", "auto",
        ["result", "data"], "title", "url",
        limit=10, base_score=68.0
    )


def fetch_10jqka() -> List[Article]:
    return _api_fetch(
        "https://news.10jqka.com.cn/tapp/news/push/stock/?page=1&tag=",
        "同花顺", "auto",
        ["data", "list"], "title", "url",
        limit=15, base_score=72.0,
        url_prefix="https://news.10jqka.com.cn/tapp/news/push/stock/"
    )


def fetch_wallstreetcn() -> List[Article]:
    return _api_fetch(
        "https://api-one.wallstcn.com/apiv1/content/lives?channel=global-channel&limit=10",
        "华尔街见闻", "finance",
        ["data", "items"], "title", "id",
        limit=10, base_score=66.0,
        url_prefix="https://wallstreetcn.com/livenews/"
    )


def fetch_baidu_hot() -> List[Article]:
    articles: List[Article] = []
    try:
        resp = requests.get(
            "https://top.baidu.com/board?tab=realtime",
            headers={"User-Agent": "Mozilla/5.0"}, timeout=10
        )
        html = resp.text
        start_marker = "<!--s-data:"
        end_marker = "-->"
        s = html.find(start_marker)
        if s == -1:
            return articles
        s += len(start_marker)
        e = html.find(end_marker, s)
        if e == -1:
            return articles
        data = json.loads(html[s:e].strip())
        cards = data.get("data", {}).get("cards", [{}])[0]
        items = cards.get("content", [])
        for i, item in enumerate(items[:12]):
            title = item.get("word", "").strip()
            u = item.get("url", "")
            if title:
                cat = classify_by_keywords(title)
                articles.append(Article(
                    title=title, url=u, source="百度热搜",
                    category=cat, score=65.0 - i
                ))
    except Exception:
        pass
    return articles


def fetch_toutiao() -> List[Article]:
    articles: List[Article] = []
    try:
        resp = requests.get(
            "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
            headers={"User-Agent": "Mozilla/5.0"}, timeout=10
        )
        data = resp.json()
        items = data.get("data", [])
        for i, item in enumerate(items[:12]):
            title = item.get("Title", "").strip()
            u = "https://www.toutiao.com/trending/" + str(item.get("ClusterIdStr", ""))
            if title:
                cat = classify_by_keywords(title)
                articles.append(Article(
                    title=title, url=u, source="今日头条",
                    category=cat, score=63.0 - i
                ))
    except Exception:
        pass
    return articles


def fetch_all() -> List[Article]:
    results: List[Article] = []
    results.extend(fetch_10jqka())
    results.extend(fetch_36kr())
    results.extend(fetch_baidu_hot())
    results.extend(fetch_toutiao())
    results.extend(fetch_sina_finance())
    results.extend(fetch_wallstreetcn())
    return results
