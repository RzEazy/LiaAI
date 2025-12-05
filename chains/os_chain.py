"""
Enhanced OS Command Chain with TLDR-based RAG

REPLACE: chains/os_chain.py
"""
import cohere
import platform
from typing import Dict, Any, Optional
from chains.base_chain import BaseChain
from rag.retriever import Retriever
from rag.vectordb import VectorDB

OS_COMMAND_PROMPT_TEMPLATE = """
You are an expert system administrator. Convert the user's request into the correct command for their operating system.

CURRENT OS: {os_type}

{retrieved_docs}

CRITICAL RULES:
1. If the request is NOT a system command or operation, respond ONLY with: NO_COMMAND
2. Return ONLY the command - no explanations, no markdown, no extra text
3. Use the TLDR documentation above as your primary reference
4. Match the command syntax exactly to the user's OS
5. Use the most appropriate flags/options from the examples
6. If multiple approaches exist, choose the simplest and safest one

COMMAND GUIDELINES:
- For file operations: prefer safer options (e.g., -i for interactive)
- For listings: use human-readable formats when available (-h)
- For searches: use recursive options when context suggests it
- For network: use standard, well-supported tools
- Always validate paths are reasonable (no system directories without clear intent)

User Request: {user_input}

Command:"""


class OSCommandChain(BaseChain):
    """Enhanced OS Command Chain with TLDR-based RAG"""
    
    def __init__(self, co_client: cohere.Client):
        self.co = co_client
        self.os_type = self._get_os_type()
        
        # Initialize RAG components
        try:
            vectordb = VectorDB()
            self.retriever = Retriever(vectordb)
            self.rag_available = True
        except Exception as e:
            print(f"Warning: Could not initialize RAG components: {e}")
            self.retriever = None
            self.rag_available = False
    
    def _get_os_type(self) -> str:
        """Get normalized OS type matching TLDR platforms"""
        system = platform.system().lower()
        if system == 'darwin':
            return 'macOS'
        elif system == 'windows':
            return 'Windows'
        else:  # linux and others
            return 'Linux'
    
    def _get_platform_priority(self) -> list:
        """Get platform search priority based on current OS"""
        os_map = {
            'macOS': ['osx', 'common', 'linux'],
            'Linux': ['linux', 'common'],
            'Windows': ['windows', 'common']
        }
        return os_map.get(self.os_type, ['common'])
    
    def _retrieve_relevant_docs(self, user_input: str, n_results: int = 5) -> str:
        """
        Retrieve relevant TLDR documentation for the user's request.
        
        Args:
            user_input: User's natural language request
            n_results: Number of documents to retrieve
            
        Returns:
            Formatted documentation string
        """
        if not self.retriever:
            return self._get_fallback_examples()
        
        try:
            # Search for relevant commands
            docs = self.retriever.search(
                query=user_input,
                collection="os_commands",
                n_results=n_results
            )
            
            if not docs:
                return self._get_fallback_examples()
            
            # Filter by platform preference
            platform_priority = self._get_platform_priority()
            
            # Sort docs by platform priority
            def get_platform_score(doc):
                platform = doc.get('metadata', {}).get('platform', 'common')
                if platform in platform_priority:
                    return platform_priority.index(platform)
                return len(platform_priority)
            
            docs.sort(key=get_platform_score)
            
            # Format documentation
            formatted = "RELEVANT COMMAND DOCUMENTATION (from tldr-pages):\n\n"
            
            for i, doc in enumerate(docs[:3], 1):  # Show top 3 most relevant
                formatted += f"[Document {i}]\n"
                formatted += doc['text']
                formatted += "\n" + "="*60 + "\n\n"
            
            return formatted
            
        except Exception as e:
            print(f"Warning: Could not retrieve documentation: {e}")
            return self._get_fallback_examples()
    
    def _get_fallback_examples(self) -> str:
        """Fallback examples when RAG is unavailable"""
        return """BASIC COMMAND REFERENCE:

File Operations:
- List files: ls (Linux/macOS) or dir (Windows)
- Create folder: mkdir folder_name
- Remove file: rm file.txt (Linux/macOS) or del file.txt (Windows)
- Copy file: cp source dest (Linux/macOS) or copy source dest (Windows)

System Info:
- Disk usage: df -h (Linux/macOS) or wmic logicaldisk get size,freespace (Windows)
- Memory: free -h (Linux) or Get-Process (Windows PowerShell)
- Current directory: pwd (Linux/macOS) or cd (Windows)

Network:
- Test connectivity: ping hostname
- Show IP: ip addr (Linux) or ipconfig (Windows)
"""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process OS command input and generate a command
        
        Args:
            user_input: User's natural language request
            context: Additional context (memory, previous interactions)
            
        Returns:
            Dictionary with response (command) and metadata
        """
        if context is None:
            context = {}
        
        # Retrieve relevant TLDR documentation
        retrieved_docs = self._retrieve_relevant_docs(user_input)
        
        # Construct prompt
        prompt = OS_COMMAND_PROMPT_TEMPLATE.format(
            os_type=self.os_type,
            user_input=user_input,
            retrieved_docs=retrieved_docs
        )
        
        try:
            response = self.co.chat(
                model="command-a-03-2025",
                message=prompt,
                temperature=0.1  # Low temperature for consistent command generation
            )
            
            command = response.text.strip()
            
            # Clean up the command
            command = self._clean_command(command)
            
            if command == "NO_COMMAND" or not command:
                return {
                    "response": None,
                    "metadata": {
                        "chain": "os_command",
                        "command": None,
                        "rag_used": self.rag_available
                    }
                }
            
            return {
                "response": command,
                "metadata": {
                    "chain": "os_command",
                    "command": command,
                    "os_type": self.os_type,
                    "rag_used": self.rag_available
                }
            }
        except Exception as e:
            return {
                "response": None,
                "metadata": {
                    "chain": "os_command",
                    "error": str(e),
                    "rag_used": self.rag_available
                }
            }
    
    def _clean_command(self, command: str) -> str:
        """Clean and normalize the command"""
        # Remove any markdown formatting
        command = command.replace('`', '')
        command = command.replace('```', '')
        
        # Remove OS prefixes if they accidentally got included
        prefixes = ['Windows:', 'Linux:', 'macOS:', 'Command:', 'Output:', '$', '#']
        for prefix in prefixes:
            if command.startswith(prefix):
                command = command[len(prefix):].strip()
        
        # Remove trailing/leading whitespace
        command = command.strip()
        
        # Remove any explanatory text after the command
        # (keep only first line if multiple lines)
        if '\n' in command:
            command = command.split('\n')[0].strip()
        
        return command