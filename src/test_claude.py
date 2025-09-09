# src/test_claude.py
import anthropic
import sys
import os

# Add the config directory to our path so we can import credentials
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from config.credentials import CLAUDE_API_KEY
except ImportError:
    print("❌ Error: Can't find credentials.py file!")
    print("Make sure you created config/credentials.py with your API key")
    exit(1)

def test_claude_connection():
    """
    Test if we can connect to Claude successfully
    """
    print("🤖 Testing connection to Claude...")
    
    try:
        # Create the Claude client
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        
        # Send a simple test message
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{
                "role": "user", 
                "content": "Hello Claude! I'm building an AI assistant. Can you respond with just 'Hello! I'm ready to help with your AI assistant project.'"
            }]
        )
        
        print("✅ Connection successful!")
        print("📝 Claude's response:")
        print(response.content[0].text)
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Jarvis AI Assistant - Connection Test")
    print("=" * 50)
    
    test_claude_connection()