"""TTS Converter Tool - Uses Amazon Polly to convert text to speech."""

import boto3
import os
from datetime import datetime
from typing import Optional
from config import Config


class TTSConverter:
    """Converts text to speech using Amazon Polly."""
    
    def __init__(self):
        self.aws_access_key_id = Config.AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY
        self.aws_region = Config.AWS_REGION
        self.output_dir = Config.OUTPUT_DIR
        
        if not all([self.aws_access_key_id, self.aws_secret_access_key]):
            raise ValueError("AWS credentials are required for Amazon Polly")
        
        # Initialize Polly client
        self.polly_client = boto3.client(
            'polly',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region
        )
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def text_to_speech(
        self, 
        text: str, 
        voice_id: str = 'Joanna', 
        output_format: str = 'mp3',
        filename: Optional[str] = None
    ) -> str:
        """
        Convert text to speech using Amazon Polly.
        
        Args:
            text: Text to convert to speech
            voice_id: Polly voice ID (default: 'Joanna')
            output_format: Output format ('mp3', 'ogg_vorbis', 'pcm')
            filename: Custom filename (optional)
        
        Returns:
            Path to the generated audio file
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_summary_{timestamp}.{output_format}"
        
        # Ensure filename has correct extension
        if not filename.endswith(f'.{output_format}'):
            filename += f'.{output_format}'
        
        file_path = os.path.join(self.output_dir, filename)
        
        try:
            # Configure SSML for better speech quality
            ssml_text = self._prepare_ssml(text)
            
            # Request speech synthesis
            response = self.polly_client.synthesize_speech(
                Text=ssml_text,
                OutputFormat=output_format,
                VoiceId=voice_id,
                TextType='ssml',
                Engine='standard'  # Use standard engine for compatibility
            )
            
            # Save audio file
            with open(file_path, 'wb') as audio_file:
                audio_file.write(response['AudioStream'].read())
            
            print(f"Audio file saved: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"Error converting text to speech: {e}")
            raise
    
    def _prepare_ssml(self, text: str) -> str:
        """
        Prepare text as SSML (Speech Synthesis Markup Language) for better speech quality.
        """
        # Clean up the text
        text = text.strip()
        
        # Wrap in SSML tags with prosody adjustments for podcast-style delivery
        ssml = f"""
        <speak>
            <prosody rate="medium" pitch="medium">
                <break time="500ms"/>
                {self._escape_ssml(text)}
                <break time="1s"/>
            </prosody>
        </speak>
        """
        
        return ssml.strip()
    
    def _escape_ssml(self, text: str) -> str:
        """Escape special characters for SSML."""
        # Replace common text patterns with SSML equivalents
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # Add pauses for better flow
        text = text.replace('. ', '. <break time="300ms"/> ')
        text = text.replace('! ', '! <break time="500ms"/> ')
        text = text.replace('? ', '? <break time="500ms"/> ')
        text = text.replace(', ', ', <break time="200ms"/> ')
        
        # Add emphasis for important words (you can customize this)
        important_words = ['breaking', 'urgent', 'important', 'major', 'significant']
        for word in important_words:
            text = text.replace(f' {word} ', f' <emphasis level="strong">{word}</emphasis> ')
        
        return text
    
    def get_available_voices(self) -> list:
        """Get list of available voices from Polly."""
        try:
            response = self.polly_client.describe_voices()
            voices = response.get('Voices', [])
            
            # Filter for neural voices (better quality)
            neural_voices = [
                voice for voice in voices 
                if voice.get('SupportedEngines', []).count('neural') > 0
            ]
            
            return neural_voices
            
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []
    
    def get_recommended_voices(self) -> dict:
        """Get recommended voices for different use cases."""
        return {
            'news_anchor': 'Joanna',      # Clear, professional female voice
            'podcast_host': 'Matthew',    # Warm, conversational male voice
            'casual': 'Salli',           # Friendly, casual female voice
            'professional': 'Kimberly',   # Professional, authoritative female voice
            'conversational': 'Joey',     # Natural, conversational male voice
            'international': 'Emma'       # British accent for international feel
        }
    
    def validate_text_length(self, text: str) -> bool:
        """Validate that text is within Polly's limits."""
        # Polly has a 100,000 character limit for SSML
        return len(text) <= 100000
    
    def split_long_text(self, text: str, max_length: int = 8000) -> list:
        """Split long text into chunks for processing."""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence + '. ') <= max_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def create_podcast_audio(self, text: str, voice_id: str = 'Joanna') -> str:
        """Create podcast-style audio with optimized settings."""
        # Validate text length
        if not self.validate_text_length(text):
            print("Text is too long, splitting into chunks...")
            chunks = self.split_long_text(text)
            
            # For now, just process the first chunk
            # In a production system, you might want to concatenate multiple audio files
            text = chunks[0]
        
        # Use podcast-optimized settings
        return self.text_to_speech(
            text=text,
            voice_id=voice_id,
            output_format='mp3',
            filename=f"podcast_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )
