from typing import List, Dict, Any

class ResultFormatter:
    @staticmethod
    def format_os_result(command: str, output: str) -> str:
        """Format OS command results"""
        if not output:
            return f"🛠 Executed: `{command}`\n\nNo output."
        
        # Truncate long outputs
        if len(output) > 1000:
            output = output[:1000] + "\n... (truncated)"
        
        return f"🛠 Executed: `{command}`\n\nOutput:\n```\n{output}\n```"
    
    @staticmethod
    def format_osquery_result(sql: str, results: List[Dict[str, Any]]) -> str:
        """Format osquery results as a table"""
        if not results:
            return f"🔍 Query: `{sql}`\n\nNo results found."
        
        # Limit results to prevent overwhelming output
        display_results = results[:50]  # Show max 50 rows
        
        # Get column names
        if display_results:
            headers = list(display_results[0].keys())
        else:
            return f"🔍 Query: `{sql}`\n\nNo results found."
        
        # Create table
        table = "| " + " | ".join(headers) + " |\n"
        table += "|" + "|".join(["---" for _ in headers]) + "|\n"
        
        for row in display_results:
            values = [str(row.get(header, "")) for header in headers]
            # Truncate long values
            values = [val[:50] + "..." if len(val) > 50 else val for val in values]
            table += "| " + " | ".join(values) + " |\n"
        
        result_text = f"🔍 Query: `{sql}`\n\nResults ({len(results)} rows):\n\n{table}"
        
        if len(results) > 50:
            result_text += f"\n*Showing first 50 of {len(results)} results*"
        
        return result_text
    
    @staticmethod
    def format_error(error_msg: str) -> str:
        """Format error messages"""
        return f"⚠ Error: {error_msg}"