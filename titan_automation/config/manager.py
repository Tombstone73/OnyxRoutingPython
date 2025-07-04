"""
Configuration management for Titan Automation
Handles loading, saving, and accessing configuration data
"""
import json
import os
from .constants import DEFAULT_CONFIG, CONFIG_FILE

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            print("No config file found, using defaults")
            return DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            config = DEFAULT_CONFIG.copy()
            config.update(loaded_config)
            
            print("Config loaded successfully")
            return config
            
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Config saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
    
    def update(self, updates):
        """Update multiple configuration values"""
        self.config.update(updates)
    
    # Convenience methods for common operations
    def get_printers(self):
        """Get printer configuration"""
        return self.config.get("printers", {})
    
    def get_active_printers(self):
        """Get list of active printer display names"""
        printers = self.get_printers()
        return [pdata.get("display_name", name) 
                for name, pdata in printers.items() 
                if pdata.get("active", True)]
    
    def get_printer_folder_name(self, display_name):
        """Get actual folder name for a printer display name"""
        printers = self.get_printers()
        for folder_name, pdata in printers.items():
            if pdata.get("display_name", folder_name) == display_name:
                return folder_name
        return display_name
    
    def get_media_config(self, printer=None):
        """Get media configuration for a specific printer or default"""
        if printer:
            printer_media = self.config.get("printer_media_config", {})
            if printer in printer_media:
                return printer_media[printer]
        
        return self.config.get("media_config", {})
    
    def get_client_list(self):
        """Get list of clients"""
        return self.config.get("client_list", [])
    
    def get_client_art_folders(self):
        """Get client art folder mappings"""
        return self.config.get("client_art_folders", {})
    
    def get_routing_rules(self, printer=None):
        """Get routing rules for a specific printer or all"""
        rules = self.config.get("routing_rules", {})
        if printer:
            return rules.get(printer, [])
        return rules
    
    def add_routing_rule(self, printer, rule):
        """Add a routing rule for a printer"""
        if "routing_rules" not in self.config:
            self.config["routing_rules"] = {}
        if printer not in self.config["routing_rules"]:
            self.config["routing_rules"][printer] = []
        
        self.config["routing_rules"][printer].append(rule)
    
    def get_filename_components(self):
        """Get filename component configuration"""
        return {
            "order": self.config.get("order", []),
            "include_vars": self.config.get("include_vars", {}),
            "show_panel": self.config.get("show_panel", True)
        }
    
    def is_art_copy_enabled(self):
        """Check if client art copying is enabled"""
        return self.config.get("enable_art_copy", True)
    
    def get_hotfolder_root(self):
        """Get hotfolder root path"""
        return self.config.get("hotfolder_root", "")
    
    def get_art_root_path(self):
        """Get client art root path"""
        return self.config.get("art_root_path", "")