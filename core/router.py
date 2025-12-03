import cohere
from enum import Enum

class Intent(Enum):
    CHAT = "chat"
    OS_COMMAND = "os_command"
    OSQUERY = "osquery"
    UNKNOWN = "unknown"

class IntentRouter:
    def __init__(self, co_client: cohere.Client):
        self.co = co_client
    
    def classify_intent(self, user_input: str) -> Intent:
        """
        Classifies user input into one of three intents:
        - CHAT: General conversation
        - OS_COMMAND: System commands (file operations, launching programs)
        - OSQUERY: Security/forensics queries about system state
        """
        prompt = f"""
Classify the following user input into one of these categories:
- CHAT: General conversation, greetings, personal questions, non-technical queries
- OS_COMMAND: Direct system operations like creating files/folders, launching applications, file management
- OSQUERY: Questions about system state, security, running processes, users, network connections, installed software

Respond ONLY with one of: CHAT, OS_COMMAND, OSQUERY

Examples:
"Hello how are you?" -> CHAT
"What time is it?" -> CHAT
"What can you help me with?" -> CHAT
"Show me running processes" -> OSQUERY
"Show running processes" -> OSQUERY
"What processes are running" -> OSQUERY
"List files in current directory" -> OS_COMMAND
"Create a new folder called test" -> OS_COMMAND
"Make a directory named projects" -> OS_COMMAND
"What users are logged in?" -> OSQUERY
"Are there any suspicious network connections?" -> OSQUERY
"What ports are listening?" -> OSQUERY
"Run ps aux" -> OSQUERY
"Execute ls -la" -> OS_COMMAND
"Open Chrome" -> OS_COMMAND

User input: {user_input}
Classification:"""

        try:
            response = self.co.chat(
                model="command-a-03-2025",
                message=prompt
            )
            
            intent_text = response.text.strip().upper()
            
            # Map the response to Intent enum
            if "CHAT" in intent_text:
                return Intent.CHAT
            elif "OS_COMMAND" in intent_text:
                return Intent.OS_COMMAND
            elif "OSQUERY" in intent_text:
                return Intent.OSQUERY
            else:
                # If unclear, default to CHAT for safety
                return Intent.CHAT
                
        except Exception as e:
            print(f"Router error: {e}")
            # Default to chat if classification fails
            return Intent.CHAT