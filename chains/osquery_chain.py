import cohere
from typing import Dict, Any, Optional
from .base_chain import BaseChain

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
SELECT time, username, host FROM last WHERE time > strftime('%s', 'now') - 3600;

User: {user_input}
SQL Query:"""

class OsqueryChain(BaseChain):
    def __init__(self, co_client: cohere.Client):
        self.co = co_client
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process security/forensics input and generate osquery SQL
        """
        if context is None:
            context = {}
        
        # Construct prompt
        prompt = OSQUERY_PROMPT_TEMPLATE.format(
            user_input=user_input
        )
        
        try:
            response = self.co.chat(
                model="command-a-03-2025",
                message=prompt
            )
            
            sql_query = response.text.strip()
            
            if sql_query == "NOT_APPLICABLE":
                return {
                    "response": None,
                    "metadata": {
                        "chain": "osquery",
                        "sql": None
                    }
                }
            
            return {
                "response": sql_query,
                "metadata": {
                    "chain": "osquery",
                    "sql": sql_query
                }
            }
        except Exception as e:
            return {
                "response": None,
                "metadata": {
                    "chain": "osquery",
                    "error": str(e)
                }
            }