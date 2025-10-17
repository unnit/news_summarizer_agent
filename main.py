"""Main News Summarizer Agent Application."""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from typing import Optional

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from tools.news_fetcher import NewsFetcher, POPULAR_RSS_FEEDS
from tools.news_summarizer import NewsSummarizer
from tools.tts_converter import TTSConverter
from tools.messenger_sender import MessengerSender, run_async


class NewsSummarizerAgent:
    """Main orchestrator for the News Summarizer Agent."""
    
    def __init__(self):
        """Initialize the agent with all required tools."""
        try:
            # Validate configuration
            Config.validate_config()
            
            # Initialize tools
            self.news_fetcher = NewsFetcher()
            self.news_summarizer = NewsSummarizer()
            self.tts_converter = TTSConverter()
            self.messenger_sender = MessengerSender()
            
            print("✅ News Summarizer Agent initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing agent: {e}")
            sys.exit(1)
    
    def run_complete_workflow(
        self, 
        news_category: str = 'general',
        country: str = 'us',
        rss_feeds: Optional[list] = None,
        voice_id: str = 'Joanna',
        send_messages: bool = True
    ) -> dict:
        """
        Run the complete news summarization workflow.
        
        Args:
            news_category: News category for NewsAPI
            country: Country code for NewsAPI
            rss_feeds: List of RSS feed URLs
            voice_id: Voice ID for Amazon Polly
            send_messages: Whether to send messages via platforms
        
        Returns:
            Dictionary with workflow results
        """
        results = {
            'success': False,
            'articles_fetched': 0,
            'summary_generated': False,
            'audio_created': False,
            'messages_sent': {},
            'errors': []
        }
        
        try:
            print("🚀 Starting News Summarizer Agent workflow...")
            
            # Step 1: Fetch news articles
            print("📰 Fetching news articles...")
            articles = self.news_fetcher.fetch_top_headlines(
                sources=rss_feeds or POPULAR_RSS_FEEDS[:2]  # Use first 2 RSS feeds if none specified
            )
            
            if not articles:
                results['errors'].append("No news articles were fetched")
                return results
            
            results['articles_fetched'] = len(articles)
            print(f"✅ Fetched {len(articles)} news articles")
            
            # Step 2: Generate summary
            print("🤖 Generating podcast-style summary...")
            summary = self.news_summarizer.create_podcast_summary(articles)
            
            if not summary or summary == "No news articles available for summarization.":
                results['errors'].append("Failed to generate summary")
                return results
            
            results['summary_generated'] = True
            print("✅ Summary generated successfully")
            print(f"📝 Summary length: {len(summary)} characters")
            
            # Step 3: Convert to speech
            print("🎤 Converting summary to speech...")
            try:
                audio_path = self.tts_converter.create_podcast_audio(summary, voice_id)
                results['audio_created'] = True
                results['audio_path'] = audio_path
                print(f"✅ Audio created: {audio_path}")
                
            except Exception as e:
                print(f"⚠️ Audio creation failed: {e}")
                results['errors'].append(f"Audio creation failed: {e}")
            
            # Step 4: Send messages (if requested)
            if send_messages:
                print("📱 Sending messages...")
                try:
                    message_results = run_async(
                        self.messenger_sender.send_news_summary(summary, results.get('audio_path'))
                    )
                    results['messages_sent'] = message_results
                    
                    # Print results
                    for platform, success in message_results.items():
                        status = "✅" if success else "❌"
                        print(f"{status} {platform}: {'Sent' if success else 'Failed'}")
                        
                except Exception as e:
                    print(f"⚠️ Message sending failed: {e}")
                    results['errors'].append(f"Message sending failed: {e}")
            else:
                print("📱 Message sending skipped")
            
            results['success'] = True
            print("🎉 Workflow completed successfully!")
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def run_text_only_workflow(self, news_category: str = 'general') -> dict:
        """Run workflow without audio generation or messaging."""
        results = {
            'success': False,
            'articles_fetched': 0,
            'summary': '',
            'errors': []
        }
        
        try:
            print("🚀 Starting text-only workflow...")
            
            # Fetch news
            articles = self.news_fetcher.fetch_top_headlines()
            if not articles:
                results['errors'].append("No news articles were fetched")
                return results
            
            results['articles_fetched'] = len(articles)
            print(f"✅ Fetched {len(articles)} news articles")
            
            # Generate summary
            summary = self.news_summarizer.create_podcast_summary(articles)
            if not summary:
                results['errors'].append("Failed to generate summary")
                return results
            
            results['summary'] = summary
            results['success'] = True
            print("✅ Text summary generated successfully")
            
        except Exception as e:
            print(f"❌ Text workflow failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def get_status(self) -> dict:
        """Get the current status of the agent."""
        return {
            'configuration_valid': True,
            'available_platforms': self.messenger_sender.get_available_platforms(),
            'polly_voices': len(self.tts_converter.get_available_voices()),
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='News Summarizer Agent')
    parser.add_argument('--mode', choices=['full', 'text-only'], default='full',
                       help='Run mode: full workflow or text-only')
    parser.add_argument('--category', default='general',
                       help='News category (general, business, technology, etc.)')
    parser.add_argument('--country', default='us',
                       help='Country code for news (us, gb, ca, etc.)')
    parser.add_argument('--voice', default='Joanna',
                       help='Amazon Polly voice ID')
    parser.add_argument('--no-messages', action='store_true',
                       help='Skip sending messages')
    parser.add_argument('--status', action='store_true',
                       help='Show agent status and exit')
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = NewsSummarizerAgent()
    
    # Show status if requested
    if args.status:
        status = agent.get_status()
        print("📊 Agent Status:")
        print(f"  Available platforms: {', '.join(status['available_platforms']) or 'None'}")
        print(f"  Polly voices available: {status['polly_voices']}")
        print(f"  Timestamp: {status['timestamp']}")
        return
    
    # Run workflow based on mode
    if args.mode == 'full':
        results = agent.run_complete_workflow(
            news_category=args.category,
            country=args.country,
            voice_id=args.voice,
            send_messages=not args.no_messages
        )
    else:
        results = agent.run_text_only_workflow(news_category=args.category)
    
    # Print final results
    print("\n📊 Final Results:")
    print(f"  Success: {'✅' if results['success'] else '❌'}")
    print(f"  Articles fetched: {results.get('articles_fetched', 0)}")
    
    if results.get('summary_generated'):
        print("  Summary: ✅ Generated")
    if results.get('audio_created'):
        print(f"  Audio: ✅ Created at {results.get('audio_path', 'Unknown')}")
    
    if results.get('messages_sent'):
        print("  Messages sent:")
        for platform, success in results['messages_sent'].items():
            print(f"    {platform}: {'✅' if success else '❌'}")
    
    if results.get('errors'):
        print("  Errors:")
        for error in results['errors']:
            print(f"    ❌ {error}")
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == '__main__':
    main()
