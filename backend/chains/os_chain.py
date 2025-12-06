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
- Be precise with the OS-specific syntax

Examples:
User: make a folder called test
Windows: mkdir test
Linux: mkdir test
macOS: mkdir test

User: list files in current directory
Windows: dir
Linux: ls -la
macOS: ls -la

User: show current directory
Windows: cd
Linux: pwd
macOS: pwd

User: show me the current path
Windows: cd
Linux: pwd
macOS: pwd

User: how much disk space is free?
Windows: wmic logicaldisk get size,freespace,caption
Linux: df -h
macOS: df -h

User: display RAM usage
Windows: systeminfo | findstr /C:"Total Physical Memory" /C:"Available Physical Memory"
Linux: free -h
macOS: vm_stat

User: check memory usage
Windows: systeminfo | findstr Memory
Linux: free -h
macOS: vm_stat

User: show disk usage
Windows: wmic logicaldisk get size,freespace,caption
Linux: df -h
macOS: df -h

User: what's my IP address?
Windows: ipconfig
Linux: ip addr show
macOS: ifconfig

User: show network interfaces
Windows: ipconfig /all
Linux: ip link show
macOS: ifconfig

User: display environment variables
Windows: set
Linux: printenv
macOS: printenv

User: show running processes
Windows: tasklist
Linux: ps aux
macOS: ps aux

User: open chrome
Windows: start chrome
Linux: google-chrome &
macOS: open -a "Google Chrome"

User: ping google.com
Windows: ping google.com
Linux: ping -c 4 google.com
macOS: ping -c 4 google.com

User: show system information
Windows: systeminfo
Linux: uname -a
macOS: uname -a

User: create a file called test.txt
Windows: type nul > test.txt
Linux: touch test.txt
macOS: touch test.txt

User: delete file test.txt
Windows: del test.txt
Linux: rm test.txt
macOS: rm test.txt

User: copy file.txt to backup.txt
Windows: copy file.txt backup.txt
Linux: cp file.txt backup.txt
macOS: cp file.txt backup.txt

User: show contents of file.txt
Windows: type file.txt
Linux: cat file.txt
macOS: cat file.txt

User: search for "error" in log.txt
Windows: findstr "error" log.txt
Linux: grep "error" log.txt
macOS: grep "error" log.txt

User: who am I
Windows: whoami
Linux: whoami
macOS: whoami

User: show current user
Windows: echo %USERNAME%
Linux: whoami
macOS: whoami

User: {user_input}
Command:"""

class OSCommandChain(BaseChain):
    def __init__(self, co_client: cohere.Client):
        self.co = co_client
        self.os_type = self._get_os_type()
    
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
        
        # Construct prompt
        prompt = OS_COMMAND_PROMPT_TEMPLATE.format(
            os_type=self.os_type,
            user_input=user_input
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