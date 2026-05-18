"""
每日AI日报 - 数据采集脚本（增强版）
数据来源: HN + GitHub Trending + ArXiv + 国外科技媒体 RSS
"""

import json
import os
import sys
import re
import urllib.request
import urllib.error
from datetime import datetime, date
from html.parser import HTMLParser
from xml.parsers.expat import ParserCreate

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "public")
os.makedirs(DATA_DIR, exist_ok=True)
TODAY = date.today()

# ===== 配置 =====

AI_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "openai", "anthropic",
    "deepseek", "gemini", "mistral", "copilot", "cursor", "codex",
    "coding", "programming", "agent", "mcp", "function calling",
    "embodied", "robot", "humanoid",
    "transformer", "diffusion", "reasoning", "agentic",
]

CATEGORY_MAP = {
    "ai_coding": ["coding", "cursor", "copilot", "codex", "programming", "code",
                  "claude code", "agent", "mcp", "dev tools",
                  "vibe coding", "ide", "compiler", "swe"],
    "embodied_ai": ["robot", "humanoid", "embodied", "robotics",
                    "boston dynamics", "figure ai", "optimu"],
}

# RSS 新闻源
RSS_FEEDS = [
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "name": "TechCrunch"},
    {"url": "https://arstechnica.com/ai/feed/", "name": "Ars Technica"},
    {"url": "https://www.theverge.com/ai-artificial-intelligence/rss.xml", "name": "The Verge"},
    {"url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "name": "MIT Tech Review"},
    {"url": "https://blog.google/technology/ai/rss/", "name": "Google AI"},
]

# 这些源的 RSS 已按 AI 分类，无需关键词过滤
RSS_NO_FILTER = {"TechCrunch", "Ars Technica", "The Verge", "MIT Tech Review", "Google AI"}


# ===== 工具函数 =====

def fetch(url, max_bytes=0):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
            if max_bytes:
                data = data[:max_bytes]
            return data.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"    请求失败: {url[:60]}: {e}")
        return None


def fetch_json(url):
    d = fetch(url)
    return json.loads(d) if d else None


def extract_og_desc(html):
    m = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html, re.I)
    if m: return m.group(1)[:300]
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.I)
    if m: return m.group(1)[:300]
    return ""


def classify(title_lower):
    cats = []
    for cat, kws in CATEGORY_MAP.items():
        if any(kw in title_lower for kw in kws):
            cats.append(cat)
    return cats or ["general_ai"]


def make_reason(title_lower, cats, source):
    if "ai_coding" in cats:
        base = "AI Coding 领域重要动态"
    elif "embodied_ai" in cats:
        base = "具身智能领域重要进展"
    else:
        base = "AI 领域重要动态"

    if "claude" in title_lower or "anthropic" in title_lower:
        base += "，Claude 生态持续扩展"
    elif "openai" in title_lower or "gpt" in title_lower:
        base += "，反映头部玩家最新动作"
    elif "deepseek" in title_lower:
        base += "，开源模型竞争加剧"
    elif "robot" in title_lower or "humanoid" in title_lower or "embodied" in title_lower:
        base += "，具身智能商业化加速"
    elif "agent" in title_lower or "mcp" in title_lower:
        base += "，AI Agent 工程化趋势明显"
    elif source in RSS_NO_FILTER:
        base += "，来自一线科技媒体的深度报道"
    else:
        base += "，值得关注其后续影响"
    return base + "。"


# ===== 数据源 1: RSS 科技新闻 =====

class RSSParser:
    """简易 RSS/Atom 解析器"""
    def __init__(self):
        self.entries = []
        self._tag_stack = []
        self._current = {}
        self._text = ""
        self._in_entry = False
        self._entry_tags = {"item", "entry"}

    def start_element(self, name, attrs):
        self._tag_stack.append(name)
        self._text = ""
        if name in self._entry_tags:
            self._in_entry = True
            self._current = {}

    def end_element(self, name):
        if name in self._entry_tags and self._in_entry:
            if self._current.get("title"):
                self.entries.append(self._current)
            self._in_entry = False
        if self._in_entry:
            text = self._text.strip()
            if name == "title":
                self._current["title"] = text
            elif name == "link" and "url" not in self._current:
                self._current["url"] = text
            elif name == "description" or name == "summary":
                self._current["summary"] = re.sub(r'<[^>]+>', '', text).strip()[:400]
            elif name == "published" or name == "updated" or name == "pubDate":
                self._current["pub_date"] = text
        self._tag_stack.pop()
        self._text = ""

    def char_data(self, data):
        self._text += data

    def parse(self, xml_str):
        p = ParserCreate()
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        try:
            p.Parse(xml_str, True)
        except Exception:
            pass
        return self.entries


def fetch_rss_news():
    """从多家国外科技媒体 RSS 获取 AI 新闻"""
    all_entries = []
    for feed in RSS_FEEDS:
        print(f"  [RSS] {feed['name']}...", end=" ")
        xml = fetch(feed["url"])
        if not xml:
            print("失败")
            continue
        parser = RSSParser()
        entries = parser.parse(xml)
        print(f"{len(entries)} 条")

        need_filter = feed["name"] not in RSS_NO_FILTER
        count = 0
        for e in entries:
            title = e.get("title", "")
            title_lower = title.lower()
            summary = e.get("summary", "")
            url = e.get("url", "")

            # 需要关键词过滤的源
            if need_filter:
                matched = [kw for kw in AI_KEYWORDS if kw in title_lower]
                if not matched:
                    continue

            categories = classify(title_lower)

            # 摘要为空时尝试抓取 OG 描述
            if not summary and url:
                html = fetch(url, max_bytes=8192)
                if html:
                    summary = extract_og_desc(html)

            all_entries.append({
                "title": title,
                "url": url,
                "summary": summary[:300],
                "categories": categories,
                "source": feed["name"],
            })
            count += 1
            if count >= 3:
                break
    return all_entries


# ===== 数据源 2: Hacker News =====

def fetch_hn_news():
    print("  [HN] 获取热门故事...")
    ids = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not ids: return []

    stories = []
    for sid in ids[:120]:
        story = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if not story or story.get("type") != "story":
            continue
        title = (story.get("title") or "").lower()
        matched = [kw for kw in AI_KEYWORDS if kw in title]
        if not matched:
            continue

        categories = classify(title)
        external_url = story.get("url") or ""
        hn_url = f"https://news.ycombinator.com/item?id={sid}"

        summary = ""
        story_text = story.get("text") or ""
        if story_text:
            summary = re.sub(r'<[^>]+>', '', story_text).strip()[:300]
        elif external_url:
            html = fetch(external_url, max_bytes=8192)
            summary = extract_og_desc(html) if html else ""

        stories.append({
            "title": story.get("title", ""),
            "url": external_url or hn_url,
            "hn_url": hn_url if external_url else "",
            "summary": summary,
            "score": story.get("score", 0),
            "comments": story.get("descendants", 0),
            "categories": categories,
            "source": "Hacker News",
        })
        if len(stories) >= 5:
            break
    return stories


# ===== 数据源 3: GitHub Trending =====

class GHParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.repos = []
        self._article = False
        self._h2 = False
        self._desc = False
        self._cur = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "article": self._article = True; self._cur = {}
        if self._article and tag == "h2": self._h2 = True
        if self._article and tag == "a" and a.get("href","").startswith("/"):
            p = a["href"]
            if p.count("/") == 2: self._cur["url"] = "https://github.com" + p
        if self._article and tag == "p" and "col-9" in a.get("class",""):
            self._desc = True
    def handle_endtag(self, tag):
        if tag == "article" and self._article:
            if self._cur.get("name"): self.repos.append(self._cur)
            self._article = False
        if tag == "h2": self._h2 = False
        if tag == "p": self._desc = False
    def handle_data(self, data):
        if self._h2:
            n = data.strip()
            if n: self._cur["name"] = n
        if self._desc:
            d = data.strip()
            if d and "description" not in self._cur: self._cur["description"] = d[:300]


def fetch_github_trending():
    print("  [GitHub] 获取 Trending...")
    html = fetch("https://github.com/trending?since=daily")
    if not html: return []
    parser = GHParser()
    parser.feed(html)
    repos = []
    for repo in parser.repos[:10]:
        full = repo.get("url","").replace("https://github.com/","")
        name = repo.get("name","")
        desc = repo.get("description","")
        matched = [kw for kw in AI_KEYWORDS if kw in name.lower() or kw in full.lower() or kw in desc.lower()]
        if not matched: continue
        cats = ["ai_coding"] if any(kw in name.lower()+full.lower()+desc.lower() for kw in
                ["agent","coding","code","llm","mcp","framework","compiler","swe"]) else ["general_ai"]
        repos.append({
            "title": name,
            "url": repo.get("url",""),
            "summary": desc[:300],
            "categories": cats,
            "source": "GitHub Trending",
        })
        if len(repos) >= 3: break
    return repos


# ===== 数据源 4: ArXiv =====

def fetch_arxiv():
    print("  [ArXiv] 获取最新论文...")
    q = "cat:cs.AI+OR+cat:cs.RO+OR+cat:cs.SE"
    xml = fetch(f"http://export.arxiv.org/api/query?search_query={q}&sortBy=submittedDate&sortOrder=descending&max_results=10")
    if not xml: return []
    papers = []
    entries = re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL)
    for entry in entries:
        tm = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
        sm = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
        im = re.search(r'<id>(.*?)</id>', entry)
        if not tm: continue
        title = tm.group(1).strip().replace('\n',' ').replace('  ',' ')
        tlower = title.lower()
        matched = [kw for kw in AI_KEYWORDS if kw in tlower]
        if not matched: continue
        cats = []
        if any(kw in tlower for kw in ["code","programming","llm","agent","mcp"]):
            cats.append("ai_coding")
        elif any(kw in tlower for kw in ["robot","embodied","manipulation"]):
            cats.append("embodied_ai")
        else:
            cats.append("general_ai")
        papers.append({
            "title": title,
            "url": im.group(1).strip() if im else "",
            "summary": (sm.group(1).strip()[:300] if sm else "").replace('\n',' '),
            "categories": cats,
            "source": "ArXiv",
        })
        if len(papers) >= 2: break
    return papers


# ===== 主流程 =====

def build():
    print(f"=== 每日AI日报生成 === {TODAY}")
    all_items = []

    # 1. RSS 新闻（优先）
    rss = fetch_rss_news()
    print(f"  RSS 总计: {len(rss)} 条\n")
    all_items.extend(rss)

    # 2. Hacker News
    hn = fetch_hn_news()
    print(f"  HN 总计: {len(hn)} 条\n")
    all_items.extend(hn)

    # 3. GitHub Trending
    gh = fetch_github_trending()
    print(f"  GitHub 总计: {len(gh)} 条\n")
    all_items.extend(gh)

    # 4. ArXiv
    arxiv = fetch_arxiv()
    print(f"  ArXiv 总计: {len(arxiv)} 条\n")
    all_items.extend(arxiv)

    # 去重 + 排序
    seen = set()
    deduped = []
    for item in all_items:
        key = item["title"].lower().strip()[:60]
        if key in seen:
            continue
        seen.add(key)
        item["reason"] = make_reason(item["title"].lower(), item["categories"], item["source"])
        deduped.append(item)

    # 排序: RSS > HN(按分) > ArXiv > GitHub
    rss_items = [i for i in deduped if i["source"] in RSS_NO_FILTER]
    hn_items = sorted([i for i in deduped if i["source"] == "Hacker News"],
                      key=lambda x: x.get("score",0), reverse=True)
    arxiv_items = [i for i in deduped if i["source"] == "ArXiv"]
    gh_items = [i for i in deduped if i["source"] == "GitHub Trending"]

    result = []
    taken = set()
    # 尽量每个来源选 1 条，保证多样性
    for pool in [rss_items, hn_items, arxiv_items, gh_items]:
        for item in pool:
            if len(result) >= 5: break
            key = item["title"][:40]
            if key not in taken:
                result.append(item)
                taken.add(key)
        if len(result) >= 5: break
    # 如果不足 5 条，继续补充
    for pool in [hn_items, rss_items, arxiv_items, gh_items]:
        for item in pool:
            if len(result) >= 5: break
            key = item["title"][:40]
            if key not in taken:
                result.append(item)
                taken.add(key)

    return {
        "date": str(TODAY),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(result),
        "items": result[:5],
    }


def main():
    data = build()
    path = os.path.join(DATA_DIR, "briefing.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"保存: {path}")
    print(f"共 {data['total']} 条")
    for i, item in enumerate(data["items"], 1):
        print(f"  {i}. [{item['source']}] {item['title'][:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
