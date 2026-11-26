import json
import urllib.request
import xml.etree.ElementTree as ET
import re

# مصادر RSS الرسمية والموثوقة
RSS_SOURCES = [
    {"url": "https://gate.ahram.org.eg/RSS.aspx", "region": "مصر", "source": "بوابة الأهرام"},
    {"url": "https://www.youm7.com/rss/SectionRss?SectionID=65", "region": "مصر", "source": "اليوم السابع"},
    {"url": "https://feeds.bbci.co.uk/arabic/rss.xml", "region": "العالم", "source": "بي بي سي عربي"}
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    clean_text = re.sub(r'<.*?>', '', raw_html)
    return " ".join(clean_text.split()).strip()

def fetch_rss(feed_info, limit=4):
    items = []
    try:
        req = urllib.request.Request(
            feed_info["url"],
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        for item in root.findall('.//item')[:limit]:
            title = clean_html(item.findtext('title'))
            desc = clean_html(item.findtext('description'))
            if not desc:
                desc = title
            if len(desc) > 220:
                desc = desc[:217] + "..."
            if title:
                items.append({
                    "region": feed_info["region"],
                    "title": title,
                    "summary": desc,
                    "source": f"{feed_info['source']} (تحديث تلقائي)"
                })
    except Exception as e:
        print(f"تعذر الجلب من {feed_info['source']}: {e}")
    return items

def main():
    # 1. الاحتفاظ بأخبار القليوبية وشبين القناطر المحلية الموجودة حالياً في news.json
    local_news = []
    try:
        with open("news.json", "r", encoding="utf-8") as f:
            current_data = json.load(f)
            local_news = [
                item for item in current_data
                if item.get("region") in ["القليوبية", "شبين القناطر"]
            ]
    except Exception:
        pass

    # 2. جلب الأخبار الجديدة تلقائياً لمصر والعالم
    auto_news = []
    for src in RSS_SOURCES:
        auto_news.extend(fetch_rss(src, limit=4))

    # 3. دمج الأخبار المحلية مع التلقائية وحفظها في news.json
    final_news = local_news + auto_news
    if final_news:
        with open("news.json", "w", encoding="utf-8") as f:
            json.dump(final_news, f, ensure_ascii=False, indent=2)
        print(f"تم تحديث {len(final_news)} خبراً بنجاح.")

if __name__ == "__main__":
    main()