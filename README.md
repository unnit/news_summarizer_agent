# News Summarizer Agent

An AI-powered news summarization agent that fetches the latest news, creates podcast-style summaries using Google Gemini or OpenAI GPT, converts them to speech with Amazon Polly, and delivers them via Telegram and WhatsApp.

## Features

🔍 **News Fetching**: Retrieves top headlines from NewsAPI and RSS feeds  
🤖 **AI Summarization**: Uses Google Gemini or OpenAI GPT to create engaging podcast-style summaries  
🎤 **Text-to-Speech**: Converts summaries to natural-sounding audio using Amazon Polly  
📱 **Multi-Platform Delivery**: Sends summaries via Telegram and WhatsApp  
🌐 **Web Interface**: Beautiful, responsive web UI for easy access  
⚡ **Fully Automated**: Complete workflow from news fetching to message delivery  

## Architecture

The agent consists of four main tools:

1. **News Fetcher**: Fetches news from NewsAPI and RSS feeds
2. **News Summarizer**: Uses Google Gemini or OpenAI GPT to create podcast-style summaries
3. **TTS Converter**: Converts text to speech using Amazon Polly
4. **Messenger Sender**: Delivers messages via Telegram and WhatsApp

## Web Interface Features

The web interface provides a modern, user-friendly experience:

- 📱 **Mobile-Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- 🎨 **Beautiful UI**: Clean, modern interface with smooth animations
- 📞 **Phone Number Input**: Smart formatting with country code validation
- 🎛️ **Customizable Options**: Choose news category, country, and voice preferences
- ⏳ **Real-time Progress**: Visual progress indicators during processing
- 🎧 **Audio Download**: Direct download links for generated audio files
- 📊 **Status Updates**: Real-time feedback on WhatsApp delivery status
- 🔄 **Easy Reset**: One-click to generate another summary

## Prerequisites

- Python 3.8 or higher
- NewsAPI account (free tier available)
- Google Gemini API key OR OpenAI API key
- AWS account with Amazon Polly access
- Telegram bot (optional)
- Twilio account for WhatsApp (optional)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd news_summarizer_agent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

## Configuration

Create a `.env` file with the following variables:

### Required
```env
# News API Configuration
NEWS_API_KEY=your_news_api_key_here

# AI Model Configuration (choose one)
AI_MODEL_PROVIDER=gemini  # or 'openai'
GEMINI_API_KEY=your_gemini_api_key_here  # if using Gemini
# OPENAI_API_KEY=your_openai_api_key_here  # if using OpenAI

# AWS Configuration for Amazon Polly
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
```

### Optional (for messaging)
```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# WhatsApp Configuration (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
WHATSAPP_FROM_NUMBER=whatsapp:+14155238886
WHATSAPP_TO_NUMBER=whatsapp:+1234567890
```

## API Setup Guide

### 1. NewsAPI
1. Go to [NewsAPI](https://newsapi.org/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add it to your `.env` file

### 2. Google Gemini API (Recommended)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" and create a new key
4. Add it to your `.env` file as `GEMINI_API_KEY`
5. Set `AI_MODEL_PROVIDER=gemini` in your `.env` file

### 3. OpenAI API (Alternative)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and add billing information
3. Generate an API key
4. Add it to your `.env` file as `OPENAI_API_KEY`
5. Set `AI_MODEL_PROVIDER=openai` in your `.env` file

### 4. Amazon Polly
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to Amazon Polly
3. Create an IAM user with Polly permissions
4. Generate access keys and add them to your `.env` file

### 5. Telegram Bot (Optional)
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token
4. Get your chat ID by messaging your bot and checking: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`

### 6. WhatsApp via Twilio (Optional)
1. Sign up for [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token
3. Set up WhatsApp Sandbox for testing
4. Add the credentials to your `.env` file

## Usage

### Web Interface (Recommended)

The easiest way to use the News Summarizer Agent is through the web interface:

1. **Start the web application**:
   ```bash
   python web_app.py
   ```

2. **Open your browser** and go to `http://localhost:5000`

3. **Enter your mobile number** with country code (e.g., +1 234 567 8900)

4. **Select your preferences**:
   - News category (General, Technology, Business, etc.)
   - Country for news sources
   - Voice for audio generation

5. **Click "Generate News Summary"** and wait for the magic to happen!

The web interface will:
- ✅ Fetch the latest news
- 🤖 Create an AI-powered summary
- 🎤 Generate natural-sounding audio
- 📱 Send the audio to your WhatsApp (if configured)
- 📥 Provide a download link for the audio file

### Command Line Interface

Run the complete workflow from command line:
```bash
python main.py
```

### Advanced Usage

```bash
# Text-only mode (no audio or messaging)
python main.py --mode text-only

# Specific news category
python main.py --category technology

# Different country
python main.py --country gb

# Custom voice
python main.py --voice Matthew

# Skip sending messages
python main.py --no-messages

# Check agent status
python main.py --status
```

### Command Line Options

- `--mode`: Choose between 'full' or 'text-only' workflow
- `--category`: News category (general, business, technology, health, science, sports, entertainment)
- `--country`: Country code (us, gb, ca, au, etc.)
- `--voice`: Amazon Polly voice ID (Joanna, Matthew, Salli, etc.)
- `--no-messages`: Skip sending messages via platforms
- `--status`: Show agent configuration status

## Available Voices

Amazon Polly offers various voices. Popular choices for podcast-style content:

- `Joanna`: Clear, professional female voice (default)
- `Matthew`: Warm, conversational male voice
- `Salli`: Friendly, casual female voice
- `Kimberly`: Professional, authoritative female voice
- `Joey`: Natural, conversational male voice

To see all available voices:
```python
from tools.tts_converter import TTSConverter
converter = TTSConverter()
voices = converter.get_available_voices()
```

## Project Structure

```
news_summarizer_agent/
├── main.py                 # Main application entry point
├── web_app.py             # Flask web application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore file
├── README.md            # This file
├── templates/           # HTML templates
│   └── index.html        # Main web interface
├── static/              # Static web assets
│   ├── css/
│   │   └── style.css     # Web interface styles
│   └── js/
│       └── app.js        # Web interface JavaScript
├── tools/               # Tool implementations
│   ├── __init__.py
│   ├── news_fetcher.py     # News fetching logic
│   ├── news_summarizer.py  # AI summarization
│   ├── tts_converter.py    # Text-to-speech conversion
│   └── messenger_sender.py # Message delivery
└── output/              # Generated audio files (created automatically)
```

## Workflow

1. **News Fetching**: Retrieves top headlines from NewsAPI and popular RSS feeds
2. **Deduplication**: Removes duplicate articles based on title similarity
3. **Summarization**: Uses GPT-4 to create engaging, podcast-style summaries
4. **Text-to-Speech**: Converts summaries to natural-sounding audio using Amazon Polly
5. **Message Delivery**: Sends text summaries and audio files via configured platforms

## Error Handling

The agent includes comprehensive error handling:
- Network connectivity issues
- API rate limits and failures
- Invalid configuration
- Missing dependencies
- Audio generation failures

## Customization

### Adding New News Sources
Edit `tools/news_fetcher.py` and add RSS feeds to the `POPULAR_RSS_FEEDS` list.

### Customizing Summaries
Modify the prompt in `tools/news_summarizer.py` to change the summary style or length.

### Adding New Messaging Platforms
Extend `tools/messenger_sender.py` to add support for additional platforms.

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure all required API keys are set in your `.env` file
   - Check that the `.env` file is in the project root directory

2. **"No news articles were fetched"**
   - Verify your NewsAPI key is valid
   - Check your internet connection
   - Ensure NewsAPI quota hasn't been exceeded

3. **"Error generating summary"**
   - For Gemini: Verify your Google Gemini API key is valid and has proper permissions
   - For OpenAI: Verify your OpenAI API key is valid and has sufficient credits
   - Check that the AI_MODEL_PROVIDER is set correctly in your `.env` file

4. **"Audio creation failed"**
   - Verify your AWS credentials are correct
   - Check that Amazon Polly is available in your AWS region
   - Ensure your AWS account has Polly permissions

5. **"Telegram/WhatsApp messages failed"**
   - Verify bot tokens and chat IDs are correct
   - Check that bots are properly configured
   - Ensure destination numbers are in correct format

### Debug Mode

For detailed logging, you can modify the code to add more print statements or use Python's logging module.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration setup
3. Open an issue on GitHub

## Roadmap

- [ ] Support for additional news sources
- [ ] Multiple language support
- [ ] Custom summary templates
- [ ] Scheduled execution
- [ ] Web dashboard
- [ ] Email delivery option
- [ ] Voice customization options
- [ ] Batch processing capabilities
