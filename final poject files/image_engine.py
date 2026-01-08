"""
Image Generation Engine (100% FREE VERSION).
FIXED: Flowchart error + Support for hardcoded token
"""
import requests
import urllib.parse
import random
import time
import json

class ImageGenerator:
    def __init__(self, api_key=None):
        """
        Free image generation.
        
        To hardcode your HuggingFace token, edit this line:
        """
        # 🔥 PASTE YOUR TOKEN HERE 🔥
        HARDCODED_TOKEN = "paste your token here"  # Change to: "hf_YOUR_TOKEN_HERE"
        
        # Use hardcoded token if no API key provided
        self.hf_token = api_key or HARDCODED_TOKEN
        self.hf_api = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

    def generate_educational_image(self, topic, user_level="Beginner"):
        """
        Tries multiple free APIs in order:
        1. Hugging Face (AI-generated) - if token available
        2. Unsplash (Real photos)
        3. Lorem Picsum (Always works)
        """
        
        # METHOD 1: Try Hugging Face Stable Diffusion (FREE but needs token)
        if self.hf_token:
            print(f"🎨 Trying HuggingFace with token: {self.hf_token[:10]}...")
            result = self._try_huggingface(topic, user_level)
            if result:
                print("✅ HuggingFace SUCCESS!")
                return result, None
            print("❌ HuggingFace failed, falling back...")
        
        # METHOD 2: Try Unsplash (FREE, no signup needed)
        print("📸 Trying Unsplash...")
        result = self._try_unsplash(topic)
        if result:
            print("✅ Unsplash SUCCESS!")
            return result, None
        
        # METHOD 3: Guaranteed Fallback - Lorem Picsum
        print("🖼️ Using fallback (Lorem Picsum)")
        return self._get_placeholder(topic), None

    def _try_huggingface(self, topic, user_level):
        """
        Uses Hugging Face's free Stable Diffusion API.
        """
        try:
            # Craft educational prompt
            if "Beginner" in user_level:
                style = "simple educational diagram, cartoon style, colorful, clear labels"
            else:
                style = "detailed technical diagram, scientific illustration, professional"
            
            prompt = f"educational illustration of {topic}, {style}, white background, no text"
            
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {"inputs": prompt}
            
            response = requests.post(
                self.hf_api, 
                headers=headers, 
                json=payload,
                timeout=60  # Increased timeout
            )
            
            if response.status_code == 200:
                # Return image as base64
                import base64
                img_base64 = base64.b64encode(response.content).decode()
                return f"data:image/png;base64,{img_base64}"
            else:
                print(f"HF Error: {response.status_code}")
                if response.status_code == 503:
                    print("Model is loading, please wait...")
                
        except Exception as e:
            print(f"HuggingFace exception: {e}")
        
        return None

    def _try_unsplash(self, topic):
        """
        Uses Unsplash Source - FREE random images by keyword.
        """
        try:
            # Clean topic for URL
            clean_topic = topic.replace(" ", ",").lower()[:50]
            
            # Unsplash Source API
            image_url = f"https://source.unsplash.com/1024x1024/?{clean_topic},education"
            
            # Verify it's accessible
            response = requests.head(image_url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return image_url
            
        except Exception as e:
            print(f"Unsplash failed: {e}")
        
        return None

    def _get_placeholder(self, topic):
        """
        Guaranteed fallback - Lorem Picsum.
        """
        seed = abs(hash(topic)) % 1000
        return f"https://picsum.photos/seed/{seed}/1024/1024"

    def generate_diagram(self, concept_type, data=None):
        """
        FIXED: Generate educational diagrams using QuickChart (FREE).
        """
        try:
            if concept_type == "flowchart":
                # Fixed Mermaid syntax
                mermaid_code = """graph TD
    A[Start Learning] --> B{Understand Topic?}
    B -->|Yes| C[Practice Problems]
    B -->|No| D[Review Materials]
    D --> B
    C --> E[Take Quiz]
    E --> F{Pass Quiz?}
    F -->|Yes| G[Master Level]
    F -->|No| D"""
                
                # Properly encode for QuickChart
                chart_config = {
                    "type": "mermaid",
                    "mermaid": mermaid_code
                }
                
                encoded = urllib.parse.quote(json.dumps(chart_config))
                url = f"https://quickchart.io/chart?c={encoded}&width=800&height=600"
                
                # Test if it works
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    return url
            
            elif concept_type == "pie":
                # Simple pie chart
                chart_config = {
                    "type": "pie",
                    "data": {
                        "labels": ["Understood", "Needs Review", "Not Covered"],
                        "datasets": [{
                            "data": [60, 30, 10],
                            "backgroundColor": ["#4CAF50", "#FFC107", "#F44336"]
                        }]
                    },
                    "options": {
                        "title": {
                            "display": True,
                            "text": "Learning Progress"
                        }
                    }
                }
                encoded = urllib.parse.quote(json.dumps(chart_config))
                return f"https://quickchart.io/chart?c={encoded}&width=600&height=400"
            
            elif concept_type == "bar":
                # Bar chart for progress
                chart_config = {
                    "type": "bar",
                    "data": {
                        "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
                        "datasets": [{
                            "label": "Mastery %",
                            "data": [20, 45, 65, 85],
                            "backgroundColor": "#2196F3"
                        }]
                    }
                }
                encoded = urllib.parse.quote(json.dumps(chart_config))
                return f"https://quickchart.io/chart?c={encoded}&width=600&height=400"
                
        except Exception as e:
            print(f"Diagram generation failed: {e}")
        
        # Fallback to placeholder
        return self._get_placeholder(concept_type)