import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: API Key not found in .env")
else:
    print(f"✅ Found API Key: {api_key[:5]}...")
    
    # Configure the library
    genai.configure(api_key=api_key)

    print("\n🔍 Listing available models for this key...")
    try:
        found_any = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                found_any = True
        
        if not found_any:
            print("⚠️ No models found. Your API key might be invalid or region-locked.")
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")