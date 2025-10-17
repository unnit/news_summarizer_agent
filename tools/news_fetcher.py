"""News Fetcher Tool - Fetches news articles from various sources."""

import requests
import feedparser
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import Config


class NewsArticle:
    """Represents a news article."""
    
    def __init__(self, title: str, content: str, url: str, source: str, published_at: Optional[datetime] = None):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.published_at = published_at or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert article to dictionary."""
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'published_at': self.published_at.isoformat()
        }


class NewsFetcher:
    """Fetches news from various sources."""
    
    def __init__(self):
        self.news_api_key = Config.NEWS_API_KEY
        self.max_articles = Config.MAX_NEWS_ARTICLES
    
    def fetch_from_newsapi(self, category: str = 'general', country: str = 'us') -> List[NewsArticle]:
        """Fetch news from NewsAPI."""
        if not self.news_api_key:
            raise ValueError("NewsAPI key is required")
        
        url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'apiKey': self.news_api_key,
            'category': category,
            'country': country,
            'pageSize': self.max_articles
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article_data in data.get('articles', []):
                if article_data.get('title') and article_data.get('content'):
                    article = NewsArticle(
                        title=article_data['title'],
                        content=article_data.get('content', '') or article_data.get('description', ''),
                        url=article_data.get('url', ''),
                        source=article_data.get('source', {}).get('name', 'Unknown'),
                        published_at=self._parse_date(article_data.get('publishedAt'))
                    )
                    articles.append(article)
            
            return articles
            print(articles)
            
        except requests.RequestException as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []
    
    def fetch_from_rss(self, rss_url: str) -> List[NewsArticle]:
        """Fetch news from RSS feed."""
        try:
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:self.max_articles]:
                if entry.get('title'):
                    # Try to get content from different fields
                    content = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
                    content = content or entry.get('summary', '') or entry.get('description', '')
                    
                    article = NewsArticle(
                        title=entry['title'],
                        content=content,
                        url=entry.get('link', ''),
                        source=feed.feed.get('title', 'RSS Feed'),
                        published_at=self._parse_date(entry.get('published'))
                    )
                    print(entry['title'])
                    articles.append(article)
            return articles
            
        except Exception as e:
            print(f"Error fetching from RSS feed: {e}")
            return []
    
    def fetch_top_headlines(self, sources: Optional[List[str]] = None) -> List[NewsArticle]:
        """Fetch top headlines from multiple sources."""
        all_articles = []
        
        # Fetch from NewsAPI
        try:
            newsapi_articles = self.fetch_from_newsapi()
            all_articles.extend(newsapi_articles)
        except Exception as e:
            print(f"Failed to fetch from NewsAPI: {e}")
        
        # Add RSS feeds if specified
        if sources:
            for source in sources:
                try:
                    rss_articles = self.fetch_from_rss(source)
                    all_articles.extend(rss_articles)
                except Exception as e:
                    print(f"Failed to fetch from RSS source {source}: {e}")
        
        # Remove duplicates based on title similarity
        unique_articles = self._remove_duplicates(all_articles)
        
        # Sort by publication date (newest first)
        unique_articles.sort(key=lambda x: x.published_at, reverse=True)
        
        return unique_articles[:self.max_articles]
    
    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_string:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try common RSS date formats
                from email.utils import parsedate_to_datetime
                return parsedate_to_datetime(date_string)
            except (ValueError, TypeError):
                return None
    
    def _remove_duplicates(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity."""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Simple deduplication based on normalized title
            normalized_title = article.title.lower().strip()
            if normalized_title not in seen_titles and len(normalized_title) > 10:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        return unique_articles


# Popular RSS feeds for news
POPULAR_RSS_FEEDS = [
    'http://feeds.bbci.co.uk/news/rss.xml',
    'https://rss.cnn.com/rss/edition.rss',
    'https://feeds.reuters.com/reuters/topNews',
    'https://feeds.npr.org/1001/rss.xml',
    'https://feeds.skynews.com/feeds/rss/world.xml'
]
