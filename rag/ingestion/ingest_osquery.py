"""
Ingest osquery documentation into the vector database.
"""
import json
import requests
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vectordb import VectorDB

def fetch_osquery_schema(limit: int = 50) -> Dict[str, Any]:
    """
    Fetch osquery schema from GitHub specs.
    
    Returns:
        Schema data as dictionary
    """
    try:
        # Get list of table specs from GitHub
        response = requests.get("https://api.github.com/repos/osquery/osquery/contents/specs")
        response.raise_for_status()
        files = response.json()
        
        tables = []
        table_files = [f for f in files if f['name'].endswith('.table')]
        
        # Fetch and parse tables (up to limit)
        for table_file in table_files[:limit]:
            table_name = table_file['name'].replace('.table', '')
            # Fetch the table spec
            spec_response = requests.get(table_file['download_url'])
            spec_response.raise_for_status()
            spec_content = spec_response.text
            
            # Parse the table spec
            table_data = parse_table_spec(table_name, spec_content)
            if table_data:
                tables.append(table_data)
        
        return {'tables': tables}
    except Exception as e:
        print(f"Error fetching schema: {e}")
        return {}

def parse_table_spec(table_name: str, spec_content: str) -> Dict[str, Any]:
    """Parse a table spec file into structured data."""
    table = {
        'name': table_name,
        'description': '',
        'columns': []
    }
    
    # Extract description
    import re
    desc_match = re.search(r'description\("([^"]+)"\)', spec_content)
    if desc_match:
        table['description'] = desc_match.group(1)
    
    # Extract columns from schema
    schema_match = re.search(r'schema\(\[(.*?)\]\)', spec_content, re.DOTALL)
    if schema_match:
        schema_content = schema_match.group(1)
        # Parse column definitions
        column_pattern = r'Column\("([^"]+)",\s*([^,]+),\s*"([^"]+)"[^\)]*\)'
        columns = re.findall(column_pattern, schema_content)
        
        for col_name, col_type, col_desc in columns:
            table['columns'].append({
                'name': col_name,
                'type': col_type,
                'description': col_desc
            })
    
    return table

def parse_table_documents(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse schema into document format for embedding.
    
    Args:
        schema: Osquery schema data
        
    Returns:
        List of document dictionaries
    """
    documents = []
    
    for table in schema.get('tables', []):
        # Create document text
        doc_text = f"Table: {table['name']}\n"
        doc_text += f"Description: {table['description']}\n"
        doc_text += "Columns:\n"
        
        columns = []
        for col in table.get('columns', []):
            col_text = f"  - {col['name']} ({col['type']}): {col['description']}"
            columns.append(col_text)
        
        doc_text += "\n".join(columns)
        
        # Create document metadata
        metadata = {
            "table": table['name'],
            "category": table.get('category', ''),
            "source": "osquery_schema"
        }
        
        documents.append({
            "text": doc_text,
            "metadata": metadata
        })
    
    return documents

def ingest_osquery_schema(vectordb: VectorDB, limit: int = 50):
    """
    Ingest osquery schema into vector database.
    
    Args:
        vectordb: VectorDB instance
        limit: Maximum number of tables to ingest
    """
    print("Fetching osquery schema from GitHub specs...")
    schema = fetch_osquery_schema(limit=limit)
    
    if not schema:
        print("Failed to fetch schema")
        return
    
    print(f"Parsing {len(schema.get('tables', []))} tables...")
    documents = parse_table_documents(schema)
    
    # Limit documents if specified
    if limit and len(documents) > limit:
        documents = documents[:limit]
        print(f"Limited to {limit} tables")
    
    # Prepare for insertion
    doc_texts = [doc['text'] for doc in documents]
    doc_metadatas = [doc['metadata'] for doc in documents]
    doc_ids = [f"osquery_{i}" for i in range(len(documents))]
    
    print(f"Ingesting {len(documents)} documents...")
    try:
        vectordb.add_documents(
            collection_name="osquery_docs",
            documents=doc_texts,
            metadatas=doc_metadatas,
            ids=doc_ids
        )
        print("Ingestion complete!")
    except Exception as e:
        print(f"Error during ingestion: {e}")

if __name__ == "__main__":
    # Initialize vector database
    db = VectorDB()
    
    # Create collection if it doesn't exist
    try:
        db.create_collection("osquery_docs")
    except Exception:
        print("Collection already exists or error creating collection")
    
    # Ingest schema
    ingest_osquery_schema(db, limit=50)