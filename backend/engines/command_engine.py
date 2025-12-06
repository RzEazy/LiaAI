import subprocess
import platform
from typing import Tuple

class CommandEngine:
    def __init__(self):
        self.os_type = platform.system().lower()  # windows / linux / darwin (mac)
    
    def execute_command(self, command: str) -> Tuple[str, str]:
        """
        Execute an OS command and return results
        
        Returns:
            Tuple of (output, error_message)
        """
        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip() if result.stdout else "Done.", ""
            else:
                return "", result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            return "", "Command timed out"
        except Exception as e:
            return "", f"Execution error: {str(e)}"