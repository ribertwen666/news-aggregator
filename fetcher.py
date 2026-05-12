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
    summary: str = ""


STOCK_KW = {
    # 核心行情 (高权重)
    "涨停": 3, "跌停": 3, "A股": 3, "沪指": 3, "深指": 3, "创业板": 3,
    "科创板": 3, "北交所": 3, "牛市": 3, "熊市": 3, "IPO": 3, "打新": 3,
    "涨停板": 3, "跌停板": 3, "龙头股": 3, "妖股": 3,
    # 交易行为 (中权重)
    "回购": 2, "减持": 2, "增持": 2, "分红": 2, "派息": 2, "除权": 2,
    "配股": 2, "定增": 2, "并购": 2, "重组": 2, "停牌": 2, "复牌": 2,
    "申购": 2, "中签": 2, "上市": 2, "退市": 2, "ST": 2, "大股东": 2,
    "举牌": 2, "股权": 2, "转让": 2, "要约收购": 2, "借壳": 2,
    # 财务数据 (中权重)
    "营收": 2, "净利": 2, "净利润": 2, "业绩": 2, "预增": 2, "预减": 2,
    "年报": 2, "季报": 2, "中报": 2, "财报": 2, "每股收益": 2, "EPS": 2,
    # 市场指标 (低权重)
    "市值": 1, "换手率": 1, "成交量": 1, "成交额": 1, "主力": 1,
    "北向资金": 1, "南下资金": 1, "机构": 1, "游资": 1, "散户": 1,
    "板块": 1, "概念股": 1, "蓝筹": 1, "白马股": 1,
    "股": 1, "涨": 1, "跌": 1,
}

FINANCE_KW = {
    # 宏观经济 (高权重)
    "GDP": 3, "CPI": 3, "PPI": 3, "PMI": 3, "通胀": 3, "通缩": 3,
    "加息": 3, "降息": 3, "降准": 3, "存款准备金": 3, "货币": 3,
    "央行": 3, "美联储": 3, "欧央行": 3, "日央行": 3,
    # 金融市场 (中权重)
    "债券": 2, "国债": 2, "企业债": 2, "可转债": 2, "基金": 2,
    "ETF": 2, "理财": 2, "信托": 2, "私募": 2, "资管": 2,
    "期货": 2, "期权": 2, "大宗商品": 2, "黄金": 2, "原油": 2,
    # 银行业务 (中权重)
    "银行": 2, "贷款": 2, "存款": 2, "房贷": 2, "按揭": 2,
    "利率": 2, "LPR": 2, "信贷": 2, "坏账": 2, "不良贷款": 2,
    "保险": 2, "保费": 2, "理赔": 2, "年金": 2,
    # 国际金融 (中权重)
    "汇率": 2, "人民币": 2, "美元": 2, "欧元": 2, "日元": 2,
    "离岸": 2, "在岸": 2, "外汇": 2, "跨境": 2, "结算": 2,
    "贸易": 2, "进口": 2, "出口": 2, "顺差": 2, "逆差": 2, "关税": 2,
    # 财政税收 (低权重)
    "预算": 1, "赤字": 1, "地方债": 1, "专项债": 1, "税收": 1,
    "减税": 1, "补贴": 1, "社保": 1, "养老": 1, "公积金": 1,
    "楼": 1, "房价": 1, "房地产": 1,
}

TECH_KW = {
    # AI/前沿科技 (高权重)
    "AI": 3, "人工智能": 3, "大模型": 3, "GPT": 3, "ChatGPT": 3,
    "OpenAI": 3, "DeepSeek": 3, "生成式": 3, "AGI": 3, "深度学习": 3,
    "机器学习": 3, "神经网络": 3, "算法": 2, "自动驾驶": 3,
    # 半导体/芯片 (高权重)
    "芯片": 3, "半导体": 3, "光刻机": 3, "晶圆": 3, "台积电": 3,
    "英伟达": 3, "NVIDIA": 3, "AMD": 3, "英特尔": 3, "高通": 3,
    "制程": 2, "封装": 2, "RISC-V": 3, "ARM": 2,
    # 科技公司 (中权重)
    "华为": 3, "苹果": 2, "小米": 2, "特斯拉": 2, "比亚迪": 2,
    "SpaceX": 2, "三星": 2, "谷歌": 2, "微软": 2, "Meta": 2,
    "字节跳动": 2, "腾讯": 2, "阿里": 2, "百度": 2,
    # 技术领域 (中权重)
    "5G": 2, "6G": 2, "量子计算": 3, "机器人": 2, "无人机": 2,
    "卫星": 2, "火箭": 2, "航天": 2, "新能源": 2, "电池": 2,
    "光伏": 2, "储能": 2, "电动": 2, "智能": 1,
    # 互联网/软件 (低权重)
    "互联网": 1, "软件": 1, "SaaS": 2, "云": 1, "开源": 2,
    "手机": 1, "电脑": 1, "应用": 1, "App": 1, "融资": 1,
    "创投": 1, "种子轮": 2, "投资": 1, "收购": 1,
}

POLITICS_KW = {
    # 中国政治 (高权重)
    "习近平": 3, "主席": 2, "总理": 3, "国务院": 3, "外交部": 3,
    "国防部": 3, "中央": 2, "两会": 3, "人大": 2, "政协": 2,
    "政治局": 3, "常委": 3, "部委": 2,
    # 军事安全 (高权重)
    "军队": 3, "国防": 3, "军事": 3, "海军": 3, "空军": 3,
    "火箭军": 3, "导弹": 3, "核武器": 3,
    # 地缘热点 (高权重)
    "台湾": 3, "香港": 3, "南海": 3, "钓鱼岛": 3, "新疆": 2, "西藏": 2,
    # 国际关系 (中权重)
    "中美": 3, "中欧": 3, "中日": 3, "中俄": 3, "中印": 3,
    "北约": 3, "欧盟": 3, "俄罗斯": 2, "乌克兰": 2, "巴以": 3,
    "中东": 2, "朝韩": 3, "伊朗": 2, "朝鲜": 2, "韩国": 1, "日本": 1,
    # 国际组织/法律 (中权重)
    "联合国": 2, "世卫": 2, "WTO": 2, "IMF": 2, "G20": 2,
    "制裁": 2, "法案": 2, "选举": 2, "总统": 2, "白宫": 2,
    "议会": 2, "国会": 2, "大选": 2, "脱欧": 2,
    # 国内治理 (低权重)
    "政策": 1, "法规": 1, "监管": 1, "反腐": 2, "巡视": 2,
    "执法": 1, "改革": 1, "试点": 1, "民生": 1,
}


def classify_by_keywords(title: str) -> str:
    t = title
    stock_score = sum(weight for kw, weight in STOCK_KW.items() if kw in t)
    finance_score = sum(weight for kw, weight in FINANCE_KW.items() if kw in t)
    tech_score = sum(weight for kw, weight in TECH_KW.items() if kw in t)
    politics_score = sum(weight for kw, weight in POLITICS_KW.items() if kw in t)

    scores = {"stock": stock_score, "finance": finance_score,
              "tech": tech_score, "politics": politics_score}
    best = max(scores, key=scores.get)
    return best if scores[best] >= 2 else "weird"


def _rss_fetch(url: str, source: str, category: str,
               limit: int = 10, base_score: float = 60.0) -> List[Article]:
    articles: List[Article] = []
    try:
        feed = feedparser.parse(url)
        for i, entry in enumerate(feed.entries[:limit]):
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            summary = entry.get("summary", "") or entry.get("description", "")
            if hasattr(summary, "encode"):
                from html import unescape
                clean = unescape(re.sub(r"<[^>]+>", "", summary)).strip()
            else:
                clean = ""
            if title:
                cat = classify_by_keywords(title) if category == "auto" else category
                articles.append(Article(
                    title=title, url=link, source=source,
                    category=cat, score=base_score - i, summary=clean[:120]
                ))
    except Exception:
        pass
    return articles


def _api_fetch(url: str, source: str, category: str,
               items_path: List[str], title_key: str, url_key: str,
               limit: int = 10, base_score: float = 65.0,
               url_prefix: str = "", summary_key: str = "") -> List[Article]:
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
            summary = item.get(summary_key, "") if summary_key else ""
            if isinstance(summary, str):
                summary = summary.strip()[:120]
            else:
                summary = ""
            if url_prefix:
                u = url_prefix + str(u)
            if title:
                cat = classify_by_keywords(title) if category == "auto" else category
                articles.append(Article(
                    title=title, url=u, source=source,
                    category=cat, score=base_score - i, summary=summary
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
        limit=10, base_score=68.0, summary_key="intro",
    )


def fetch_10jqka() -> List[Article]:
    return _api_fetch(
        "https://news.10jqka.com.cn/tapp/news/push/stock/?page=1&tag=",
        "同花顺", "auto",
        ["data", "list"], "title", "url",
        limit=15, base_score=72.0,
        url_prefix="https://news.10jqka.com.cn/tapp/news/push/stock/",
        summary_key="digest",
    )


def fetch_wallstreetcn() -> List[Article]:
    return _api_fetch(
        "https://api-one.wallstcn.com/apiv1/content/lives?channel=global-channel&limit=10",
        "华尔街见闻", "finance",
        ["data", "items"], "title", "id",
        limit=10, base_score=66.0,
        url_prefix="https://wallstreetcn.com/livenews/",
        summary_key="content_text",
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
            summary = item.get("desc", "").strip()[:120] if isinstance(item.get("desc", ""), str) else ""
            if title:
                cat = classify_by_keywords(title)
                articles.append(Article(
                    title=title, url=u, source="百度热搜",
                    category=cat, score=65.0 - i, summary=summary
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
            summary = item.get("HotDesc", "") or item.get("Abstract", "") or ""
            if isinstance(summary, str):
                summary = summary.strip()[:120]
            if title:
                cat = classify_by_keywords(title)
                articles.append(Article(
                    title=title, url=u, source="今日头条",
                    category=cat, score=63.0 - i, summary=summary
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
