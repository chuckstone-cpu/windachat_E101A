"""
Adaptive LLM Interface with GPU Support
Combines pedagogical strategies with GPU-accelerated local models
"""

from typing import List, Dict
import os
import torch


class AdaptiveTutor:
    def __init__(self, model_path=None, use_gpu=True):
        """
        Initialize adaptive tutor with optional local model or Ollama.
        
        Args:
            model_path: Path to local GGUF model directory
            use_gpu: Use GPU acceleration if available
        """
        self.history = []
        self.use_local = model_path is not None
        
        if self.use_local:
            # Use local GPU-accelerated model
            from gpt4all import GPT4All
            
            gpu_available = torch.cuda.is_available() and use_gpu
            device = 'gpu' if gpu_available else 'cpu'
            
            if model_path:
                os.environ['GPT4ALL_MODEL_PATH'] = model_path
            
            print(f"🎮 Loading model on {device.upper()}...")
            
            self.model = GPT4All(
                model_name="Phi-3-mini-4k-instruct.Q4_0.gguf",
                model_path=model_path,
                allow_download=True,
                device=device,
                n_threads=2 if device == 'cpu' else None
            )
            
            print(f"✅ Model loaded on {device.upper()}")
        else:
            # Use Ollama API
            self.api_url = "http://localhost:11434/api/chat"
            print("🔗 Using Ollama API")

    def generate_adaptive_response(self, user_query: str, context_chunks: List[str], strategy_instruction: str) -> str:
        """
        Generate response using adaptive strategy and RAG context.
        
        Args:
            user_query: User's question
            context_chunks: Retrieved context from RAG
            strategy_instruction: Pedagogical strategy instruction
        
        Returns:
            str: Generated response
        """
        # Format context
        context_block = "\n\n".join(context_chunks[:3])
        
        # Construct system prompt
        system_prompt = f"""
[ROLE DEFINITION]
You are an Advanced AI Tutor. You adapt your teaching style based on student level.

[CURRENT STRATEGY]
{strategy_instruction}

[KNOWLEDGE SOURCE]
Use ONLY the following context to answer:
{context_block}
"""
        
        if self.use_local:
            # Use local model
            return self._generate_local(user_query, system_prompt)
        else:
            # Use Ollama
            return self._generate_ollama(user_query, system_prompt)
    
    def _generate_local(self, user_query: str, system_prompt: str) -> str:
        """Generate using local GPU model."""
        try:
            prompt = f"{system_prompt}\n\nUser: {user_query}\nAssistant:"
            
            response = self.model.generate(
                prompt,
                max_tokens=512,
                temp=0.3,
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.1
            )
            
            self.history.append({"q": user_query, "a": response})
            return response.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _generate_ollama(self, user_query: str, system_prompt: str) -> str:
        """Generate using Ollama API."""
        try:
            import requests
            
            payload = {
                "model": "llama3",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=180)
            if response.status_code == 200:
                answer = response.json()['message']['content']
                self.history.append({"q": user_query, "a": answer})
                return answer
            else:
                return f"⚠️ Ollama Error: {response.status_code}"
        except Exception as e:
            return f"⚠️ Connection Error: {str(e)}"