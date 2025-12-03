import subprocess
import json
from typing import List, Dict, Any, Tuple

class OsqueryEngine:
    def __init__(self, osqueryi_path: str = "osqueryi"):
        self.osqueryi_path = osqueryi_path
    
    def execute_query(self, sql_query: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Execute an osquery SQL statement and return results
        
        Returns:
            Tuple of (results, error_message)
        """
        try:
            # Format the query for osqueryi
            cmd = [
                self.osqueryi_path,
                "--json",
                sql_query
            ]
            
            # Execute the query
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode != 0:
                return [], f"Osquery error: {result.stderr}"
            
            # Parse JSON output
            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    return data, ""
                except json.JSONDecodeError:
                    return [], "Failed to parse osquery output"
            else:
                return [], ""
                
        except subprocess.TimeoutExpired:
            return [], "Query timed out"
        except Exception as e:
            return [], f"Execution error: {str(e)}"
    
    def is_osquery_installed(self) -> bool:
        """Check if osquery is installed and accessible"""
        try:
            result = subprocess.run(
                [self.osqueryi_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False