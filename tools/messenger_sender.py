"""Messenger Sender Tool - Sends messages via Telegram and WhatsApp."""

import os
import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException
from config import Config


class MessengerSender:
    """Sends messages via Telegram and WhatsApp."""
    
    def __init__(self):
        # Telegram configuration
        self.telegram_bot_token = Config.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = Config.TELEGRAM_CHAT_ID
        
        # WhatsApp configuration (Twilio)
        self.twilio_account_sid = Config.TWILIO_ACCOUNT_SID
        self.twilio_auth_token = Config.TWILIO_AUTH_TOKEN
        self.whatsapp_from_number = Config.WHATSAPP_FROM_NUMBER
        self.whatsapp_to_number = Config.WHATSAPP_TO_NUMBER
        
        # Initialize clients if credentials are available
        self.telegram_bot = None
        self.twilio_client = None
        
        if self.telegram_bot_token:
            self.telegram_bot = Bot(token=self.telegram_bot_token)
        
        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = TwilioClient(self.twilio_account_sid, self.twilio_auth_token)
    
    async def send_telegram_message(self, text: str, chat_id: Optional[str] = None) -> bool:
        """
        Send a text message via Telegram.
        
        Args:
            text: Message text to send
            chat_id: Telegram chat ID (uses config default if not provided)
        
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.telegram_bot:
            print("Telegram bot not configured")
            return False
        
        chat_id = chat_id or self.telegram_chat_id
        if not chat_id:
            print("Telegram chat ID not configured")
            return False
        
        try:
            await self.telegram_bot.send_message(chat_id=chat_id, text=text)
            print(f"Telegram message sent to {chat_id}")
            return True
            
        except TelegramError as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    async def send_telegram_audio(self, audio_path: str, caption: str = "", chat_id: Optional[str] = None) -> bool:
        """
        Send an audio file via Telegram.
        
        Args:
            audio_path: Path to the audio file
            caption: Optional caption for the audio
            chat_id: Telegram chat ID (uses config default if not provided)
        
        Returns:
            True if audio sent successfully, False otherwise
        """
        if not self.telegram_bot:
            print("Telegram bot not configured")
            return False
        
        if not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return False
        
        chat_id = chat_id or self.telegram_chat_id
        if not chat_id:
            print("Telegram chat ID not configured")
            return False
        
        try:
            with open(audio_path, 'rb') as audio_file:
                await self.telegram_bot.send_audio(
                    chat_id=chat_id,
                    audio=audio_file,
                    caption=caption,
                    title="News Summary",
                    performer="News Summarizer Bot"
                )
            print(f"Telegram audio sent to {chat_id}")
            return True
            
        except TelegramError as e:
            print(f"Error sending Telegram audio: {e}")
            return False
    
    def send_whatsapp_message(self, text: str, to_number: Optional[str] = None) -> bool:
        """
        Send a text message via WhatsApp (Twilio).
        
        Args:
            text: Message text to send
            to_number: WhatsApp number to send to (uses config default if not provided)
        
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.twilio_client:
            print("Twilio client not configured")
            return False
        
        to_number = to_number or self.whatsapp_to_number
        if not to_number:
            print("WhatsApp destination number not configured")
            return False
        
        try:
            message = self.twilio_client.messages.create(
                body=text,
                from_=self.whatsapp_from_number,
                to=to_number
            )
            print(f"WhatsApp message sent: {message.sid}")
            return True
            
        except TwilioException as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
    
    def send_whatsapp_media(self, media_url: str, caption: str = "", to_number: Optional[str] = None) -> bool:
        """
        Send media (audio) via WhatsApp (Twilio).
        
        Args:
            media_url: URL of the media file
            caption: Optional caption for the media
            to_number: WhatsApp number to send to (uses config default if not provided)
        
        Returns:
            True if media sent successfully, False otherwise
        """
        if not self.twilio_client:
            print("Twilio client not configured")
            return False
        
        to_number = to_number or self.whatsapp_to_number
        if not to_number:
            print("WhatsApp destination number not configured")
            return False
        
        try:
            message = self.twilio_client.messages.create(
                body=caption,
                from_=self.whatsapp_from_number,
                to=to_number,
                media_url=[media_url]
            )
            print(f"WhatsApp media sent: {message.sid}")
            return True
            
        except TwilioException as e:
            print(f"Error sending WhatsApp media: {e}")
            return False
    
    async def send_news_summary(self, summary_text: str, audio_path: Optional[str] = None) -> dict:
        """
        Send news summary via available messaging platforms.
        
        Args:
            summary_text: Text summary of the news
            audio_path: Optional path to audio file
        
        Returns:
            Dictionary with results for each platform
        """
        results = {
            'telegram_text': False,
            'telegram_audio': False,
            'whatsapp_text': False,
            'whatsapp_audio': False
        }
        
        # Send text summary via Telegram
        if self.telegram_bot_token and self.telegram_chat_id:
            results['telegram_text'] = await self.send_telegram_message(summary_text)
        
        # Send audio via Telegram if available
        if audio_path and self.telegram_bot_token and self.telegram_chat_id:
            results['telegram_audio'] = await self.send_telegram_audio(
                audio_path, 
                caption="Your daily news summary"
            )
        
        # Send text summary via WhatsApp
        if self.twilio_account_sid and self.twilio_auth_token and self.whatsapp_to_number:
            results['whatsapp_text'] = self.send_whatsapp_message(summary_text)
        
        # Note: WhatsApp media sending requires the audio file to be accessible via URL
        # For local files, you'd need to upload to a web server first
        
        return results
    
    def get_available_platforms(self) -> list:
        """Get list of available messaging platforms based on configuration."""
        platforms = []
        
        if self.telegram_bot_token:  # Chat ID is optional
            platforms.append('telegram')
        
        if self.twilio_account_sid and self.twilio_auth_token and self.whatsapp_to_number:
            platforms.append('whatsapp')
        
        return platforms
    
    def validate_configuration(self) -> dict:
        """Validate the messaging configuration."""
        validation = {
            'telegram_configured': bool(self.telegram_bot_token),  # Chat ID is optional
            'whatsapp_configured': bool(
                self.twilio_account_sid and 
                self.twilio_auth_token and 
                self.whatsapp_to_number
            ),
            'errors': []
        }
        
        if not validation['telegram_configured']:
            if not self.telegram_bot_token:
                validation['errors'].append("Telegram bot token not configured")
            # Note: Telegram chat ID is optional - can be provided per request
        
        if not validation['whatsapp_configured']:
            if not self.twilio_account_sid:
                validation['errors'].append("Twilio account SID not configured")
            if not self.twilio_auth_token:
                validation['errors'].append("Twilio auth token not configured")
            if not self.whatsapp_to_number:
                validation['errors'].append("WhatsApp destination number not configured")
        
        return validation


# Helper function to run async functions
def run_async(coro):
    """Run an async function in a new event loop."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)
