#!/usr/bin/env python3
"""
Server diagnostics module for DNS Server Manager
"""

import logging
import socket
import platform
import psutil
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ServerDiagnostics:
    """Comprehensive server diagnostics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": sys.version,
                "architecture": platform.architecture(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
                "memory_available": f"{psutil.virtual_memory().available / (1024**3):.1f} GB",
                "disk_usage": f"{psutil.disk_usage('/').used / (1024**3):.1f} GB / {psutil.disk_usage('/').total / (1024**3):.1f} GB"
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            # Get local IP addresses
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Get all network interfaces
            interfaces = {}
            for interface, addrs in psutil.net_if_addrs().items():
                interfaces[interface] = [addr.address for addr in addrs if addr.family == socket.AF_INET]
            
            # Check if port 53 is available
            port_53_status = self._check_port(53)
            
            return {
                "hostname": hostname,
                "local_ip": local_ip,
                "interfaces": interfaces,
                "port_53_status": port_53_status,
                "dns_servers": self._get_dns_servers()
            }
        except Exception as e:
            self.logger.error(f"Error getting network info: {e}")
            return {"error": str(e)}
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get process information"""
        try:
            current_process = psutil.Process()
            return {
                "pid": current_process.pid,
                "name": current_process.name(),
                "status": current_process.status(),
                "create_time": datetime.fromtimestamp(current_process.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
                "cpu_percent": f"{current_process.cpu_percent():.1f}%",
                "memory_percent": f"{current_process.memory_percent():.1f}%",
                "memory_info": f"{current_process.memory_info().rss / (1024**2):.1f} MB",
                "num_threads": current_process.num_threads(),
                "connections": len(current_process.connections())
            }
        except Exception as e:
            self.logger.error(f"Error getting process info: {e}")
            return {"error": str(e)}
    
    def get_dns_server_info(self, dns_server) -> Dict[str, Any]:
        """Get DNS server specific information"""
        try:
            if not dns_server:
                return {"error": "DNS server not available"}
            
            return {
                "is_running": dns_server.is_running,
                "port": dns_server.port,
                "bind_address": dns_server.bind_address,
                "timeout": dns_server.timeout,
                "max_connections": dns_server.max_connections,
                "active_connections": len(dns_server.active_connections) if hasattr(dns_server, 'active_connections') else "N/A",
                "total_queries": getattr(dns_server, 'total_queries', 0),
                "queries_per_second": getattr(dns_server, 'queries_per_second', 0),
                "uptime": self._get_uptime(dns_server)
            }
        except Exception as e:
            self.logger.error(f"Error getting DNS server info: {e}")
            return {"error": str(e)}
    
    def get_database_info(self, database) -> Dict[str, Any]:
        """Get database information"""
        try:
            if not database:
                return {"error": "Database not available"}
            
            # Get database file info
            db_path = Path(database.db_path)
            if db_path.exists():
                file_size = db_path.stat().st_size
                file_modified = datetime.fromtimestamp(db_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            else:
                file_size = 0
                file_modified = "File not found"
            
            # Get record count
            try:
                records = database.list_records()
                record_count = len(records)
            except:
                record_count = "Error"
            
            return {
                "database_path": str(database.db_path),
                "file_size": f"{file_size / 1024:.1f} KB",
                "last_modified": file_modified,
                "record_count": record_count,
                "database_exists": db_path.exists()
            }
        except Exception as e:
            self.logger.error(f"Error getting database info: {e}")
            return {"error": str(e)}
    
    def run_connectivity_tests(self) -> Dict[str, Any]:
        """Run connectivity tests"""
        tests = {}
        
        # Test local DNS resolution
        try:
            result = socket.gethostbyname('localhost')
            tests['localhost_resolution'] = {"status": "PASS", "result": result}
        except Exception as e:
            tests['localhost_resolution'] = {"status": "FAIL", "error": str(e)}
        
        # Test Google DNS
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            sock.connect(('8.8.8.8', 53))
            tests['google_dns_connectivity'] = {"status": "PASS", "result": "Connected"}
            sock.close()
        except Exception as e:
            tests['google_dns_connectivity'] = {"status": "FAIL", "error": str(e)}
        
        # Test port 53 availability
        port_test = self._check_port(53)
        tests['port_53_availability'] = port_test
        
        return tests
    
    def generate_full_report(self, dns_server=None, database=None) -> str:
        """Generate comprehensive diagnostics report"""
        report = []
        report.append("=" * 60)
        report.append("DNS SERVER MANAGER - DIAGNOSTICS REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        
        # System Information
        report.append("🖥️ SYSTEM INFORMATION")
        report.append("-" * 30)
        sys_info = self.get_system_info()
        for key, value in sys_info.items():
            if key != "error":
                report.append(f"{key.replace('_', ' ').title()}: {value}")
        report.append("")
        
        # Network Information
        report.append("🌐 NETWORK INFORMATION")
        report.append("-" * 30)
        net_info = self.get_network_info()
        for key, value in net_info.items():
            if key != "error" and key != "interfaces":
                report.append(f"{key.replace('_', ' ').title()}: {value}")
        
        if "interfaces" in net_info:
            report.append("\nNetwork Interfaces:")
            for interface, ips in net_info["interfaces"].items():
                if ips:
                    report.append(f"  {interface}: {', '.join(ips)}")
        report.append("")
        
        # Process Information
        report.append("⚙️ PROCESS INFORMATION")
        report.append("-" * 30)
        proc_info = self.get_process_info()
        for key, value in proc_info.items():
            if key != "error":
                report.append(f"{key.replace('_', ' ').title()}: {value}")
        report.append("")
        
        # DNS Server Information
        report.append("🔌 DNS SERVER INFORMATION")
        report.append("-" * 30)
        dns_info = self.get_dns_server_info(dns_server)
        for key, value in dns_info.items():
            if key != "error":
                report.append(f"{key.replace('_', ' ').title()}: {value}")
        report.append("")
        
        # Database Information
        report.append("💾 DATABASE INFORMATION")
        report.append("-" * 30)
        db_info = self.get_database_info(database)
        for key, value in db_info.items():
            if key != "error":
                report.append(f"{key.replace('_', ' ').title()}: {value}")
        report.append("")
        
        # Connectivity Tests
        report.append("🔍 CONNECTIVITY TESTS")
        report.append("-" * 30)
        tests = self.run_connectivity_tests()
        for test_name, result in tests.items():
            status = result.get("status", "UNKNOWN")
            report.append(f"{test_name.replace('_', ' ').title()}: {status}")
            if "error" in result:
                report.append(f"  Error: {result['error']}")
            elif "result" in result:
                report.append(f"  Result: {result['result']}")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 30)
        recommendations = self._generate_recommendations(sys_info, net_info, dns_info, tests)
        for rec in recommendations:
            report.append(f"• {rec}")
        
        report.append("")
        report.append("=" * 60)
        report.append("END OF DIAGNOSTICS REPORT")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def _check_port(self, port: int) -> Dict[str, Any]:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    return {"status": "IN_USE", "message": f"Port {port} is already in use"}
                else:
                    return {"status": "AVAILABLE", "message": f"Port {port} is available"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def _get_dns_servers(self) -> List[str]:
        """Get system DNS servers"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['nslookup'], capture_output=True, text=True, timeout=5)
                # Parse DNS servers from nslookup output
                lines = result.stderr.split('\n')
                dns_servers = []
                for line in lines:
                    if 'Server:' in line:
                        dns_server = line.split('Server:')[1].strip()
                        if dns_server:
                            dns_servers.append(dns_server)
                return dns_servers
            else:
                # For Linux/Mac, read /etc/resolv.conf
                with open('/etc/resolv.conf', 'r') as f:
                    dns_servers = []
                    for line in f:
                        if line.startswith('nameserver'):
                            dns_servers.append(line.split()[1])
                    return dns_servers
        except:
            return ["Unable to determine"]
    
    def _get_uptime(self, dns_server) -> str:
        """Get DNS server uptime"""
        try:
            if hasattr(dns_server, 'start_time'):
                uptime_seconds = datetime.now().timestamp() - dns_server.start_time
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
            else:
                return "Unknown"
        except:
            return "Unknown"
    
    def _generate_recommendations(self, sys_info: Dict, net_info: Dict, dns_info: Dict, tests: Dict) -> List[str]:
        """Generate recommendations based on diagnostics"""
        recommendations = []
        
        # Check DNS server status
        if dns_info.get("is_running") is False:
            recommendations.append("Start the DNS server to begin accepting queries")
        
        # Check port 53
        if net_info.get("port_53_status", {}).get("status") == "IN_USE":
            recommendations.append("Port 53 is already in use. Check for other DNS services running")
        
        # Check memory
        if "memory_available" in sys_info:
            try:
                available_gb = float(sys_info["memory_available"].split()[0])
                if available_gb < 1.0:
                    recommendations.append("Low available memory. Consider closing other applications")
            except:
                pass
        
        # Check connectivity
        if tests.get("localhost_resolution", {}).get("status") == "FAIL":
            recommendations.append("Local DNS resolution failed. Check network configuration")
        
        if tests.get("google_dns_connectivity", {}).get("status") == "FAIL":
            recommendations.append("Cannot connect to external DNS servers. Check internet connection")
        
        if not recommendations:
            recommendations.append("All systems appear to be functioning normally")
        
        return recommendations
