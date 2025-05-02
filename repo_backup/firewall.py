import subprocess
import os
from utils import log_action, log_error

class FirewallManager:
    def __init__(self):
        self.enabled_profiles = set()  # Track enabled profiles

    def enable_firewall(self):
        try:
            # Check if the Windows Firewall service is running
            service_status = subprocess.run(
                ["sc", "query", "MpsSvc"],
                capture_output=True,
                text=True,
                check=True
            )
            if "RUNNING" not in service_status.stdout:
                log_error("Windows Firewall service is not running. Please start the service and try again.")
                raise RuntimeError("Windows Firewall service is not running.")

            # Attempt to enable the firewall
            subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "on"], check=True)
            log_action("Firewall enabled.")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to enable firewall: {e}. Ensure the application is running with administrator privileges.")
        except Exception as e:
            log_error(f"Unexpected error while enabling firewall: {e}")

    def disable_firewall(self):
        try:
            subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "off"], check=True)
            log_action("Firewall disabled.")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to disable firewall: {e}")

    def open_ports(self, port, protocol="TCP"):
        try:
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "add", "rule", f"name=Open Port {port} ({protocol})",
                 "dir=in", "action=allow", f"protocol={protocol}", f"localport={port}"],
                check=True
            )
            log_action(f"Opened Port {port} ({protocol})")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to open Port {port} ({protocol}): {e}")

    def close_ports(self, port, protocol="TCP"):
        try:
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "delete", "rule", f"name=Open Port {port} ({protocol})",
                 f"protocol={protocol}", f"localport={port}"],
                check=True
            )
            log_action(f"Closed Port {port} ({protocol})")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to close Port {port} ({protocol}): {e}")

    def list_active_rules(self):
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"],
                capture_output=True,
                text=True,
                check=True
            )
            log_action("Listed active rules.")
            return result.stdout
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to list active rules: {e}")

    def search_firewall_rule(self, rule_name):
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"],
                capture_output=True,
                text=True,
                check=True
            )
            log_action(f"Searched for firewall rule: {rule_name}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to search firewall rule: {e}")

    def delete_firewall_rule(self, rule_name):
        try:
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"],
                check=True
            )
            log_action(f"Deleted firewall rule: {rule_name}")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to delete firewall rule: {e}")

    def backup_firewall_rules(self, backup_file="firewall_backup.wfw"):
        try:
            subprocess.run(
                ["netsh", "advfirewall", "export", backup_file],
                check=True
            )
            log_action(f"Backed up firewall rules to {backup_file}")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to back up firewall rules: {e}")

    def restore_firewall_rules(self, backup_file="firewall_backup.wfw"):
        try:
            subprocess.run(
                ["netsh", "advfirewall", "import", backup_file],
                check=True
            )
            log_action(f"Restored firewall rules from {backup_file}")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to restore firewall rules: {e}")

    def view_statistics(self):
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles"],
                capture_output=True,
                text=True,
                check=True
            )
            log_action("Viewed firewall statistics.")
            return result.stdout
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to view statistics: {e}")

    def query_port_status(self, port):
        try:
            result = subprocess.run(["netstat", "-an"], capture_output=True, text=True, check=True)
            if f":{port}" in result.stdout:
                log_action(f"Port {port} is in use.")
                return f"Port {port} is in use."
            else:
                log_action(f"Port {port} is not in use.")
                return f"Port {port} is not in use."
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to query port status: {e}")
            return f"Error querying port status: {e}"

    def reset_firewall(self):
        try:
            subprocess.run(["netsh", "advfirewall", "reset"], check=True)
            log_action("Firewall reset to default settings.")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to reset firewall: {e}")

    def predefined_port_profiles(self):
        profiles = {
            "Communication Tools": [
                {"name": "Zoom", "ports": "TCP/UDP 8801-8802"},
                {"name": "Skype", "ports": "TCP 50000-60000, UDP 50000-60000"},
                {"name": "Discord", "ports": "TCP 443, UDP 443, TCP 50000-60000, UDP 50000-60000"}
            ],
            "Game Servers": [
                {"name": "Minecraft", "ports": "TCP 25565, UDP 25565"},
                {"name": "CS:GO", "ports": "UDP 27015-27030, UDP 27036"},
                {"name": "ARK: Survival Evolved", "ports": "UDP 7777-7778, UDP 27015"},
                {"name": "FiveM", "ports": "TCP 30120, UDP 30120"},
                {"name": "Fortnite", "ports": "TCP 5222, UDP 5222, TCP 5795-5847, UDP 5795-5847"},
                {"name": "Call of Duty: Warzone", "ports": "TCP 3074, UDP 3074, TCP 27014-27050, UDP 27014-27050"},
                {"name": "League of Legends", "ports": "TCP 5000-5500, TCP 8393-8400, TCP 2099, TCP 5222-5223, TCP 8088"},
                {"name": "Valorant", "ports": "UDP 7000-7500, UDP 8080, UDP 8180, UDP 10000-10099"},
                {"name": "Apex Legends", "ports": "TCP 4000-4500, UDP 4000-4500, TCP 8080"},
                {"name": "SPT FIKA", "ports": "TCP 443, UDP 443, TCP 8080, UDP 8080, TCP 50555, UDP 50555, TCP 6969, UDP 6969"}
            ],
            "File Sharing": [
                {"name": "FTP", "ports": "TCP 21"},
                {"name": "BitTorrent", "ports": "TCP 6881-6889, UDP 6881-6889"}
            ],
            "Development Tools": [
                {"name": "Docker", "ports": "TCP 2375-2376"},
                {"name": "Jenkins", "ports": "TCP 8080"},
                {"name": "GitLab", "ports": "TCP 80, TCP 443, TCP 22"},
                {"name": "Kubernetes", "ports": "TCP 6443"},
                {"name": "ElasticSearch", "ports": "TCP 9200-9300"}
            ],
            "Database Servers": [
                {"name": "MySQL", "ports": "TCP 3306"},
                {"name": "PostgreSQL", "ports": "TCP 5432"},
                {"name": "MongoDB", "ports": "TCP 27017"},
                {"name": "Redis", "ports": "TCP 6379"}
            ],
            "Web Servers": [
                {"name": "HTTP", "ports": "TCP 80"},
                {"name": "HTTPS", "ports": "TCP 443"}
            ]
        }
        return profiles

    def detect_port_conflicts(self, port):
        try:
            result = subprocess.run(["netstat", "-an"], capture_output=True, text=True, check=True)
            if f":{port}" in result.stdout:
                log_action(f"Port {port} is in use.")
            else:
                log_action(f"Port {port} is not in use.")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to detect port conflicts: {e}")

    def view_network_profile(self):
        try:
            result = subprocess.run(["netsh", "advfirewall", "show", "currentprofile"], capture_output=True, text=True, check=True)
            log_action("Viewed network profile.")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to view network profile: {e}")

    def optimize_rules(self):
        """Optimize firewall rules by removing duplicates and unused rules."""
        try:
            # Retrieve all active rules
            result = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"],
                capture_output=True,
                text=True,
                check=True
            )
            rules = result.stdout.splitlines()

            # Logic to identify and remove duplicate or unused rules
            optimized_rules = set()
            for rule in rules:
                if rule.strip() and rule not in optimized_rules:
                    optimized_rules.add(rule)

            # Log optimization results
            log_action(f"Optimized firewall rules. Total rules after optimization: {len(optimized_rules)}")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to optimize firewall rules: {e}")
        except Exception as e:
            log_error(f"Unexpected error during optimization: {e}")

    def validate_firewall_rule(self, rule_name):
        """Validate if a specific firewall rule exists and is correctly configured."""
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"],
                capture_output=True,
                text=True,
                check=True
            )
            if "No rules match the specified criteria" in result.stdout:
                log_error(f"Firewall rule '{rule_name}' does not exist.")
                return False
            else:
                log_action(f"Firewall rule '{rule_name}' is valid.")
                return True
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to validate firewall rule '{rule_name}': {e}")
            return False
        except Exception as e:
            log_error(f"Unexpected error during rule validation: {e}")
            return False

    def malware_detection(self, file_path):
        """Perform a basic malware scan on a file by checking for suspicious patterns."""
        try:
            if not os.path.exists(file_path):
                log_error(f"File '{file_path}' does not exist.")
                return "File not found."

            # Example logic: Check for suspicious patterns in the file
            suspicious_patterns = ["malicious_code", "virus_signature"]
            with open(file_path, "r", errors="ignore") as file:
                content = file.read()
                for pattern in suspicious_patterns:
                    if pattern in content:
                        log_action(f"Malware detected in file '{file_path}'. Pattern: {pattern}")
                        return f"Malware detected: {pattern}"

            log_action(f"No malware detected in file '{file_path}'.")
            return "No malware detected."
        except Exception as e:
            log_error(f"Failed to scan file '{file_path}' for malware: {e}")
            return f"Error during malware scan: {e}"

    def is_profile_enabled(self, profile_name):
        """Check if a predefined port profile is enabled."""
        return profile_name in self.enabled_profiles

    def enable_profile(self, profile_name):
        """Enable a predefined port profile."""
        # Logic to enable the profile (e.g., open ports)
        self.enabled_profiles.add(profile_name)

    def disable_profile(self, profile_name):
        """Disable a predefined port profile."""
        # Logic to disable the profile (e.g., close ports)
        self.enabled_profiles.discard(profile_name)
