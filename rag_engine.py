import os
import re
import requests
import random
import json

class RAGEngine:
    def __init__(self):
        self.chunks = [] 
        # This points to the model downloading in your CMD right now
        self.api_url = "http://localhost:11434/api/chat"
        self.model_name = "llama3" 
        self.quiz_cache = []
        print(f"✅ RAG Engine Initialized (Local Llama 3 - No Internet Needed)")

    def ingest_document(self, pdf_text_list):
        print("⚙️ Processing Document...")
        self.chunks = []
        self.quiz_cache = [] 
        
        for page in pdf_text_list:
            text = page.get('text', '')
            page_num = page.get('page_number', '?')
            
            # Split by double newline to preserve paragraph context
            raw_paragraphs = text.split('\n\n')
            
            for p in raw_paragraphs:
                clean_text = p.strip()
                # Only keep substantial paragraphs
                if len(clean_text) > 30: 
                    self.chunks.append({
                        'text': clean_text,
                        'page': page_num
                    })
                    
        print(f"✅ Indexed {len(self.chunks)} chunks.")
        return True

    def retrieve_context(self, query, k=3):
        if not self.chunks: return []

        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'what', 'how', 'who', '?', 'does', 'it'}
        query_words = set(re.findall(r'\w+', query.lower())) - stop_words
        
        if not query_words: return self.chunks[:k]

        scored_chunks = []
        for chunk in self.chunks:
            score = 0
            chunk_text_lower = chunk['text'].lower()
            for word in query_words:
                if word in chunk_text_lower:
                    score += 1
            if score > 0:
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:k]]

    def _call_local_llm(self, prompt):
        """
        Sends a request to your local Llama 3 model.
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful AI Tutor."},
                {"role": "user", "content": prompt}
            ],
            "stream": False 
        }

        try:
            # 60s timeout because local CPUs can be slower than cloud
            response = requests.post(self.api_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                return data['message']['content'].strip()
            else:
                return f"Error: Ollama status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Error: Ollama is not running! Open CMD and type 'ollama serve'."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def generate_answer(self, query):
        if not self.chunks: return "⚠️ Please upload a document first."

        context_docs = self.retrieve_context(query)
        if not context_docs: context_docs = self.chunks[:3]

        context_text = "\n".join([f"- {d['text']} (Page {d['page']})" for d in context_docs])
        cited_pages = sorted(list(set(str(d['page']) for d in context_docs)))
        citation_str = ", ".join(cited_pages)

        prompt = f"""
        Answer the student's question using ONLY the context below.
        
        CONTEXT:
        {context_text}

        QUESTION: "{query}"
        
        ANSWER:
        """
        
        response_text = self._call_local_llm(prompt)
        return f"{response_text}\n\n*Source: Pages {citation_str}*"

    def generate_quiz_question(self):
        """
        Generates MCQ using Local Llama 3.
        """
        if not self.chunks: return {"error": "Upload a document first!"}

        if self.quiz_cache:
            return self.quiz_cache.pop(0)

        chunk = random.choice(self.chunks)
        
        prompt = f"""
        Create a Multiple Choice Question based on this text.
        
        TEXT: "{chunk['text']}"

        FORMAT (Strict):
        QUESTION: [Question]
        A) [Option]
        B) [Option]
        C) [Option]
        D) [Option]
        ANSWER: [A/B/C/D]
        EXPLANATION: [Why]
        """
        
        response_text = self._call_local_llm(prompt)
        
        # Parse Response
        if "Error" not in response_text:
            lines = response_text.split('\n')
            quiz_data = {'options': []}
            
            for line in lines:
                line = line.strip()
                if line.startswith("QUESTION:"): quiz_data['question'] = line.replace("QUESTION:", "").strip()
                elif line.startswith("A)"): quiz_data['options'].append(line)
                elif line.startswith("B)"): quiz_data['options'].append(line)
                elif line.startswith("C)"): quiz_data['options'].append(line)
                elif line.startswith("D)"): quiz_data['options'].append(line)
                elif line.startswith("ANSWER:"): quiz_data['correct_answer'] = line.replace("ANSWER:", "").strip()
                elif line.startswith("EXPLANATION:"): quiz_data['explanation'] = line.replace("EXPLANATION:", "").strip()
            
            if 'question' in quiz_data and len(quiz_data['options']) >= 2:
                return quiz_data

        return {"error": "AI generated invalid format. Try again."}