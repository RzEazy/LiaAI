import cohere
import platform
from typing import Dict, Any, Optional
from .base_chain import BaseChain
from rag.retriever import Retriever
from rag.vectordb import VectorDB

OS_COMMAND_PROMPT_TEMPLATE = """
Convert the user's request into a precise command based on the OS and relevant documentation.

OS: {os_type}

{examples}

RULES:
- If it's NOT a computer action, reply ONLY with: NO_COMMAND
- No explanation, no extra text, only the command.
- Be precise with the OS-specific syntax
- Use the documentation examples as guidance for proper command structure
- Include necessary flags and options based on the documentation
- For complex commands, prioritize the most commonly used options

User: {user_input}
Command:"""

class OSCommandChain(BaseChain):
    def __init__(self, co_client: cohere.Client):
        self.co = co_client
        self.os_type = self._get_os_type()
        
        # Initialize RAG components
        try:
            vectordb = VectorDB()
            self.retriever = Retriever(vectordb)
        except Exception as e:
            print(f"Warning: Could not initialize RAG components: {e}")
            self.retriever = None
    
    def _get_os_type(self) -> str:
        """Get normalized OS type"""
        system = platform.system().lower()
        if system == 'darwin':
            return 'macOS'
        elif system == 'windows':
            return 'Windows'
        else:  # linux and others
            return 'Linux'
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process OS command input and generate a command
        """
        if context is None:
            context = {}
        
        # Retrieve relevant documentation examples
        examples = ""
        if self.retriever:
            try:
                docs = self.retriever.search(
                    query=user_input,
                    collection="os_commands",
                    n_results=5  # Increase to get more relevant docs
                )
                
                if docs:
                    examples = "RELEVANT COMMAND DOCUMENTATION:\n"
                    for doc in docs:
                        examples += f"{doc['text']}\n\n"
            except Exception as e:
                print(f"Warning: Could not retrieve documentation: {e}")
        
        # If no relevant docs found, use original examples
        if not examples:
            examples = """COMMAND DOCUMENTATION EXAMPLES:
Command: ls (Linux/macOS)
Category: File Operations
Description: List directory contents
Syntax: ls [OPTION]... [FILE]...
Detailed Description: List information about the FILEs (the current directory by default).
Common Options:
  -a, --all: Do not ignore entries starting with .
  -l: Use a long listing format
  -h, --human-readable: Print human readable sizes
Examples:
  ls -la: List all files in long format
  ls -lh: Show files with human-readable sizes

Command: mkdir (Cross-platform)
Category: File Operations
Description: Make directories
Syntax (Linux/macOS): mkdir [OPTION] DIRECTORY...
Syntax (Windows): mkdir [drive:]path
Detailed Description: Create the DIRECTORY(ies), if they do not already exist.
Options (Linux/macOS):
  -p, --parents: Make parent directories as needed
Examples:
  mkdir new_folder: Create a new directory
  mkdir -p path/to/new/folder: Create nested directories

Command: ps (Linux/macOS)
Category: Process Management
Description: Report a snapshot of the current processes
Syntax: ps [options]
Common Options:
  aux: List all processes (BSD syntax)
  -ef: Full format listing (POSIX syntax)
Examples:
  ps aux: Show all running processes
  ps -ef: Show full process list

Command: grep (Linux/macOS)
Category: Text Processing
Description: Search for patterns in files
Syntax: grep [OPTIONS] PATTERN [FILE...]
Common Options:
  -r, --recursive: Read all files under each directory recursively
  -i, --ignore-case: Ignore case distinctions
Examples:
  grep 'error' logfile.txt: Search for 'error' in logfile
  grep -r 'function' ./src: Recursively search for 'function'"""

        # Construct prompt
        prompt = OS_COMMAND_PROMPT_TEMPLATE.format(
            os_type=self.os_type,
            user_input=user_input,
            examples=examples
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
                        "command": None
                    }
                }
            
            return {
                "response": command,
                "metadata": {
                    "chain": "os_command",
                    "command": command,
                    "os_type": self.os_type
                }
            }
        except Exception as e:
            return {
                "response": None,
                "metadata": {
                    "chain": "os_command",
                    "error": str(e)
                }
            }
    
    def _clean_command(self, command: str) -> str:
        """Clean and normalize the command"""
        # Remove any markdown formatting
        command = command.replace('`', '')
        
        # Remove OS prefixes if they accidentally got included
        prefixes = ['Windows:', 'Linux:', 'macOS:', 'Command:']
        for prefix in prefixes:
            if command.startswith(prefix):
                command = command[len(prefix):].strip()
        
        # Remove trailing/leading whitespace
        command = command.strip()
        
        return command