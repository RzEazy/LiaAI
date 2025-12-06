# Prompt templates for different chains

CHAT_PROMPT_TEMPLATE = """
You are Lia, a helpful AI assistant. Keep your responses concise and friendly.

Previous conversation:
{history}

User: {user_input}
Lia:"""

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

OSQUERY_PROMPT_TEMPLATE = """
Convert the user's security/forensics question into a valid osquery SQL statement.

RULES:
- Respond ONLY with the SQL query, nothing else
- Use proper osquery tables and columns
- If the question isn't related to system security/state, respond with: NOT_APPLICABLE
- Focus on tables like: processes, users, listening_ports, etc.
- Do NOT use destructive operations (DROP, DELETE, INSERT, UPDATE)
- Use LIMIT clauses for large result sets

Examples:
User: Show me all running processes
SELECT pid, name, cmdline, parent FROM processes;

User: What network ports are listening?
SELECT port, protocol, process.name FROM listening_ports JOIN processes USING (pid);

User: Are there any suspicious login attempts?
SELECT time, username, host FROM last WHERE time > strftime('%%s', 'now') - 3600;

User: {user_input}
SQL Query:"""