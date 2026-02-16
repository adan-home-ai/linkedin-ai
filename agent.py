import feedparser
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

# --- CONFIGURATION ---
# Industry specific feed
RSS_FEED_URL = "http://feeds.feedburner.com/TechCrunch/" 
SENSITIVE_KEYWORDS = ["politics", "election", "war", "crime", "death", "racism", "trump", "biden"]

# Email Config (We will load these from "Secrets" later for safety)
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') # This must be a Google App Password
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

def is_safe_content(text):
    text_lower = text.lower()
    for word in SENSITIVE_KEYWORDS:
        if word in text_lower:
            return False
    return True

def get_safe_trend():
    feed = feedparser.parse(RSS_FEED_URL)
    for entry in feed.entries:
        if is_safe_content(entry.title) and is_safe_content(entry.description):
            return entry
    return None

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def run_agent():
    article = get_safe_trend()
    
    if article:
        # Generate the Draft (Simulated AI)
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
