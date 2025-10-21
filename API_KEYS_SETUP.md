# API Keys Setup Guide

## Where to Add Your API Keys

You need to create a `.env` file in your project root directory (`/Users/dheerajt/Desktop/news_summarizer_agent/.env`) with your API keys.

## Step-by-Step Setup

### 1. Create the .env file
```bash
cd /Users/dheerajt/Desktop/news_summarizer_agent
touch .env
```

### 2. Add your API keys to the .env file
Copy and paste this template, then replace the placeholder values with your actual keys:

```bash
# ===========================================
# REQUIRED API KEYS (Choose AI provider)
# ===========================================

# News API - Get from https://newsapi.org/
NEWS_API_KEY=your_news_api_key_here

# AI Model Provider - Choose 'openai' or 'gemini'
AI_MODEL_PROVIDER=gemini

# OpenAI API Key - Get from https://platform.openai.com/
# Only needed if AI_MODEL_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Key - Get from https://aistudio.google.com/
# Only needed if AI_MODEL_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# ===========================================
# AWS CONFIGURATION (Required for TTS)
# ===========================================

# AWS Credentials - Get from https://aws.amazon.com/
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=us-east-1

# ===========================================
# TELEGRAM CONFIGURATION (Preferred)
# ===========================================

# Telegram Bot Token - Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Telegram Chat ID - Optional, can be set per request
# Get by messaging your bot and checking: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# ===========================================
# WHATSAPP CONFIGURATION (Fallback)
# ===========================================

# Twilio Credentials - Get from https://www.twilio.com/
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here

# WhatsApp Numbers
WHATSAPP_FROM_NUMBER=whatsapp:+14155238886
WHATSAPP_TO_NUMBER=whatsapp:+1234567890

# ===========================================
# APPLICATION SETTINGS
# ===========================================

# Maximum number of news articles to fetch
MAX_NEWS_ARTICLES=5

# Summary length in minutes
SUMMARY_LENGTH_MINUTES=2

# Output directory for audio files
OUTPUT_DIR=output

# Flask secret key (change this!)
SECRET_KEY=your-secret-key-change-this
```

## Minimum Required Keys

For basic functionality, you need at least:

1. **NEWS_API_KEY** - From NewsAPI.org
2. **AWS_ACCESS_KEY_ID** - From AWS
3. **AWS_SECRET_ACCESS_KEY** - From AWS
4. **GEMINI_API_KEY** OR **OPENAI_API_KEY** - Choose one AI provider

## How the Configuration Works

Your `config.py` file automatically loads these environment variables:

```python
from dotenv import load_dotenv
load_dotenv()  # This loads your .env file

class Config:
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    # ... etc
```

## Security Notes

- **Never commit the .env file to git** (it should be in .gitignore)
- **Keep your API keys secure** and don't share them
- **Use different keys for development and production**

## Testing Your Setup

After adding your keys, test the configuration:

```bash
python -c "from config import Config; print('Configuration loaded successfully')"
```
