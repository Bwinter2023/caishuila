"""
财税法资讯站 - 每日新闻聚合脚本
每天自动抓取 RSS 源，按关键词过滤财税相关新闻，更新 daily_news.js
运行环境：GitHub Actions（Ubuntu），Python 3 标准库，0 外部依赖
"""
import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import hashlib
import re

# === 配置 ===
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'daily_news.js')

# 财税关键词过滤器（标题或摘要包含以下任一关键词即收录）
KEYWORDS = [
    # 税类
    '增值税', '企业所得税', '个人所得税', '印花税', '消费税',
    '房产税', '土地增值税', '关税', '附加税', '城建税',
    # 行为
    '补税', '退税', '稽查', '偷税', '漏税', '逃税', '虚开',
    '纳税申报', '汇算清缴', '税务处罚', '税务检查', '税务登记',
    '税收优惠', '税前扣除', '滞纳金', '进项', '销项', '抵扣',
    # 政策
    '税务总局', '税务局', '税收征管', '税法', '财税',
    '新政', '政策解读', '法规',
    # 公司涉税
    '上市公司', '公告', '披露', '审计', '年报',
    # 法律
    '公司法', '合同法', '民法典', '司法解释',
    '行政处罚', '刑事责任', '量刑', '裁定', '判决',
    '破产', '清算', '股权',
]

# RSS 源列表
RSS_FEEDS = [
    # 中文财税新闻
    ('https://feedx.net/rss/36kr.xml', '36氪'),
    ('https://feedx.net/rss/sspai.xml', '少数派'),
    # ABC News Business (国际)
    ('https://abcnews.go.com/abcnews/businessheadlines', 'ABC Business'),
    # 备用源
    ('https://rss.nytimes.com/services/xml/rss/nyt/Business.xml', 'NYT Business'),
]

MAX_NEWS = 100  # 保留最多新闻条数
HTTP_TIMEOUT = 15  # 请求超时秒数


def fetch_rss(url, source_name):
    """抓取并解析 RSS feed"""
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=HTTP_TIMEOUT)
        data = resp.read()
    except Exception as e:
        print('  [WARN] %s: HTTP error %s' % (source_name, e))
        return []

    articles = []
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        print('  [WARN] %s: Parse error %s' % (source_name, e))
        return []

    # RSS 2.0 格式: rss/channel/item
    # Atom 格式: feed/entry
    ns = {'atom': 'http://www.w3.org/2005/Atom',
          'content': 'http://purl.org/rss/1.0/modules/content/'}

    for item in root.iter('item'):
        title = item.findtext('title', '')
        link = item.findtext('link', '')
        desc = item.findtext('description', '')
        pubdate = item.findtext('pubDate', '')
        articles.append({
            'title': title.strip(),
            'link': link.strip(),
            'summary': re.sub(r'<[^>]+>', '', desc).strip(),
            'pubdate': pubdate.strip(),
            'source': source_name,
        })

    for entry in root.iter('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title')
        link_el = entry.find('{http://www.w3.org/2005/Atom}link')
        summary = entry.find('{http://www.w3.org/2005/Atom}summary')
        published = entry.find('{http://www.w3.org/2005/Atom}published')
        articles.append({
            'title': title.text.strip() if title is not None and title.text else '',
            'link': link_el.get('href', '') if link_el is not None else '',
            'summary': re.sub(r'<[^>]+>', '', summary.text).strip() if summary is not None and summary.text else '',
            'pubdate': published.text.strip() if published is not None and published.text else '',
            'source': source_name,
        })

    print('  [OK] %s: %d articles' % (source_name, len(articles)))
    return articles


def filter_relevant(articles):
    """按关键词过滤财税相关文章"""
    matched = []
    for a in articles:
        text = a['title'] + ' ' + a['summary']
        for kw in KEYWORDS:
            if kw in text:
                matched.append(a)
                break
    print('  => %d relevant after keyword filter' % len(matched))
    return matched


def parse_date(pubdate):
    """尝试解析 RSS 日期格式，返回 YYYY-MM-DD"""
    if not pubdate:
        return ''
    # Mon, 01 Jun 2026 12:00:00 GMT
    months = {
        'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'
    }
    m = re.match(r'\w+,\s+(\d+)\s+(\w+)\s+(\d+)', pubdate)
    if m:
        d, mon, y = m.groups()
        return '%s-%s-%s' % (y, months.get(mon, '01'), d.zfill(2))
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', pubdate)
    if m:
        return m.group(0)
    return ''


def generate_id(title, link):
    """生成唯一 ID"""
    raw = (title + link).encode('utf-8')
    return hashlib.md5(raw).hexdigest()[:10]


def load_existing():
    """加载已有 daily_news.js"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    # 提取 JSON 数组
    m = re.search(r'\[[\s\S]*\]', content)
    if m:
        try:
            return json.loads(m.group(0))
        except:
            return []
    return []


def save_news(news_list):
    """保存到 daily_news.js"""
    data = json.dumps(news_list, ensure_ascii=False, indent=2)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write('const dailyNews = ')
        f.write(data)
        f.write(';\n')
    print('Saved %d news items to daily_news.js' % len(news_list))


def main():
    print('=== Fetching daily finance/tax/law news ===')
    print()

    all_articles = []
    for url, name in RSS_FEEDS:
        print('Fetching %s...' % name)
        try:
            articles = fetch_rss(url, name)
            relevant = filter_relevant(articles)
            all_articles.extend(relevant)
        except Exception as e:
            print('  [ERROR] %s: %s' % (name, e))

    print()
    print('Total relevant articles: %d' % len(all_articles))

    # 去重 + 格式化
    existing = load_existing()
    existing_ids = {a['id'] for a in existing}

    new_items = []
    for a in all_articles:
        aid = generate_id(a['title'], a['link'])
        if aid in existing_ids:
            continue
        if not a['title'] or not a['link']:
            continue
        new_items.append({
            'id': aid,
            'title': a['title'],
            'source': a['source'],
            'date': parse_date(a['pubdate']),
            'url': a['link'],
            'summary': a['summary'][:200],
        })
        existing_ids.add(aid)

    print('New items to add: %d' % len(new_items))

    # 合并：新文章在最前
    merged = new_items + existing
    merged = merged[:MAX_NEWS]

    if len(merged) != len(existing):
        save_news(merged)
        print('Update: %d -> %d items, +%d new' % (len(existing), len(merged), len(new_items)))
    else:
        print('No new items. File unchanged.')
    print('Done.')


if __name__ == '__main__':
    main()
