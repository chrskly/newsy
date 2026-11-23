#!/usr/bin/env python3

import datetime
from datetime import timedelta, timezone
import feedparser
from newspaper import Article
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import simpleSplit

# Margins in points (15mm ≈ 42.52pt)
TOP_MARGIN = 42.52
BOTTOM_MARGIN = 42.52
LEFT_MARGIN = 42.52
RIGHT_MARGIN = 42.52
FONT_SIZE_TITLE = 16
FONT_SIZE_SOURCE = 12
FONT_SIZE_BODY = 10
ARTICLE_DAYS = 1

FEEDS = [
    [ "TheJournal", "https://thejournal.ie/feed/" ],
    [ "TheGuardian", "https://www.theguardian.com/world/rss" ],
    [ "RTE", "https://rte.ie/feeds/rss/?index=/news/" ],
    [ "Hackaday", "https://hackaday.com/feed/" ],
    [ "Pluralistic", "https://pluralistic.net/feed/" ],
]

ARTICLES = []

def ensure_aware_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def fetch_article(url):
    article = Article(url)
    article.download()
    article.parse()
    a = { 'title': article.title, 'publish_date': article.publish_date, 'text': article.text }
    #print(article.__dir__())
    return a

def fetch_feed(feed_url, feed_name=None):
    print(f"Processing feed: {feed_name} : {feed_url}")
    d = feedparser.parse(feed_url)
    for entry in d.entries:
        url = entry.link
        article_data = fetch_article(url)
        if feed_name:
            article_data['feed_name'] = feed_name
        print("  Article fetched:", article_data['title'])
        ARTICLES.append(article_data)

def get_sorted_articles():
    now = datetime.datetime.now(timezone.utc)
    recent_articles = []
    for article in ARTICLES:
        pub_date = ensure_aware_utc(article['publish_date'])
        if pub_date and pub_date > now - timedelta(days=ARTICLE_DAYS):
            recent_articles.append(article)
    recent_articles.sort(key=lambda x: ensure_aware_utc(x['publish_date']), reverse=True)
    return recent_articles

def write_article_to_pdf(canvas, article):
    # Write Title text
    canvas.setFont("Helvetica-Bold", FONT_SIZE_TITLE)
    page_width, page_height = canvas._pagesize
    max_width = page_width - LEFT_MARGIN - RIGHT_MARGIN
    x = LEFT_MARGIN
    y = page_height - TOP_MARGIN
    wrapped_title = simpleSplit(article['title'], 'Helvetica-Bold', FONT_SIZE_TITLE, max_width)
    for line in wrapped_title:
        canvas.drawString(x, y, line)
        y -= 20  # line spacing

    # Write Feed name
    canvas.setFont("Helvetica-Oblique", FONT_SIZE_SOURCE)
    canvas.drawString(x, y, f"{article['feed_name']}")
    y -= 20

    # Write Publish Date
    pub_date = ensure_aware_utc(article['publish_date'])
    if pub_date:
        pub_date_str = pub_date.strftime("%Y-%m-%d %H:%M %Z")
        canvas.drawString(x, y, f"{pub_date_str}")
        y -= 20

    # Set up for body text
    canvas.setFont("Helvetica", FONT_SIZE_BODY)
    body_lines = []
    for paragraph in article['text'].split('\n'):
        if paragraph.strip():
            wrapped = simpleSplit(paragraph, 'Helvetica', FONT_SIZE_BODY, max_width)
            body_lines.extend(wrapped)
        else:
            body_lines.append("")

    # Write body lines, start new page if needed
    y -= 10  # small gap after title
    line_height = 15
    for line in body_lines:
        if line == "Advertisement":
            continue  # skip advertisement lines
        line = line.strip()
        if y < BOTTOM_MARGIN:
            canvas.showPage()
            y = page_height - TOP_MARGIN
            canvas.setFont("Helvetica", FONT_SIZE_BODY)
        canvas.drawString(x, y, line)
        y -= line_height
    canvas.showPage()




print("Starting ...")
# datestamp
datestamp = datetime.datetime.now().strftime("%Y-%m-%d")
pdf_file = f"{datestamp}-articles.pdf"
canvas = Canvas(pdf_file)

for feed in FEEDS:
    fetch_feed(feed[1], feed_name=feed[0])

for article in get_sorted_articles():
    print(f"Writing article: {article['title'], article['feed_name']}")
    write_article_to_pdf(canvas, article)

canvas.save()
