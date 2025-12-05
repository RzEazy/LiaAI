"""
Ingest tldr-pages command documentation into the vector database.
This replaces hardcoded command examples with community-maintained documentation.

REPLACE: rag/ingestion/ingest_commands.py
"""
import json
import requests
import os
from typing import List, Dict, Any
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vectordb import VectorDB


class TLDRIngester:
    """Ingests tldr-pages documentation into vector database"""
    
    # GitHub API base URL for tldr-pages
    TLDR_API_BASE = "https://api.github.com/repos/tldr-pages/tldr/contents/pages"
    TLDR_RAW_BASE = "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages"
    
    # Platform directories to ingest
    PLATFORMS = ["common", "linux", "osx", "windows"]
    
    def __init__(self, vectordb: VectorDB):
        self.vectordb = vectordb
        self.session = requests.Session()
        
    def fetch_command_list(self, platform: str) -> List[Dict[str, str]]:
        """
        Fetch list of command files for a platform.
        
        Args:
            platform: Platform name (common, linux, osx, windows)
            
        Returns:
            List of command file info
        """
        try:
            url = f"{self.TLDR_API_BASE}/{platform}"
            response = self.session.get(url)
            response.raise_for_status()
            
            files = response.json()
            return [
                {
                    "name": f["name"].replace(".md", ""),
                    "download_url": f["download_url"],
                    "platform": platform
                }
                for f in files if f["name"].endswith(".md")
            ]
        except Exception as e:
            print(f"Error fetching {platform} command list: {e}")
            return []
    
    def fetch_command_content(self, download_url: str) -> str:
        """
        Fetch the markdown content of a command page.
        
        Args:
            download_url: URL to download the markdown file
            
        Returns:
            Markdown content as string
        """
        try:
            response = self.session.get(download_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching command content: {e}")
            return ""
    
    def parse_tldr_markdown(self, content: str, command_name: str, platform: str) -> Dict[str, Any]:
        """
        Parse tldr markdown format into structured document.
        
        TLDR format:
        # command-name
        
        > Description of the command.
        > More info: <url>
        
        - Description of example:
        
        `command example`
        
        Args:
            content: Markdown content
            command_name: Name of the command
            platform: Platform (common, linux, osx, windows)
            
        Returns:
            Structured document dictionary
        """
        lines = content.strip().split('\n')
        
        doc = {
            "command": command_name,
            "platform": platform,
            "description": "",
            "more_info": "",
            "examples": []
        }
        
        # Parse description (lines starting with >)
        description_lines = []
        more_info_line = ""
        for line in lines:
            if line.startswith('> '):
                desc_text = line[2:].strip()
                if desc_text.startswith('More info:'):
                    more_info_line = desc_text
                else:
                    description_lines.append(desc_text)
        
        doc["description"] = " ".join(description_lines)
        doc["more_info"] = more_info_line
        
        # Parse examples
        i = 0
        while i < len(lines):
            line = lines[i]
            # Example description starts with "- "
            if line.startswith('- '):
                example_desc = line[2:].strip()
                # Next non-empty line should be the command
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines) and lines[i].startswith('`') and lines[i].endswith('`'):
                    example_cmd = lines[i].strip('`')
                    doc["examples"].append({
                        "description": example_desc,
                        "command": example_cmd
                    })
            i += 1
        
        return doc
    
    def format_document_text(self, doc: Dict[str, Any]) -> str:
        """
        Format parsed document into text for embedding.
        
        Args:
            doc: Parsed document dictionary
            
        Returns:
            Formatted text string
        """
        text = f"Command: {doc['command']}\n"
        text += f"Platform: {doc['platform']}\n"
        text += f"Description: {doc['description']}\n"
        
        if doc['more_info']:
            text += f"{doc['more_info']}\n"
        
        if doc['examples']:
            text += "\nExamples:\n"
            for example in doc['examples']:
                text += f"  - {example['description']}\n"
                text += f"    {example['command']}\n"
        
        return text
    
    def ingest_platform(self, platform: str, limit: int = None) -> int:
        """
        Ingest all commands from a platform.
        
        Args:
            platform: Platform name
            limit: Maximum number of commands to ingest (None = all)
            
        Returns:
            Number of commands ingested
        """
        print(f"\n📥 Ingesting {platform} commands...")
        
        # Fetch command list
        command_list = self.fetch_command_list(platform)
        if not command_list:
            print(f"  No commands found for {platform}")
            return 0
        
        # Apply limit if specified
        if limit:
            command_list = command_list[:limit]
        
        print(f"  Found {len(command_list)} commands")
        
        documents = []
        metadatas = []
        ids = []
        
        for i, cmd_info in enumerate(command_list):
            if (i + 1) % 10 == 0:
                print(f"  Processing {i + 1}/{len(command_list)}...")
            
            # Fetch and parse command content
            content = self.fetch_command_content(cmd_info["download_url"])
            if not content:
                continue
            
            parsed_doc = self.parse_tldr_markdown(
                content,
                cmd_info["name"],
                cmd_info["platform"]
            )
            
            # Format for vector DB
            doc_text = self.format_document_text(parsed_doc)
            documents.append(doc_text)
            
            metadatas.append({
                "command": cmd_info["name"],
                "platform": cmd_info["platform"],
                "source": "tldr-pages"
            })
            
            ids.append(f"tldr_{platform}_{cmd_info['name']}")
        
        # Ingest into vector database
        if documents:
            try:
                self.vectordb.add_documents(
                    collection_name="os_commands",
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"  ✅ Ingested {len(documents)} commands from {platform}")
                return len(documents)
            except Exception as e:
                print(f"  ❌ Error ingesting {platform}: {e}")
                return 0
        
        return 0
    
    def ingest_all(self, limit_per_platform: int = None) -> Dict[str, int]:
        """
        Ingest commands from all platforms.
        
        Args:
            limit_per_platform: Limit commands per platform (None = all)
            
        Returns:
            Dictionary of platform -> count ingested
        """
        print("=" * 70)
        print("🚀 TLDR-PAGES INGESTION STARTING")
        print("=" * 70)
        
        results = {}
        total = 0
        
        for platform in self.PLATFORMS:
            count = self.ingest_platform(platform, limit=limit_per_platform)
            results[platform] = count
            total += count
        
        print("\n" + "=" * 70)
        print("📊 INGESTION SUMMARY")
        print("=" * 70)
        for platform, count in results.items():
            print(f"  {platform:10s}: {count:4d} commands")
        print("-" * 70)
        print(f"  {'TOTAL':10s}: {total:4d} commands")
        print("=" * 70)
        
        return results


def ingest_command_docs(vectordb: VectorDB):
    """
    Main function to ingest TLDR documentation.
    Replaces the old hardcoded command ingestion.
    
    Args:
        vectordb: VectorDB instance
    """
    ingester = TLDRIngester(vectordb)
    
    # Ingest all platforms
    # Set limit_per_platform=50 to limit for testing
    # Set limit_per_platform=None to ingest all commands
    results = ingester.ingest_all(limit_per_platform=None)
    
    print("\n✨ Ingestion complete!")
    print("\nThe os_commands collection now contains community-maintained")
    print("documentation from tldr-pages instead of hardcoded examples.")


if __name__ == "__main__":
    # Initialize vector database
    db = VectorDB()
    
    # Create collection if it doesn't exist
    try:
        db.create_collection("os_commands")
        print("✅ Created new 'os_commands' collection")
    except Exception:
        print("⚠️  Collection already exists, will add to it")
    
    # Ingest TLDR commands
    ingest_command_docs(db)