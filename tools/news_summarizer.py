"""News Summarizer Tool - Uses AI models (OpenAI GPT or Google Gemini) to create podcast-style summaries."""

from typing import List, Optional
import google.generativeai as genai
from config import Config
from tools.news_fetcher import NewsArticle

# Try to import OpenAI dependencies (optional)
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class NewsSummarizer:
    """Summarizes news articles into podcast-style content using AI models."""
    
    def __init__(self):
        self.ai_provider = Config.AI_MODEL_PROVIDER.lower()
        self.summary_length_minutes = Config.SUMMARY_LENGTH_MINUTES
        
        # Initialize based on the configured AI provider
        if self.ai_provider == 'gemini':
            self._init_gemini()
        elif self.ai_provider == 'openai':
            self._init_openai()
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
    
    def _init_gemini(self):
        """Initialize Gemini AI model."""
        self.gemini_api_key = Config.GEMINI_API_KEY
        
        if not self.gemini_api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        print("Gemini AI model initialized")
    
    def _init_openai(self):
        """Initialize OpenAI model."""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI dependencies not available. Install langchain-openai.")
        
        self.openai_api_key = Config.OPENAI_API_KEY
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            api_key=self.openai_api_key,
            temperature=0.7,
            max_tokens=1500
        )
        
        print("OpenAI model initialized")
    
    def create_podcast_summary(self, articles: List[NewsArticle]) -> str:
        """Create a podcast-style summary from news articles."""
        if not articles:
            return "No news articles available for summarization."
        
        # Prepare the articles text
        articles_text = self._prepare_articles_text(articles)
        
        # Create the prompt
        print(articles_text)
        prompt = self._create_prompt(articles_text)
        
        try:
            # Generate the summary based on the AI provider
            if self.ai_provider == 'gemini':
                response = self.model.generate_content(prompt)
                print(response.text)
                return response.text
            elif self.ai_provider == 'openai':
                response = self.llm.invoke(prompt)
                return response.content
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Sorry, I encountered an error while generating the news summary."
    
    def _prepare_articles_text(self, articles: List[NewsArticle]) -> str:
        """Prepare articles text for the LLM."""
        articles_text = ""
        
        for i, article in enumerate(articles, 1):
            articles_text += f"Article {i}:\n"
            articles_text += f"Title: {article.title}\n"
            articles_text += f"Source: {article.source}\n"
            articles_text += f"Content: {article.content[:500]}...\n\n"  # Limit content length
        
        return articles_text
    
    def _create_prompt(self, articles_text: str) -> str:
        """Create the prompt for the LLM."""
        return f"""You are a friendly news podcast host. Your task is to create a {self.summary_length_minutes}-minute podcast-style summary of the following news articles.

Guidelines:
1. Write in a conversational, engaging tone as if you're speaking to listeners
2. Keep the summary to approximately {self.summary_length_minutes} minutes of speaking time (roughly {self.summary_length_minutes * 150} words)
3. Start with a warm greeting and brief introduction
4. Cover the most important and interesting stories
5. Use transitions between topics like "Speaking of...", "In other news...", "Meanwhile..."
6. End with a closing remark
7. Focus on the key facts and implications
8. Make it engaging and easy to follow
9. Do not include content like 'Intro Music fades in', '**Host:**'

News Articles:
{articles_text}

Please create a podcast-style summary that flows naturally and keeps listeners engaged."""
    
    def create_structured_summary(self, articles: List[NewsArticle]) -> dict:
        """Create a structured summary with key points."""
        if not articles:
            return {"summary": "No news articles available.", "key_points": [], "sources": []}
        
        articles_text = self._prepare_articles_text(articles)
        
        # Create a more structured prompt
        structured_prompt = f"""Analyze the following news articles and provide a structured summary.

News Articles:
{articles_text}

Please provide your response in the following JSON format:
{{
    "summary": "A brief 2-3 sentence overview of the main news",
    "key_points": [
        "Key point 1",
        "Key point 2",
        "Key point 3"
    ],
    "sources": ["Source 1", "Source 2"],
    "podcast_script": "A conversational script for a {self.summary_length_minutes}-minute podcast segment"
}}

Make the podcast script engaging and conversational, as if speaking directly to listeners."""

        try:
            # Generate the summary based on the AI provider
            if self.ai_provider == 'gemini':
                response = self.model.generate_content(structured_prompt)
                content = response.text
            elif self.ai_provider == 'openai':
                response = self.llm.invoke(structured_prompt)
                content = response.content
            
            # For now, return a structured format
            return {
                "summary": content,
                "key_points": [article.title for article in articles[:3]],
                "sources": list(set([article.source for article in articles])),
                "podcast_script": content
            }
            
        except Exception as e:
            print(f"Error generating structured summary: {e}")
            return {
                "summary": "Error generating summary",
                "key_points": [],
                "sources": [],
                "podcast_script": "Sorry, I encountered an error while generating the news summary."
            }
    
    def estimate_speaking_time(self, text: str) -> float:
        """Estimate speaking time in minutes based on text length."""
        # Average speaking rate is about 150-160 words per minute
        word_count = len(text.split())
        return word_count / 150.0
