"""
Document retrieval component for RAG implementation.
"""
from typing import List, Dict, Any, Optional
from .vectordb import VectorDB

class Retriever:
    """Retriever for finding relevant documents using vector search."""
    
    def __init__(self, vectordb: VectorDB):
        """
        Initialize the retriever.
        
        Args:
            vectordb: VectorDB instance for document storage and retrieval
        """
        self.vectordb = vectordb
    
    def search(self, query: str, collection: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Query text
            collection: Collection name to search in
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            results = self.vectordb.search(
                collection_name=collection,
                query=query,
                n_results=n_results
            )
            
            # Format results
            documents = []
            for i in range(len(results['ids'][0])):
                documents.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return documents
        except Exception as e:
            print(f"Search error: {e}")
            return []