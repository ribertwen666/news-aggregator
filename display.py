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
    line = f"{BOLD}{num}.{RESET} {color}{tag}{RESET} {article.title}  \033[90m({article.source})\033[0m"
    if article.summary:
        line += f"\n     \033[37m{article.summary}\033[0m"
    return line


def display(articles: List[Article], category: str = "all"):
    if category != "all":
        articles = [a for a in articles if a.category == category]

    print(f"\n{BOLD}今日要闻 TOP {len(articles)}{RESET}\n")
    for i, a in enumerate(articles):
        print(format_article(a, i))
    print()


def export_html(articles: List[Article], filepath: str, category: str = "all"):
    if category != "all":
        articles = [a for a in articles if a.category == category]

    rows = []
    for i, a in enumerate(articles):
        label = CATEGORY_LABELS.get(a.category, a.category)
        color_map = {"stock": "#d94f4f", "finance": "#4f8ad9", "tech": "#4fa64f",
                     "politics": "#d9b84f", "weird": "#a64fd9"}
        color = color_map.get(a.category, "#888")
        rows.append(
            f'    <tr>'
            f'<td class="num">{i + 1}</td>'
            f'<td><span class="tag" style="background:{color}">{label}</span></td>'
            f'<td><a href="{a.url}" target="_blank">{a.title}</a>'
            + (f'<div class="summary">{a.summary}</div>' if a.summary else '') +
            f'</td>'
            f'<td class="source">{a.source}</td>'
            f'</tr>'
        )

    from datetime import date
    today = date.today().strftime("%Y-%m-%d")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>今日要闻 TOP {len(articles)} — {today}</title>
<style>
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         max-width: 900px; margin: 40px auto; padding: 0 20px;
         background: #f8f9fa; color: #222; }}
  h1 {{ font-size: 24px; border-bottom: 3px solid #333; padding-bottom: 12px; }}
  .date {{ color: #888; font-size: 14px; margin-bottom: 24px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #e0e0e0; vertical-align: middle; }}
  .num {{ width: 30px; font-weight: bold; color: #999; text-align: right; }}
  .tag {{ display: inline-block; width: 44px; text-align: center; color: #fff;
          font-size: 12px; border-radius: 4px; padding: 2px 6px; }}
  a {{ color: #1a56db; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .source {{ color: #999; font-size: 13px; white-space: nowrap; text-align: right; }}
  tr:hover {{ background: #fff; }}
  .summary {{ color: #666; font-size: 13px; margin-top: 4px; line-height: 1.5; }}
</style>
</head>
<body>
<h1>今日要闻 TOP {len(articles)}</h1>
<p class="date">{today}</p>
<table>
{"".join(rows)}
</table>
<p class="date" style="margin-top:24px">每天 8:00 自动更新</p>
</body>
</html>"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
