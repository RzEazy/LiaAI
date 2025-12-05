"""
Text embedding utilities for RAG implementation.
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np

class Embedder:
    """Text embedder using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedder.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Encode text(s) into embeddings.
        
        Args:
            texts: Single text string or list of text strings
            
        Returns:
            Embedding vector(s)
        """
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = self.model.encode(texts)
        
        # If single text, return single embedding
        if len(embeddings) == 1:
            return embeddings[0].tolist()
        
        return [embedding.tolist() for embedding in embeddings]