"""
Ingest complete osquery documentation into the vector database.
Fetches ALL tables from all spec directories (specs/, specs/linux/, specs/darwin/, 
specs/windows/, specs/posix/, specs/utility/, etc.)
"""
import json
import requests
from typing import List, Dict, Any
import sys
import os
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vectordb import VectorDB

# All spec directories to fetch from
SPEC_DIRS = [
    'specs',
    'specs/darwin',
    'specs/linux', 
    'specs/windows',
    'specs/posix',
    'specs/utility',
    'specs/yara',
    'specs/sleuthkit',
    'specs/smart',
    'specs/lldp',
    'specs/ssh',
    'specs/applications'
]

def fetch_all_table_specs() -> List[Dict[str, Any]]:
    """
    Fetch ALL osquery table specs from GitHub across all directories.
    
    Returns:
        List of table dictionaries with parsed data
    """
    all_tables = []
    
    for spec_dir in SPEC_DIRS:
        print(f"Fetching tables from {spec_dir}...")
        try:
            # Get list of files in this directory
            url = f"https://api.github.com/repos/osquery/osquery/contents/{spec_dir}"
            response = requests.get(url)
            
            if response.status_code == 404:
                print(f"  Directory {spec_dir} not found, skipping...")
                continue
                
            response.raise_for_status()
            files = response.json()
            
            # Filter for .table files
            table_files = [f for f in files if isinstance(f, dict) and f.get('name', '').endswith('.table')]
            print(f"  Found {len(table_files)} table files")
            
            # Fetch and parse each table
            for table_file in table_files:
                table_name = table_file['name'].replace('.table', '')
                try:
                    # Fetch the table spec
                    spec_response = requests.get(table_file['download_url'])
                    spec_response.raise_for_status()
                    spec_content = spec_response.text
                    
                    # Parse the table spec
                    table_data = parse_table_spec(table_name, spec_content, spec_dir)
                    if table_data:
                        all_tables.append(table_data)
                        print(f"  ✓ Parsed {table_name}")
                except Exception as e:
                    print(f"  ✗ Error parsing {table_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"  Error fetching directory {spec_dir}: {e}")
            continue
    
    return all_tables

def parse_table_spec(table_name: str, spec_content: str, spec_dir: str) -> Dict[str, Any]:
    """
    Parse a table spec file into structured data.
    
    Args:
        table_name: Name of the table
        spec_content: Content of the .table spec file
        spec_dir: Directory the spec came from (for platform info)
        
    Returns:
        Dictionary with table information
    """
    table = {
        'name': table_name,
        'description': '',
        'columns': [],
        'platform': extract_platform(spec_dir),
        'examples': []
    }
    
    # Extract description
    desc_match = re.search(r'description\s*\(\s*["\']([^"\']+)["\']', spec_content, re.DOTALL)
    if desc_match:
        table['description'] = desc_match.group(1).strip()
    
    # Extract extended description if available
    ext_desc_match = re.search(r'extended_description\s*\(\s*"""([^"]+)"""', spec_content, re.DOTALL)
    if ext_desc_match:
        table['extended_description'] = ext_desc_match.group(1).strip()
    
    # Extract platforms
    platform_match = re.search(r'platform\s*=\s*["\']([^"\']+)["\']', spec_content)
    if platform_match:
        table['specified_platform'] = platform_match.group(1)
    
    # Extract columns from schema
    schema_match = re.search(r'schema\s*\(\s*\[(.*?)\]\s*\)', spec_content, re.DOTALL)
    if schema_match:
        schema_content = schema_match.group(1)
        # Parse column definitions - handles various formats
        column_pattern = r'Column\s*\(\s*["\']([^"\']+)["\'],\s*(\w+)(?:,\s*["\']([^"\']*)["\'])?'
        columns = re.findall(column_pattern, schema_content)
        
        for col_name, col_type, col_desc in columns:
            table['columns'].append({
                'name': col_name,
                'type': col_type,
                'description': col_desc if col_desc else ''
            })
    
    # Extract example queries
    examples_match = re.search(r'examples\s*\(\s*\[(.*?)\]\s*\)', spec_content, re.DOTALL)
    if examples_match:
        examples_content = examples_match.group(1)
        # Extract quoted strings as examples
        example_queries = re.findall(r'["\']([^"\']+)["\']', examples_content)
        table['examples'] = example_queries
    
    return table

def extract_platform(spec_dir: str) -> str:
    """Extract platform from spec directory path."""
    if 'darwin' in spec_dir:
        return 'macOS'
    elif 'linux' in spec_dir:
        return 'Linux'
    elif 'windows' in spec_dir:
        return 'Windows'
    elif 'posix' in spec_dir:
        return 'POSIX'
    else:
        return 'Cross-platform'

def create_documents(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create document format for embedding.
    
    Args:
        tables: List of table dictionaries
        
    Returns:
        List of document dictionaries for vector DB
    """
    documents = []
    
    for table in tables:
        # Create comprehensive document text
        doc_text = f"Table: {table['name']}\n"
        doc_text += f"Platform: {table.get('platform', 'Unknown')}\n"
        
        if table.get('specified_platform'):
            doc_text += f"Specified Platform: {table['specified_platform']}\n"
            
        doc_text += f"Description: {table['description']}\n"
        
        if table.get('extended_description'):
            doc_text += f"\nExtended Description:\n{table['extended_description']}\n"
        
        if table['columns']:
            doc_text += "\nColumns:\n"
            for col in table['columns']:
                col_text = f"  - {col['name']} ({col['type']})"
                if col.get('description'):
                    col_text += f": {col['description']}"
                doc_text += col_text + "\n"
        
        # Add example queries
        if table.get('examples'):
            doc_text += "\nExample Queries:\n"
            for i, example in enumerate(table['examples'], 1):
                doc_text += f"  {i}. {example}\n"
        
        # Create metadata
        metadata = {
            "table": table['name'],
            "platform": table.get('platform', 'Unknown'),
            "source": "osquery_schema",
            "num_columns": len(table['columns'])
        }
        
        if table.get('specified_platform'):
            metadata['specified_platform'] = table['specified_platform']
        
        documents.append({
            "text": doc_text,
            "metadata": metadata
        })
    
    return documents

def ingest_complete_schema(vectordb: VectorDB):
    """
    Ingest complete osquery schema into vector database.
    
    Args:
        vectordb: VectorDB instance
    """
    print("="*60)
    print("Fetching COMPLETE osquery schema from GitHub")
    print("="*60)
    
    tables = fetch_all_table_specs()
    
    if not tables:
        print("❌ Failed to fetch any tables")
        return
    
    print(f"\n{'='*60}")
    print(f"✓ Successfully fetched {len(tables)} tables")
    print(f"{'='*60}\n")
    
    # Show platform breakdown
    platform_counts = {}
    for table in tables:
        platform = table.get('platform', 'Unknown')
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    print("Platform breakdown:")
    for platform, count in sorted(platform_counts.items()):
        print(f"  {platform}: {count} tables")
    
    print(f"\nCreating documents for vector database...")
    documents = create_documents(tables)
    
    # Prepare for insertion
    doc_texts = [doc['text'] for doc in documents]
    doc_metadatas = [doc['metadata'] for doc in documents]
    doc_ids = [f"osquery_{i}" for i in range(len(documents))]
    
    print(f"\nIngesting {len(documents)} documents into vector database...")
    try:
        vectordb.add_documents(
            collection_name="osquery_docs",
            documents=doc_texts,
            metadatas=doc_metadatas,
            ids=doc_ids
        )
        print(f"\n{'='*60}")
        print(f"✓ Ingestion complete! {len(documents)} documents added")
        print(f"{'='*60}")
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")

if __name__ == "__main__":
    # Initialize vector database
    db = VectorDB()
    
    # Create collection if it doesn't exist
    try:
        db.create_collection("osquery_docs")
        print("Created new collection 'osquery_docs'")
    except Exception as e:
        print(f"Collection already exists or error: {e}")
    
    # Ingest complete schema
    ingest_complete_schema(db)