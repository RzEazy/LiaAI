#!/usr/bin/env python3
"""
LiaAI Security Dashboard - Quick system security overview
Add this as a new command: "show security dashboard" or "security status"
"""

from core.lia_main import LiaMain
from typing import Dict, List, Any
import json

class SecurityDashboard:
    def __init__(self, lia_instance: LiaMain):
        self.lia = lia_instance
        
    def generate_dashboard(self) -> str:
        """Generate a comprehensive security dashboard"""
        
        dashboard = []
        dashboard.append("=" * 70)
        dashboard.append("🛡️  LIAAI SECURITY DASHBOARD")
        dashboard.append("=" * 70)
        dashboard.append("")
        
        # Section 1: System Overview
        dashboard.append("📊 SYSTEM OVERVIEW")
        dashboard.append("-" * 70)
        sys_info = self._get_system_info()
        for key, value in sys_info.items():
            dashboard.append(f"  {key}: {value}")
        dashboard.append("")
        
        # Section 2: User Activity
        dashboard.append("👤 USER ACTIVITY")
        dashboard.append("-" * 70)
        user_info = self._get_user_activity()
        for item in user_info:
            dashboard.append(f"  • {item}")
        dashboard.append("")
        
        # Section 3: Network Security
        dashboard.append("🌐 NETWORK SECURITY")
        dashboard.append("-" * 70)
        network_info = self._get_network_security()
        for item in network_info:
            dashboard.append(f"  • {item}")
        dashboard.append("")
        
        # Section 4: Process Security
        dashboard.append("⚙️  PROCESS SECURITY")
        dashboard.append("-" * 70)
        process_info = self._get_process_security()
        for item in process_info:
            dashboard.append(f"  • {item}")
        dashboard.append("")
        
        # Section 5: Security Alerts
        dashboard.append("🚨 SECURITY ALERTS")
        dashboard.append("-" * 70)
        alerts = self._check_security_alerts()
        if alerts:
            for alert in alerts:
                dashboard.append(f"  ⚠️  {alert}")
        else:
            dashboard.append("  ✅ No immediate security concerns detected")
        dashboard.append("")
        
        dashboard.append("=" * 70)
        
        return "\n".join(dashboard)
    
    def _run_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute osquery and return results"""
        results, error = self.lia.osquery_engine.execute_query(sql)
        if error:
            return []
        return results
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get basic system information"""
        sql = "SELECT hostname, cpu_brand, physical_memory FROM system_info;"
        results = self._run_query(sql)
        
        if results:
            info = results[0]
            memory_gb = int(info.get('physical_memory', 0)) / (1024**3)
            return {
                "Hostname": info.get('hostname', 'Unknown'),
                "CPU": info.get('cpu_brand', 'Unknown'),
                "Memory": f"{memory_gb:.2f} GB"
            }
        return {"Status": "Unable to retrieve system info"}
    
    def _get_user_activity(self) -> List[str]:
        """Get current user activity"""
        sql = "SELECT user, tty, host FROM logged_in_users;"
        results = self._run_query(sql)
        
        info = []
        if results:
            info.append(f"Logged in users: {len(results)}")
            for user in results[:5]:  # Show max 5
                info.append(f"  - {user.get('user', 'unknown')} on {user.get('tty', 'unknown')}")
        else:
            info.append("No logged in users detected")
        
        # Get total users
        sql = "SELECT COUNT(*) as count FROM users;"
        results = self._run_query(sql)
        if results:
            info.append(f"Total system users: {results[0].get('count', 0)}")
        
        return info
    
    def _get_network_security(self) -> List[str]:
        """Get network security status"""
        info = []
        
        # Listening ports
        sql = "SELECT COUNT(*) as count FROM listening_ports;"
        results = self._run_query(sql)
        if results:
            info.append(f"Listening ports: {results[0].get('count', 0)}")
        
        # External connections
        sql = """
        SELECT COUNT(*) as count 
        FROM process_open_sockets 
        WHERE remote_address != '' 
          AND remote_address != '127.0.0.1'
          AND remote_address != '::1';
        """
        results = self._run_query(sql)
        if results:
            info.append(f"Active external connections: {results[0].get('count', 0)}")
        
        # Privileged ports (< 1024)
        sql = "SELECT COUNT(*) as count FROM listening_ports WHERE port < 1024;"
        results = self._run_query(sql)
        if results:
            info.append(f"Privileged ports in use: {results[0].get('count', 0)}")
        
        return info
    
    def _get_process_security(self) -> List[str]:
        """Get process security status"""
        info = []
        
        # Total processes
        sql = "SELECT COUNT(*) as count FROM processes;"
        results = self._run_query(sql)
        if results:
            info.append(f"Running processes: {results[0].get('count', 0)}")
        
        # Root processes
        sql = "SELECT COUNT(*) as count FROM processes WHERE uid = 0;"
        results = self._run_query(sql)
        if results:
            info.append(f"Root-owned processes: {results[0].get('count', 0)}")
        
        return info
    
    def _check_security_alerts(self) -> List[str]:
        """Check for potential security issues"""
        alerts = []
        
        # Check for suspicious ports
        sql = "SELECT port, protocol FROM listening_ports WHERE port IN (4444, 5555, 6666, 31337);"
        results = self._run_query(sql)
        if results:
            ports = [str(r.get('port')) for r in results]
            alerts.append(f"Suspicious ports detected: {', '.join(ports)}")
        
        # Check for too many external connections (potential data exfiltration)
        sql = """
        SELECT COUNT(*) as count 
        FROM process_open_sockets 
        WHERE remote_address != '' 
          AND remote_address != '127.0.0.1';
        """
        results = self._run_query(sql)
        if results and int(results[0].get('count', 0)) > 50:
            alerts.append(f"High number of external connections: {results[0]['count']}")
        
        # Check for unusual cron jobs (if accessible)
        sql = "SELECT COUNT(*) as count FROM crontab;"
        results = self._run_query(sql)
        if results and int(results[0].get('count', 0)) > 20:
            alerts.append(f"Unusual number of cron jobs: {results[0]['count']}")
        
        return alerts


# Integration example: Add this to lia_main.py
def add_dashboard_to_lia():
    """
    Add this method to the LiaMain class in lia_main.py:
    
    def show_dashboard(self) -> str:
        from tools.security_dashboard import SecurityDashboard
        dashboard = SecurityDashboard(self)
        return dashboard.generate_dashboard()
    
    Then in the router, add a new intent for dashboard requests,
    or handle it as a special command in _handle_chat()
    """
    pass


# Standalone usage for testing
if __name__ == "__main__":
    # Initialize LiaAI
    lia = LiaMain(
        api_key="doeM32W2so3ubfYYs673lmiOmUzwN15weKfB68bj",
        memory_file="lia_memory.json"
    )
    
    # Generate and display dashboard
    dashboard = SecurityDashboard(lia)
    print(dashboard.generate_dashboard())