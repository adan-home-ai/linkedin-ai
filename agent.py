import requests
import smtplib
from email.mime.text import MIMEText
import os
import sys
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# 1. SEARCH QUERY: We use "OR" to cast a wide net for exciting topics
SEARCH_TOPIC = "AI OR 'new technology' OR innovation OR 'future of work' OR startup"

# 2. PAYWALL BLOCKLIST: Skip these domains (they usually require a sub)
BLOCKED_DOMAINS = [
    "wsj.com", "nytimes.com", "bloomberg.com", "ft.com", "hbr.org", 
    "economist.com", "washingtonpost.com", "businessinsider.com", "theinformation.com"
]

# 3. SAFETY FILTER: Skip these words
SENSITIVE_KEYWORDS = ["politics", "election", "war", "crime", "death", "racism", "trump", "biden", "murder"]

# --- CREDENTIALS ---
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

# PRE-FLIGHT CHECK
if not NEWS_API_KEY:
    print("❌ ERROR: NEWS_API_KEY is missing in GitHub Secrets.")
    sys.exit(1)

def is_safe_and_free(article):
    title = article.get('title', '')
    desc = article.get('description', '') or ''
    source_name = article.get('source', {}).get('name', '').lower()
    url = article.get('url', '').lower()
    
    # Combined text for checking
    full_text = (title + " " + desc).lower()

    # 1. Check for Paywalls
    for domain in BLOCKED_DOMAINS:
        if domain in url:
            print(f"Skipping paywalled source: {source_name}")
            return False

    # 2. Check for Sensitive/Political Content
    for word in SENSITIVE_KEYWORDS:
        if word in full_text:
            print(f"Skipping sensitive topic: {title[:30]}...")
            return False

    return True

def get_viral_article():
    print("Searching for viral news...")
    
    # Calculate date for "Past 24 Hours"
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': SEARCH_TOPIC,
        'from': yesterday,
        'sortBy': 'popularity', # <--- THIS finds the viral stuff
        'language': 'en',
        'apiKey': NEWS_API_KEY,
        'pageSize': 20 # Fetch top 20 to filter through
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') != 'ok':
            print(f"API Error: {data.get('message')}")
            return None
            
        articles = data.get('articles', [])
        print(f"API returned {len(articles)} articles. Filtering...")
        
        for article in articles:
            if is_safe_and_free(article):
                return article
                
    except Exception as e:
        print(f"Error fetching news: {e}")
        
    return None

def send_email(subject, body):
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print(f"✅ Success! Draft sent to {RECEIVER_EMAIL}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def run_agent():
    article = get_viral_article()
    
    if article:
        print(f"🔥 FOUND VIRAL HIT: {article['title']}")
        draft = f"""
TOPIC: {article['title']}
SOURCE: {article['source']['name']}
LINK: {article['url']}

--- DRAFT POST ---
🚀 {article['title']}

I just saw this trending and had to share. It's rare to see something move this fast.

{article['description']}

What's your take? Is this overhyped or the real deal?

#Innovation #TechTrends #Future
"""
        send_email(f"🔥 Viral Post Draft: {article['title']}", draft)
    else:
        print("No suitable viral articles found today.")

if __name__ == "__main__":
    run_agent()
