"""
Quick test to verify Groq API key is working
"""
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "")

print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"API Key length: {len(api_key)}")
print(f"API Key starts with: {api_key[:10] if api_key else 'N/A'}...")

if api_key:
    print("\nTesting Groq API connection...")
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'API working' if you receive this."}],
            max_tokens=10
        )
        
        print(f"✓ API Response: {response.choices[0].message.content}")
        print("✓ Groq API is working correctly!")
        
    except Exception as e:
        print(f"✗ API Error: {e}")
else:
    print("\n✗ No API key found in .env file")
