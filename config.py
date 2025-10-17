"""Configuration settings for the News Summarizer Agent."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # News API Configuration
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    
    # AI Model Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    AI_MODEL_PROVIDER = os.getenv('AI_MODEL_PROVIDER', 'gemini')  # 'openai' or 'gemini'
    
    # AWS Configuration for Amazon Polly
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # WhatsApp Configuration (Twilio)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    WHATSAPP_FROM_NUMBER = os.getenv('WHATSAPP_FROM_NUMBER')
    WHATSAPP_TO_NUMBER = os.getenv('WHATSAPP_TO_NUMBER')
    
    # Application Settings
    MAX_NEWS_ARTICLES = int(os.getenv('MAX_NEWS_ARTICLES', '5'))
    SUMMARY_LENGTH_MINUTES = int(os.getenv('SUMMARY_LENGTH_MINUTES', '2'))
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        required_vars = [
            'NEWS_API_KEY',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY'
        ]
        
        # Add AI model provider specific requirements
        if cls.AI_MODEL_PROVIDER.lower() == 'openai':
            required_vars.append('OPENAI_API_KEY')
        elif cls.AI_MODEL_PROVIDER.lower() == 'gemini':
            required_vars.append('GEMINI_API_KEY')
        else:
            raise ValueError(f"Unsupported AI model provider: {cls.AI_MODEL_PROVIDER}. Use 'openai' or 'gemini'.")
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
