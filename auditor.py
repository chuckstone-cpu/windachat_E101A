import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ Error: GOOGLE_API_KEY not found in .env file.")

genai.configure(api_key=api_key)

# We removed Serper/Search Tool completely.

# --- SAFETY WRAPPER (Prevents Crashing) ---
def generate_safe(model, prompt, retries=3):
    """
    Tries to call Gemini. If it hits a limit, it waits and retries.
    """
    for attempt in range(retries):
        try:
            return model.generate_content(prompt).text.strip()
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                print(f"⚠️ Limit Hit. Waiting 10s... (Attempt {attempt+1})")
                time.sleep(10)
            else:
                return f"Error: {e}"
    return "Error: Failed after retries."

class ContentAuditor:
    def __init__(self):
        # We use standard Gemini Pro. It has huge internal knowledge.
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def check_bias(self, text_chunk):
        print("🔍 Scanning for bias...")
        prompt = f"""
        Analyze this text for gender bias, racial stereotypes, or exclusionary language.
        Text: "{text_chunk[:2000]}"
        
        Reply strictly:
        - "SAFE" (if neutral)
        - "WARNING: [Brief explanation]" (if biased)
        """
        return generate_safe(self.model, prompt)

    def verify_facts(self, text_chunk):
        print("🧠 Verifying facts using Internal Knowledge...")
        
        # WE ASK THE AI TO BE THE ENCYCLOPEDIA
        verify_prompt = f"""
        You are a strict Academic Fact-Checker. 
        Compare the claims in the text below against your internal knowledge base of established history and science.

        Text to Check: "{text_chunk[:2000]}"

        INSTRUCTIONS:
        1. Identify any statements that are FACTUALLY WRONG (e.g., "Earth is flat", "Aliens built pyramids").
        2. Ignore opinions or simplified explanations. Focus on hard errors.
        
        OUTPUT FORMAT:
        - If the text is accurate: Return "VERIFIED".
        - If there is a factual error: Return "MISINFORMATION: [Explain the error clearly]".
        """
        
        return generate_safe(self.model, verify_prompt)

# --- FAST TEST BLOCK ---
if __name__ == "__main__":
    auditor = ContentAuditor()
    
    print("\n--- Test 1: Bias ---")
    print(auditor.check_bias("The fireman met the stewardess."))

    print("\n--- Test 2: Fact Check (The Lie) ---")
    # Gemini knows this is false without needing Google
    print(auditor.verify_facts("The Great Wall of China was built in 1995 by aliens.")) 
    
    print("\n--- Test 3: Fact Check (The Truth) ---")
    print(auditor.verify_facts("Water boils at 100 degrees Celsius at sea level."))