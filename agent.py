import feedparser
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
import sys

# --- CONFIGURATION ---
RSS_FEED_URL = "http://feeds.feedburner.com/TechCrunch/" 
SENSITIVE_KEYWORDS = ["politics", "election", "war", "crime", "death", "racism", "trump", "biden"]

# --- CREDENTIALS CHECK ---
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

# Stop the script immediately if secrets are missing to prevent confusing errors
if not SENDER_EMAIL or not SENDER_PASSWORD:
    print("ERROR: SENDER_EMAIL or SENDER_PASSWORD is missing.")
    print("Please check GitHub Settings > Secrets > Actions.")
    sys.exit(1)

def is_safe_content(text):
    if not text: return True
    text_lower = text.lower()
    for word in SENSITIVE_KEYWORDS:
        if word in text_lower:
            return False
    return True

def get_safe_trend():
    print("Scanning feed...")
    try:
        feed = feedparser.parse(RSS_FEED_URL)
        if not feed.entries:
            print("Feed parsed but no entries found.")
            return None
            
        for entry in feed.entries:
            if is_safe_content(entry.title) and is_safe_content(entry.description):
                return entry
    except Exception as e:
        print(f"Error parsing feed: {e}")
    return None

def send_email(subject, body):
    # FIX: Explicitly use 'utf-8' to handle emojis like 🚀
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        # Connect to Gmail (Port 465 for SSL)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print(f"Success! Email sent to {RECEIVER_EMAIL}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def run_agent():
    article = get_safe_trend()
    
    if article:
        print(f"Found trend: {article.title}")
        draft = f"""
TOPIC: {article.title}
LINK: {article.link}

--- DRAFT ---
🚀 {article.title}

This is a massive shift for the industry. I've been tracking this trend...

(Paste this into your scheduler!)
"""
        send_email(f"Daily LinkedIn Draft: {article.title}", draft)
    else:
        print("No safe trends found today.")

if __name__ == "__main__":
    run_agent()
