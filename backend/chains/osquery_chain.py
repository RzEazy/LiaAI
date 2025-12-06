import cohere
import re
from typing import Dict, Any, Optional, List
from .base_chain import BaseChain

OSQUERY_PROMPT_TEMPLATE = """
You are an expert in osquery SQL. Convert the user's security/forensics question into a valid osquery SQL statement.

CRITICAL RULES:
- Respond ONLY with the SQL query, nothing else
- Use proper osquery tables and columns
- If the question isn't related to system security/state, respond with: NOT_APPLICABLE
- ALWAYS use LIMIT clauses (default LIMIT 50 unless user specifies otherwise)
- Do NOT use destructive operations (DROP, DELETE, INSERT, UPDATE, CREATE, ALTER)
- Use proper JOINs when combining tables
- Always SELECT specific columns, avoid SELECT *

COMMON OSQUERY TABLES:
- processes: pid, name, path, cmdline, uid, parent, state
- users: uid, gid, username, description, directory, shell
- listening_ports: pid, port, protocol, family, address
- process_open_sockets: pid, fd, socket, family, protocol, local_address, local_port, remote_address, remote_port
- logged_in_users: type, user, tty, host, time, pid
- system_info: hostname, uuid, cpu_type, cpu_brand, physical_memory, hardware_model
- os_version: name, version, major, minor, patch, build
- interface_addresses: interface, address, mask, broadcast
- startup_items: name, path, args, type, source, status
- kernel_modules: name, size, used_by, status
- file: path, directory, filename, size, mtime, atime, ctime, uid, gid, mode
- hash: path, md5, sha1, sha256

ADVANCED EXAMPLES:
User: Show me all running processes
Response: SELECT pid, name, cmdline, parent, uid FROM processes LIMIT 50;

User: What network ports are listening?
Response: SELECT lp.port, lp.protocol, lp.address, p.name, p.pid FROM listening_ports lp LEFT JOIN processes p ON lp.pid = p.pid LIMIT 50;

User: Show me active network connections
Response: SELECT pos.pid, p.name, pos.local_address, pos.local_port, pos.remote_address, pos.remote_port, pos.protocol FROM process_open_sockets pos JOIN processes p ON pos.pid = p.pid WHERE pos.remote_port != 0 LIMIT 50;

User: Are there any suspicious login attempts in the last hour?
Response: SELECT time, user, host, tty FROM logged_in_users WHERE time > strftime('%s', 'now') - 3600 LIMIT 50;

User: Find processes running as root
Response: SELECT pid, name, path, cmdline FROM processes WHERE uid = 0 LIMIT 50;

User: Show me Python processes
Response: SELECT pid, name, cmdline, parent FROM processes WHERE name LIKE '%python%' OR cmdline LIKE '%python%' LIMIT 50;

User: What files were modified in /tmp in the last 24 hours?
Response: SELECT path, filename, mtime, size, uid FROM file WHERE directory = '/tmp' AND mtime > strftime('%s', 'now') - 86400 LIMIT 50;

User: Show system information
Response: SELECT hostname, cpu_brand, physical_memory, hardware_model FROM system_info LIMIT 1;

User: List users with shell access
Response: SELECT uid, username, shell, directory FROM users WHERE shell NOT IN ('', '/usr/bin/false', '/sbin/nologin') LIMIT 50;

User: {user_input}
SQL Query:"""

class OsqueryChain(BaseChain):
    """Chain for generating and validating osquery SQL statements"""
    
    def __init__(self, co_client: cohere.Client):
        self.co = co_client
        self.max_retries = 2
        
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process security/forensics input and generate osquery SQL
        
        Args:
            user_input: User's natural language query
            context: Additional context including previous queries
            
        Returns:
            Dictionary with response (SQL query) and metadata
        """
        if context is None:
            context = {}
        
        # Check if user is asking about a previous query
        if self._is_reference_to_previous_query(user_input):
            previous_query = self._get_last_query(context)
            if previous_query:
                return {
                    "response": previous_query,
                    "metadata": {
                        "chain": "osquery",
                        "sql": previous_query,
                        "reused": True
                    }
                }
        
        # Generate SQL query with retries
        for attempt in range(self.max_retries):
            try:
                sql_query = self._generate_sql(user_input, context, attempt)
                
                if sql_query == "NOT_APPLICABLE":
                    return {
                        "response": None,
                        "metadata": {
                            "chain": "osquery",
                            "sql": None,
                            "reason": "not_applicable"
                        }
                    }
                
                # Validate and clean the SQL
                cleaned_sql = self._clean_sql(sql_query)
                
                if not cleaned_sql:
                    continue
                    
                # Basic validation
                if self._is_valid_osquery_sql(cleaned_sql):
                    return {
                        "response": cleaned_sql,
                        "metadata": {
                            "chain": "osquery",
                            "sql": cleaned_sql,
                            "attempts": attempt + 1
                        }
                    }
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        "response": None,
                        "metadata": {
                            "chain": "osquery",
                            "error": str(e),
                            "attempts": attempt + 1
                        }
                    }
                continue
        
        # All attempts failed
        return {
            "response": None,
            "metadata": {
                "chain": "osquery",
                "error": "Failed to generate valid SQL after multiple attempts"
            }
        }
    
    def _generate_sql(self, user_input: str, context: Dict[str, Any], attempt: int) -> str:
        """Generate SQL query using LLM"""
        prompt = OSQUERY_PROMPT_TEMPLATE.format(user_input=user_input)
        
        # Add context from previous queries if available
        recent_queries = context.get("queries", [])
        if recent_queries and attempt > 0:
            prompt += f"\n\nNote: Previous similar queries:\n"
            for q in recent_queries[-3:]:
                prompt += f"- {q.get('query', '')}\n"
        
        response = self.co.chat(
            model="command-a-03-2025",
            message=prompt,
            temperature=0.3  # Lower temperature for more consistent SQL
        )
        
        return response.text.strip()
    
    def _clean_sql(self, sql_query: str) -> str:
        """Clean and normalize SQL query"""
        # Remove markdown code blocks
        sql_query = re.sub(r'```sql\s*|\s*```', '', sql_query)
        sql_query = re.sub(r'```\s*|\s*```', '', sql_query)
        
        # Remove extra whitespace
        sql_query = ' '.join(sql_query.split())
        
        # Ensure it ends with semicolon
        if not sql_query.endswith(';'):
            sql_query += ';'
        
        return sql_query.strip()
    
    def _is_valid_osquery_sql(self, sql: str) -> bool:
        """Basic validation of osquery SQL"""
        sql_lower = sql.lower()
        
        # Must start with SELECT
        if not sql_lower.startswith('select'):
            return False
        
        # Must contain FROM
        if 'from' not in sql_lower:
            return False
        
        # Should not contain forbidden keywords
        forbidden = ['drop', 'delete', 'insert', 'update', 'create', 'alter', 'truncate']
        if any(keyword in sql_lower for keyword in forbidden):
            return False
        
        # Check for basic SQL injection patterns
        if '--' in sql or '/*' in sql or '*/' in sql:
            return False
        
        return True
    
    def _is_reference_to_previous_query(self, user_input: str) -> bool:
        """Check if user is referring to a previous query"""
        reference_patterns = [
            r'\bthat query\b',
            r'\bprevious query\b',
            r'\blast query\b',
            r'\brun (that|it) again\b',
            r'\bsame (query|thing)\b',
            r'\brepeat\b'
        ]
        
        user_input_lower = user_input.lower()
        return any(re.search(pattern, user_input_lower) for pattern in reference_patterns)
    
    def _get_last_query(self, context: Dict[str, Any]) -> Optional[str]:
        """Get the last executed query from context"""
        queries = context.get("queries", [])
        if queries:
            return queries[-1].get("query")
        return None
    
    def suggest_related_queries(self, sql_query: str) -> List[str]:
        """Suggest related queries based on the current query"""
        suggestions = []
        sql_lower = sql_query.lower()
        
        if 'processes' in sql_lower:
            suggestions.extend([
                "Show processes using the most CPU",
                "Show processes using the most memory",
                "Show processes with open network connections"
            ])
        
        if 'listening_ports' in sql_lower:
            suggestions.extend([
                "Show active network connections",
                "Show processes listening on privileged ports (< 1024)",
                "Show all network-related processes"
            ])
        
        if 'users' in sql_lower:
            suggestions.extend([
                "Show currently logged in users",
                "Show users with sudo privileges",
                "Show user login history"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions