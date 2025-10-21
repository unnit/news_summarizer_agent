"""Example usage of the News Summarizer Agent."""

import os
import sys
from main import NewsSummarizerAgent

def example_basic_usage():
    """Example of basic usage."""
    print("=== Basic Usage Example ===")
    
    # Initialize the agent
    agent = NewsSummarizerAgent()
    
    # Run the complete workflow
    results = agent.run_complete_workflow()
    
    print(f"Workflow completed: {results['success']}")
    if results['success']:
        print(f"Articles fetched: {results['articles_fetched']}")
        print(f"Audio created: {results.get('audio_created', False)}")
        print(f"Messages sent: {results.get('messages_sent', {})}")

def example_text_only():
    """Example of text-only workflow."""
    print("\n=== Text-Only Workflow Example ===")
    
    agent = NewsSummarizerAgent()
    
    # Run text-only workflow
    results = agent.run_text_only_workflow()
    
    if results['success']:
        print(f"Summary generated: {len(results['summary'])} characters")
        print(f"Preview: {results['summary'][:200]}...")

def example_custom_settings():
    """Example with custom settings."""
    print("\n=== Custom Settings Example ===")
    
    agent = NewsSummarizerAgent()
    
    # Run with custom settings
    results = agent.run_complete_workflow(
        news_category='technology',
        country='us',
        voice_id='Matthew',
        send_messages=False  # Don't send messages, just generate audio
    )
    
    print(f"Custom workflow completed: {results['success']}")

if __name__ == '__main__':
    print("News Summarizer Agent - Example Usage")
    print("=====================================")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print(".env file not found. Please create one with your API keys.")
        print("See README.md for setup instructions.")
        print("\nRequired for Gemini:")
        print("- GEMINI_API_KEY")
        print("- AI_MODEL_PROVIDER=gemini")
        print("\nRequired for OpenAI:")
        print("- OPENAI_API_KEY")
        print("- AI_MODEL_PROVIDER=openai")
        sys.exit(1)
    
    try:
        # Run examples
        example_basic_usage()
        example_text_only()
        example_custom_settings()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure all API keys are configured in your .env file.")
        print("For Gemini: Set GEMINI_API_KEY and AI_MODEL_PROVIDER=gemini")
        print("For OpenAI: Set OPENAI_API_KEY and AI_MODEL_PROVIDER=openai")
