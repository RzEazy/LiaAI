"""
ChromaDB wrapper for vector storage and retrieval.
"""
import chromadb
import os
from typing import List, Dict, Any, Optional

class VectorDB:
    """Wrapper for ChromaDB vector database operations."""
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        """
        Initialize the vector database.
        
        Args:
            persist_directory: Path to store the persistent database
        """
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )
        
    def create_collection(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Create a new collection in the database.
        
        Args:
            name: Name of the collection
            metadata: Optional metadata for the collection
        """
        return self.client.create_collection(name=name, metadata=metadata)
    
    def get_collection(self, name: str):
        """
        Get an existing collection.
        
        Args:
            name: Name of the collection
            
        Returns:
            Collection object
        """
        return self.client.get_collection(name=name)
    
    def add_documents(self, collection_name: str, documents: List[str], 
                     metadatas: Optional[List[Dict[str, Any]]] = None, 
                     ids: Optional[List[str]] = None):
        """
        Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
        """
        collection = self.get_collection(collection_name)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids or [f"doc_{i}" for i in range(len(documents))]
        )
    
    def search(self, collection_name: str, query: str, n_results: int = 5):
        """
        Search for relevant documents.
        
        Args:
            collection_name: Name of the collection to search
            query: Query text
            n_results: Number of results to return
            
        Returns:
            Search results
        """
        collection = self.get_collection(collection_name)
        return collection.query(
            query_texts=[query],
            n_results=n_results
        )
    
    def delete_collection(self, name: str):
        """
        Delete a collection.
        
        Args:
            name: Name of the collection to delete
        """
        self.client.delete_collection(name=name)