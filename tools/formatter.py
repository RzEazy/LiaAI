from typing import List, Dict, Any

class ResultFormatter:
    @staticmethod
    def format_os_result(command: str, output: str) -> str:
        """Format OS command results"""
        if not output:
            return f"🛠 Executed: `{command}`\n\nNo output."
        
        # Show full output without truncation
        return f"🛠 Executed: `{command}`\n\nOutput:\n```\n{output}\n```"
    
    @staticmethod
    def format_osquery_result(sql: str, results: List[Dict[str, Any]]) -> str:
        """Format osquery results as a well-formatted table"""
        if not results:
            return f"🔍 Query: `{sql}`\n\nNo results found."
        
        # Show all results without limiting
        display_results = results
        
        # Get column names
        if display_results:
            headers = list(display_results[0].keys())
        else:
            return f"🔍 Query: `{sql}`\n\nNo results found."
        
        # Special handling for network data - reorder columns for better readability
        network_indicators = ['port', 'protocol', 'address', 'local_address', 'remote_address', 'local_port', 'remote_port', 'state', 'name', 'pid']
        if any(indicator in ''.join(headers).lower() for indicator in ['port', 'address', 'socket']):
            # Reorder headers for network data: process info first, then connection info
            reordered_headers = []
            # Add process-related columns first
            for header in ['name', 'pid', 'process_name']:
                if header in headers:
                    reordered_headers.append(header)
            # Add network-related columns
            for header in ['local_address', 'local_port', 'remote_address', 'remote_port', 'port', 'protocol', 'address', 'state']:
                if header in headers and header not in reordered_headers:
                    reordered_headers.append(header)
            # Add any remaining columns
            for header in headers:
                if header not in reordered_headers:
                    reordered_headers.append(header)
            headers = reordered_headers
        
        # Calculate column widths for better alignment
        col_widths = {}
        for header in headers:
            max_width = len(str(header))
            for row in display_results:
                value = str(row.get(header, ""))
                max_width = max(max_width, len(value))
            # Set reasonable limits for column widths
            if header in ['local_address', 'remote_address', 'address']:
                col_widths[header] = min(max_width, 15)  # IP addresses
            elif header in ['name', 'process_name']:
                col_widths[header] = min(max_width, 20)  # Process names
            else:
                col_widths[header] = min(max_width, 30)  # Other columns
        
        # Create table header
        header_row = "|"
        separator_row = "|"
        for header in headers:
            width = col_widths[header]
            header_row += f" {header:<{width}} |"
            separator_row += "-" * (width + 2) + "|"
        
        table = header_row + "\n" + separator_row + "\n"
        
        # Add data rows
        for row in display_results:
            data_row = "|"
            for header in headers:
                width = col_widths[header]
                value = str(row.get(header, ""))
                # Truncate very long values but show more context than before
                if len(value) > width:
                    value = value[:width-3] + "..."
                data_row += f" {value:<{width}} |"
            table += data_row + "\n"
        
        result_text = f"🔍 Query: `{sql}`\n\nResults ({len(results)} rows):\n\n{table}"
        
        return result_text
    
    @staticmethod
    def format_error(error_msg: str) -> str:
        """Format error messages"""
        return f"⚠ Error: {error_msg}"