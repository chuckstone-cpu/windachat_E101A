"""
RAG Engine with GPU-accelerated embeddings
Uses GPU for faster embedding generation
"""

import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
import torch


class RAGEngine:
    """
    RAG engine with GPU support for embeddings.
    Embeddings run on GPU if available (saves RAM, faster processing).
    """
    
    def __init__(self, pdf_path):
        """
        Initialize RAG engine with GPU support.
        
        Args:
            pdf_path (str): Path to PDF file
        """
        self.pdf_path = pdf_path
        self.text_chunks = []
        self.embeddings = None
        self.index = None
        self.model = None
        
        # Check GPU availability
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🔍 RAG Engine: Using {self.device.upper()} for embeddings")
        
        # Load PDF and build index
        self._load_pdf()
        self._chunk_text()
        self._build_index()
    
    def _load_pdf(self):
        """Load text from PDF."""
        self.raw_text = ""
        
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                self.raw_text += page.extract_text() + "\n"
        
        self.raw_text = re.sub(r'\s+', ' ', self.raw_text).strip()
    
    def _chunk_text(self):
        """Split text into chunks."""
        words = self.raw_text.split()
        chunk_size = 500
        overlap = 50
        
        self.text_chunks = []
        start_idx = 0
        
        while start_idx < len(words):
            end_idx = min(start_idx + chunk_size, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_text = ' '.join(chunk_words)
            
            if chunk_text.strip():
                self.text_chunks.append(chunk_text)
            
            start_idx += chunk_size - overlap
            
            if end_idx >= len(words):
                break
    
    def _build_index(self):
        """
        Build FAISS index with GPU-accelerated embeddings.
        Embeddings generated on GPU, then moved to CPU for FAISS.
        """
        # Load model on GPU if available
        print(f"📥 Loading embedding model on {self.device.upper()}...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
        
        # Generate embeddings on GPU
        print(f"🔄 Generating embeddings for {len(self.text_chunks)} chunks...")
        self.embeddings = self.model.encode(
            self.text_chunks,
            convert_to_numpy=True,
            show_progress_bar=False,
            device=self.device  # Use GPU
        )
        
        # Get embedding dimension
        dimension = self.embeddings.shape[1]
        
        # Create FAISS index on CPU (FAISS-GPU requires more setup)
        self.index = faiss.IndexFlatL2(dimension)
        
        # Normalize embeddings
        embeddings_normalized = self.embeddings.astype('float32')
        faiss.normalize_L2(embeddings_normalized)
        
        # Add to index
        self.index.add(embeddings_normalized)
        
        if self.device == 'cuda':
            vram_used = torch.cuda.memory_allocated() / 1024**2
            print(f"✅ Embeddings ready! Using ~{vram_used:.0f}MB VRAM")
        else:
            print("✅ Embeddings ready (CPU mode)")
    
    def retrieve(self, query, k=5):
        """
        Retrieve top-k relevant chunks using GPU-accelerated search.
        
        Args:
            query (str): Search query
            k (int): Number of chunks to retrieve
        
        Returns:
            list: Top-k relevant text chunks
        """
        # Generate query embedding on GPU
        query_embedding = self.model.encode([query], convert_to_numpy=True, device=self.device)
        
        # Normalize
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        k = min(k, len(self.text_chunks))
        distances, indices = self.index.search(query_embedding, k)
        
        # Retrieve chunks
        retrieved_chunks = [self.text_chunks[idx] for idx in indices[0]]
        
        return retrieved_chunks