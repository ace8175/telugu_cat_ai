import feedparser
import requests
from datetime import datetime, timedelta
import streamlit as st
import json
import re
from bs4 import BeautifulSoup

class NewsService:
    def __init__(self):
        self.rss_feeds = [
            {
                "url": "https://feeds.feedburner.com/eenadutelangananews",
                "name": "Eenadu Telangana"
            },
            {
                "url": "https://www.sakshi.com/rss/telangana", 
                "name": "Sakshi"
            },
            {
                "url": "https://www.andhrajyothy.com/rss/telangana-news",
                "name": "Andhra Jyothy"
            },
            {
                "url": "https://feeds.feedburner.com/tv9telugulatestnews",
                "name": "TV9 Telugu"
            }
        ]
        
        # Backup news in case RSS fails
        self.backup_news = [
            {
                'id': 1,
                'title': 'తెలంగాణ రాష్ట్ర వార్తలు - రాజకీయ పరిణామాలు',
                'summary': 'తెలంగాణ రాష్ట్రంలో నేటి రాజకీయ పరిణామాలు మరియు ప్రభుత్వ విధానాల గురించిన తాజా సమాచారం. ముఖ్యమంత్రి కేసీఆర్ ఇవాళ ముఖ్యమైన ప్రకటనలు చేశారు.',
                'source': 'తెలుగు న్యూస్',
                'published': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'link': 'https://example.com/news1'
            },
            {
                'id': 2,
                'title': 'హైదరాబాద్ మెట్రో రైలు సేవలు - కొత్త మార్గాలు',
                'summary': 'హైదరాబాద్ మెట్రో రైలు కొత్త మార్గాలు ప్రారంభం. ప్రజలకు మరింత సౌకర్యవంతమైన ప్రయాణం కలుగుతుంది. టికెట్ ధరలు మరియు సమయ పట్టిక వివరాలు.',
                'source': 'మెట్రో న్యూస్',
                'published': (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
                'link': 'https://example.com/news2'
            },
            {
                'id': 3,
                'title': 'వాతావరణ సమాచారం - వర్షాలకు అవకాశం',
                'summary': 'తెలంగాణ రాష్ట్రంలో రాబోయే రెండు రోజుల పాటు వర్షాలకు అవకాశం ఉందని వాతావరణ శాఖ తెలిపింది. రైతులు అవసరమైన జాగ్రత్తలు తీసుకోవాలని సూచించారు.',
                'source': 'వాతావరణ విభాగం',
                'published': (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
                'link': 'https://example.com/news3'
            },
            {
                'id': 4,
                'title': 'ఐటి సెక్టార్ వృద్ధి - కొత్త ఉద్యోగావకాశాలు',
                'summary': 'హైదరాబాద్‌లో ఐటి సంస్థలు విస్తరణ. కొత్త ఉద్యోగావకాశాలు సృష్టి అవుతున్నాయి. సైబరాబాద్‌లో కొత్త కంపెనీలు స్థాపన.',
                'source': 'టెక్ న్యూస్',
                'published': (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
                'link': 'https://example.com/news4'
            },
            {
                'id': 5,
                'title': 'విద్యా రంగంలో కొత్త పథకాలు',
                'summary': 'తెలంగాణ ప్రభుత్వం విద్యా రంగంలో కొత్త పథకాలు ప్రవేశపెట్టనుంది. ఉచిత విద్య మరియు కొత్త పాఠశాలల నిర్మాణం గురించిన వివరాలు.',
                'source': 'విద్యా శాఖ',
                'published': (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
                'link': 'https://example.com/news5'
            }
        ]
    
    def clean_html(self, text):
        """Remove HTML tags from text"""
        if not text:
            return ""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text().strip()
    
    def create_summary(self, description, title):
        """Create a concise Telugu summary"""
        if not description:
            return f"{title[:100]}... గురించిన వివరాలు."
        
        # Clean HTML
        clean_desc = self.clean_html(description)
        
        # Take first 2 sentences or 150 characters
        sentences = clean_desc.split('.')
        if len(sentences) > 1:
            summary = '. '.join(sentences[:2]) + '.'
        else:
            summary = clean_desc
        
        # Limit length
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        # If summary is too short, add context
        if len(summary) < 50:
            summary = f"{title[:50]}... గురించిన వివరాలు మరియు తాజా సమాచారం."
        
        return summary
    
    def format_date(self, date_string):
        """Format date string"""
        try:
            if not date_string:
                return datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Try parsing different formats
            from dateutil import parser
            parsed_date = parser.parse(date_string)
            return parsed_date.strftime("%Y-%m-%d %H:%M")
        except:
            return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def fetch_rss_feed(self, feed_config, max_articles=3):
        """Fetch articles from a single RSS feed"""
        articles = []
        
        try:
            # Add user agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch with timeout
            response = requests.get(feed_config["url"], headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"HTTP {response.status_code} for {feed_config['name']}")
                return articles
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                print(f"No entries found in {feed_config['name']}")
                return articles
            
            # Process entries
            for entry in feed.entries[:max_articles]:
                try:
                    article = {
                        'id': hash(entry.link) if hasattr(entry, 'link') else hash(str(entry)),
                        'title': self.clean_html(entry.title) if hasattr(entry, 'title') else 'శీర్షిక అందుబాటులో లేదు',
                        'summary': self.create_summary(
                            entry.description if hasattr(entry, 'description') else '',
                            entry.title if hasattr(entry, 'title') else ''
                        ),
                        'source': feed_config["name"],
                        'published': self.format_date(entry.published if hasattr(entry, 'published') else ''),
                        'link': entry.link if hasattr(entry, 'link') else '#'
                    }
                    articles.append(article)
                except Exception as e:
                    print(f"Error processing entry from {feed_config['name']}: {e}")
                    continue
            
            print(f"Successfully fetched {len(articles)} articles from {feed_config['name']}")
            return articles
            
        except requests.exceptions.Timeout:
            print(f"Timeout fetching {feed_config['name']}")
        except requests.exceptions.ConnectionError:
            print(f"Connection error fetching {feed_config['name']}")
        except Exception as e:
            print(f"Error fetching {feed_config['name']}: {e}")
        
        return articles
    
    def get_telugu_news(self):
        """Fetch Telugu news from multiple sources"""
        all_articles = []
        successful_feeds = 0
        
        # Try to fetch from each RSS feed
        for feed_config in self.rss_feeds:
            try:
                articles = self.fetch_rss_feed(feed_config)
                if articles:
                    all_articles.extend(articles)
                    successful_feeds += 1
                    print(f"✓ Fetched from {feed_config['name']}: {len(articles)} articles")
                else:
                    print(f"✗ No articles from {feed_config['name']}")
            except Exception as e:
                print(f"✗ Failed to fetch from {feed_config['name']}: {e}")
        
        # If we got some articles, use them
        if all_articles:
            # Remove duplicates based on title similarity
            unique_articles = self.remove_duplicate_articles(all_articles)
            
            # Sort by published date
            try:
                unique_articles.sort(
                    key=lambda x: datetime.strptime(x['published'], "%Y-%m-%d %H:%M"), 
                    reverse=True
                )
            except:
                # If sorting fails, just return as is
                pass
            
            print(f"📰 Total unique articles fetched: {len(unique_articles)}")
            return unique_articles[:10]  # Return top 10
        
        # If no RSS feeds worked, return backup news
        print("📰 Using backup news articles")
        return self.backup_news
    
    def remove_duplicate_articles(self, articles):
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title_key = article['title'].lower().strip()[:50]  # First 50 chars
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    def get_news_by_category(self, category="all"):
        """Get news by specific category (future enhancement)"""
        # This can be enhanced to filter news by category
        return self.get_telugu_news()