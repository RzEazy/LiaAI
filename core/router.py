import cohere
from enum import Enum
from typing import Optional

class Intent(Enum):
    CHAT = "chat"
    OS_COMMAND = "os_command"
    OSQUERY = "osquery"
    UNKNOWN = "unknown"

class IntentRouter:
    """
    Advanced Intent Router for LiaAI
    Classifies user input into CHAT, OS_COMMAND, or OSQUERY with high accuracy
    """
    
    def __init__(self, co_client: cohere.Client):
        self.co = co_client
        self.classification_prompt = self._build_classification_prompt()
    
    def classify_intent(self, user_input: str) -> Intent:
        """
        Classifies user input into one of three intents
        
        Args:
            user_input: The user's natural language input
            
        Returns:
            Intent enum (CHAT, OS_COMMAND, OSQUERY, or UNKNOWN)
        """
        if not user_input or not user_input.strip():
            return Intent.CHAT
        
        try:
            prompt = self.classification_prompt.format(user_input=user_input)
            
            response = self.co.chat(
                model="command-a-03-2025",
                message=prompt,
                temperature=0.1  # Low temperature for consistent classification
            )
            
            intent_text = response.text.strip().upper()
            
            # Parse the response
            return self._parse_intent(intent_text)
                
        except Exception as e:
            print(f"Router error: {e}")
            return Intent.CHAT  # Fail-safe: default to chat
    
    def _parse_intent(self, intent_text: str) -> Intent:
        """Parse the LLM response into Intent enum"""
        # Check for exact matches first
        if intent_text == "CHAT":
            return Intent.CHAT
        elif intent_text == "OS_COMMAND":
            return Intent.OS_COMMAND
        elif intent_text == "OSQUERY":
            return Intent.OSQUERY
        
        # Check for partial matches (in case LLM added extra text)
        if "OS_COMMAND" in intent_text or "OS COMMAND" in intent_text:
            return Intent.OS_COMMAND
        elif "OSQUERY" in intent_text:
            return Intent.OSQUERY
        elif "CHAT" in intent_text:
            return Intent.CHAT
        
        # Default fallback
        return Intent.CHAT
    
    def _build_classification_prompt(self) -> str:
        """Build comprehensive classification prompt with balanced examples"""
        return """You are an expert intent classifier for a cyber security assistant.

Classify the user input into EXACTLY ONE of these categories:

1. CHAT - General conversation, questions, help requests, non-technical queries
2. OS_COMMAND - Direct system operations (file/folder operations, running programs, system commands)
3. OSQUERY - Security & forensics queries (analyzing system state, processes, users, connections)

CRITICAL RULES:
- Respond with ONLY ONE WORD: CHAT, OS_COMMAND, or OSQUERY
- No explanation, no punctuation, just the category name
- When in doubt between OS_COMMAND and OSQUERY, prefer OSQUERY for security/analysis questions

==================================================
CHAT EXAMPLES (Conversation & General Queries)
==================================================

Greetings & Pleasantries:
"hello" -> CHAT
"hi there" -> CHAT
"how are you?" -> CHAT
"good morning" -> CHAT
"hey Lia" -> CHAT
"what's up?" -> CHAT
"goodbye" -> CHAT
"see you later" -> CHAT

Help & Information:
"what can you do?" -> CHAT
"help me" -> CHAT
"what are your capabilities?" -> CHAT
"how do I use you?" -> CHAT
"explain what you are" -> CHAT
"what commands can you run?" -> CHAT
"tell me about yourself" -> CHAT

General Questions:
"what time is it?" -> CHAT
"tell me a joke" -> CHAT
"what's your favorite color?" -> CHAT
"who created you?" -> CHAT
"what's the weather like?" -> CHAT
"recommend a movie" -> CHAT

Clarifications & Feedback:
"what did I just ask?" -> CHAT
"can you explain that better?" -> CHAT
"I don't understand" -> CHAT
"thank you" -> CHAT
"that was helpful" -> CHAT
"great job" -> CHAT

Technical Explanations:
"what is cybersecurity?" -> CHAT
"explain what a process is" -> CHAT
"what are network ports?" -> CHAT
"tell me about Linux" -> CHAT
"what is osquery?" -> CHAT
"how do firewalls work?" -> CHAT

==================================================
OS_COMMAND EXAMPLES (Direct System Operations)
==================================================

File & Directory Operations:
"create a folder called test" -> OS_COMMAND
"make a directory named projects" -> OS_COMMAND
"delete the folder test" -> OS_COMMAND
"remove file test.txt" -> OS_COMMAND
"list files in current directory" -> OS_COMMAND
"show directory contents" -> OS_COMMAND
"create a file named readme.md" -> OS_COMMAND
"copy file.txt to backup.txt" -> OS_COMMAND
"move data.json to folder/" -> OS_COMMAND
"rename old.txt to new.txt" -> OS_COMMAND

Navigation & Path:
"show current directory" -> OS_COMMAND
"show me the current path" -> OS_COMMAND
"what directory am I in?" -> OS_COMMAND
"print working directory" -> OS_COMMAND
"where am I?" -> OS_COMMAND
"pwd" -> OS_COMMAND
"cd /home/user" -> OS_COMMAND

Disk & Storage:
"how much disk space is free?" -> OS_COMMAND
"show disk usage" -> OS_COMMAND
"check disk space" -> OS_COMMAND
"display storage information" -> OS_COMMAND
"df -h" -> OS_COMMAND
"show available space" -> OS_COMMAND

Memory & System Resources:
"display RAM usage" -> OS_COMMAND
"show memory usage" -> OS_COMMAND
"check available memory" -> OS_COMMAND
"free -h" -> OS_COMMAND
"how much RAM is available?" -> OS_COMMAND
"check system memory" -> OS_COMMAND

Network Configuration:
"what's my IP address?" -> OS_COMMAND
"show network interfaces" -> OS_COMMAND
"display IP configuration" -> OS_COMMAND
"ifconfig" -> OS_COMMAND
"ip addr" -> OS_COMMAND
"ipconfig" -> OS_COMMAND
"ping google.com" -> OS_COMMAND
"test connection to 8.8.8.8" -> OS_COMMAND

System Information:
"show system information" -> OS_COMMAND
"display OS version" -> OS_COMMAND
"uname -a" -> OS_COMMAND
"systeminfo" -> OS_COMMAND
"what operating system is this?" -> OS_COMMAND

User & Environment:
"who am I?" -> OS_COMMAND
"whoami" -> OS_COMMAND
"show current user" -> OS_COMMAND
"display environment variables" -> OS_COMMAND
"show PATH variable" -> OS_COMMAND
"printenv" -> OS_COMMAND
"echo $HOME" -> OS_COMMAND

Application Launching:
"open chrome" -> OS_COMMAND
"launch firefox" -> OS_COMMAND
"start calculator" -> OS_COMMAND
"open file manager" -> OS_COMMAND
"run notepad" -> OS_COMMAND

File Content & Search:
"show contents of test.txt" -> OS_COMMAND
"cat readme.md" -> OS_COMMAND
"read file log.txt" -> OS_COMMAND
"search for error in log.txt" -> OS_COMMAND
"grep warning system.log" -> OS_COMMAND
"find files named *.txt" -> OS_COMMAND

Direct Commands:
"ls -la" -> OS_COMMAND
"ps aux" -> OS_COMMAND
"top" -> OS_COMMAND
"htop" -> OS_COMMAND
"netstat -tuln" -> OS_COMMAND
"du -sh" -> OS_COMMAND

==================================================
OSQUERY EXAMPLES (Security & Forensics Analysis)
==================================================

Process Analysis:
"show me running processes" -> OSQUERY
"show running processes" -> OSQUERY
"what processes are running?" -> OSQUERY
"list all processes" -> OSQUERY
"display active processes" -> OSQUERY
"what's running on my system?" -> OSQUERY
"enumerate running processes" -> OSQUERY
"show me process details" -> OSQUERY
"show me python processes" -> OSQUERY
"list all chrome processes" -> OSQUERY
"what firefox processes are running?" -> OSQUERY
"show me processes owned by root" -> OSQUERY
"list processes by memory usage" -> OSQUERY
"show me top 10 processes by memory" -> OSQUERY
"what processes are using the most CPU?" -> OSQUERY
"show me processes with network connections" -> OSQUERY
"what processes have open sockets?" -> OSQUERY

Network Security:
"what network ports are listening?" -> OSQUERY
"show me listening ports" -> OSQUERY
"list all open ports" -> OSQUERY
"what ports are accepting connections?" -> OSQUERY
"show me network listeners" -> OSQUERY
"what's listening on my system?" -> OSQUERY
"show me all network connections" -> OSQUERY
"list active connections" -> OSQUERY
"what network connections exist?" -> OSQUERY
"display established connections" -> OSQUERY
"show me external connections" -> OSQUERY
"list connections to foreign IPs" -> OSQUERY
"what's connecting to the internet?" -> OSQUERY
"show me TCP connections" -> OSQUERY
"list UDP ports" -> OSQUERY
"what process is on port 80?" -> OSQUERY
"show me ports below 1024" -> OSQUERY
"what's listening on port 443?" -> OSQUERY
"show me Firefox network activity" -> OSQUERY
"what's Chrome connecting to?" -> OSQUERY

User & Authentication:
"who is currently logged in?" -> OSQUERY
"show me logged in users" -> OSQUERY
"list active users" -> OSQUERY
"what users are online?" -> OSQUERY
"list all users on the system" -> OSQUERY
"show me all system users" -> OSQUERY
"what users exist on this machine?" -> OSQUERY
"display all user accounts" -> OSQUERY
"show me users with shell access" -> OSQUERY
"list users with bash shell" -> OSQUERY
"what users can login?" -> OSQUERY
"show me recent login history" -> OSQUERY
"who logged in recently?" -> OSQUERY
"display last logins" -> OSQUERY
"show me login attempts" -> OSQUERY

System State & Configuration:
"show system information" -> OSQUERY
"display system details" -> OSQUERY
"what system am I running?" -> OSQUERY
"show me system specs" -> OSQUERY
"what CPU is installed?" -> OSQUERY
"how much memory is installed?" -> OSQUERY
"what's the hostname?" -> OSQUERY
"show me hardware information" -> OSQUERY
"show me mounted filesystems" -> OSQUERY
"list all mounts" -> OSQUERY
"what filesystems are mounted?" -> OSQUERY
"what kernel modules are loaded?" -> OSQUERY
"show me loaded modules" -> OSQUERY
"list kernel modules" -> OSQUERY

Scheduled Tasks & Services:
"show me scheduled cron jobs" -> OSQUERY
"list all crontab entries" -> OSQUERY
"what tasks are scheduled?" -> OSQUERY
"display cron configuration" -> OSQUERY
"show me automated tasks" -> OSQUERY

Hardware & Devices:
"what USB devices are connected?" -> OSQUERY
"show me USB devices" -> OSQUERY
"list plugged in USB devices" -> OSQUERY
"show me PCI devices" -> OSQUERY
"what hardware is installed?" -> OSQUERY

Security Analysis:
"are there any suspicious processes?" -> OSQUERY
"show me unusual network connections" -> OSQUERY
"detect potential threats" -> OSQUERY
"find backdoor processes" -> OSQUERY
"show me suspicious ports listening" -> OSQUERY
"what's listening on port 4444?" -> OSQUERY
"check for netcat processes" -> OSQUERY
"find suspicious services" -> OSQUERY
"are there any unusual ports listening?" -> OSQUERY

File System (with analysis context):
"show me recently modified files in /tmp" -> OSQUERY
"list files modified today" -> OSQUERY
"what files changed in /etc recently?" -> OSQUERY
"show me executable files in /tmp" -> OSQUERY
"list SUID files" -> OSQUERY

Complex Queries:
"show me processes and their listening ports" -> OSQUERY
"what processes have external connections?" -> OSQUERY
"list users and their processes" -> OSQUERY
"show me Firefox and its network connections" -> OSQUERY
"which processes are listening on privileged ports?" -> OSQUERY
"show me all chrome processes with their connections" -> OSQUERY

Browser & Application Analysis:
"show me browser processes" -> OSQUERY
"list browser extensions" -> OSQUERY
"what browsers are running?" -> OSQUERY
"show me database processes" -> OSQUERY
"list web server processes" -> OSQUERY

==================================================

Now classify this user input:

User input: {user_input}
Classification:"""
    
    def get_intent_description(self, intent: Intent) -> str:
        """Get human-readable description of an intent"""
        descriptions = {
            Intent.CHAT: "General conversation and questions",
            Intent.OS_COMMAND: "Direct system command execution",
            Intent.OSQUERY: "Security and forensics analysis",
            Intent.UNKNOWN: "Unclear or unclassifiable intent"
        }
        return descriptions.get(intent, "Unknown intent")
    
    def suggest_reclassification(self, user_input: str, current_intent: Intent) -> Optional[Intent]:
        """
        Suggest alternative classification if the current one seems wrong
        Used for debugging and improving classification accuracy
        """
        user_lower = user_input.lower()
        
        # Common misclassification patterns
        if current_intent == Intent.OSQUERY:
            # Should be OS_COMMAND
            os_indicators = ['disk space', 'disk usage', 'current path', 'current directory',
                           'ram usage', 'memory usage', 'ip address', 'network interface',
                           'environment variable', 'pwd', 'df -h', 'free -h', 'ifconfig']
            if any(indicator in user_lower for indicator in os_indicators):
                return Intent.OS_COMMAND
        
        elif current_intent == Intent.OS_COMMAND:
            # Should be OSQUERY
            osquery_indicators = ['listening ports', 'logged in users', 'all users',
                                'running processes', 'network connections', 'process details',
                                'security', 'suspicious', 'forensics']
            if any(indicator in user_lower for indicator in osquery_indicators):
                return Intent.OSQUERY
        
        return None