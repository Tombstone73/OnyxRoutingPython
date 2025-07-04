"""
Constants and default values for Titan Automation
"""

# Configuration file name
CONFIG_FILE = "titan_automation_config.json"

# Filename components definition
FILENAME_COMPONENTS = [
    ("Job Number", "job_number"),
    ("Client Name", "client"),
    ("Size (WxH)", "size"),
    ("Quantity", "quantity"),
    ("Finish", "finish"),
    ("Bleed", "bleed"),
    ("Rotation", "rotation"),
    ("Registration", "registration"),
    ("Grommets", "grommets"),
    ("Pole Pockets", "pole_pockets"),
    ("Mirror", "mirror"),
    ("Date (MM-DD-YY)", "date"),
    ("Custom Text", "custom_text"),
]

# Default printer configuration
DEFAULT_PRINTERS = {
    "Canon": {"display_name": "Canon", "types": ["Roll", "Flatbed"], "active": True},
    "S60": {"display_name": "S60", "types": ["Roll"], "active": True},
    "S40": {"display_name": "S40", "types": ["Roll"], "active": True},
    "Jetson": {"display_name": "Jetson", "types": ["Flatbed"], "active": True}
}

# Default media configuration
DEFAULT_MEDIA_CONFIG = {
    "Vinyl": ["Glossy", "Matte", "Satin"],
    "Banner": ["Scrim", "Mesh", "Blockout"],
    "Paper": ["Cardstock", "Photo Paper", "Canvas"]
}

# Default client list
DEFAULT_CLIENTS = ["Client A", "Client B", "Client C"]

# User presets
DEFAULT_PRESETS = ["Banner Standard", "Banner 38\""]

# Default complete configuration
DEFAULT_CONFIG = {
    "client_list": DEFAULT_CLIENTS,
    "printers": DEFAULT_PRINTERS,
    "media_config": DEFAULT_MEDIA_CONFIG,
    "printer_media_config": {},
    "hotfolder_root": "",
    "art_root_path": "",
    "client_art_folders": {},
    "enable_art_copy": True,
    "routing_rules": {},
    "show_panel": True,
    "include_vars": {comp[1]: True for comp in FILENAME_COMPONENTS},
    "order": [comp[1] for comp in FILENAME_COMPONENTS]
}

# UI Constants
WINDOW_TITLE = "Titan Automation Suite"
WINDOW_SIZE = "1150x950"
UI_THEME = "dark-blue"
UI_MODE = "Dark"