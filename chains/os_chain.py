import cohere
import platform
from typing import Dict, Any, Optional
from .base_chain import BaseChain

OS_COMMAND_PROMPT_TEMPLATE = """
Convert the user's request into a command depending on the OS.

OS: {os_type}

RULES:
- If it's NOT a computer action, reply ONLY with: NO_COMMAND
- No explanation, no extra text, only the command.

Examples:
User: make a folder called test
Windows: mkdir test
Linux: mkdir test
macOS: mkdir test

User: open chrome
Windows: start chrome
Linux: google-chrome &
macOS: open -a "Google Chrome"

User: {user_input}
Command:"""

class OSCommandChain(BaseChain):
    def __init__(self, co_client: cohere.Client):
        self.co = co_client
        self.os_type = platform.system().lower()  # windows / linux / darwin (mac)
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process OS command input and generate a command
        """
        if context is None:
            context = {}
        
        # Construct prompt
        prompt = OS_COMMAND_PROMPT_TEMPLATE.format(
            os_type=self.os_type,
            user_input=user_input
        )
        
        try:
            response = self.co.chat(
                model="command-a-03-2025",
                message=prompt
            )
            
            command = response.text.strip()
            
            if command == "NO_COMMAND":
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
                    "command": command
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