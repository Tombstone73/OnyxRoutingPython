"""
Routing tab for Titan Automation
Handles routing configuration and analysis
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class RoutingTab(ctk.CTkFrame):
    """Routing tab containing routing configuration interfaces"""
    
    def __init__(self, parent, config_manager, routing_engine):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        self.config_manager = config_manager
        self.routing_engine = routing_engine
        
        # Build UI
        self.build_ui()
    
    def build_ui(self):
        """Build the routing interface"""
        try:
            # Main container
            main_container = ctk.CTkFrame(self)
            main_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Top section - Printer selection and controls
            top_section = ctk.CTkFrame(main_container)
            top_section.pack(fill="x", pady=(0, 10))
            
            # Printer selection
            printer_frame = ctk.CTkFrame(top_section)
            printer_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            ctk.CTkLabel(printer_frame, text="Select Printer for Routing:", 
                        font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
            
            self.routing_printer_var = tk.StringVar()
            printer_selection_frame = ctk.CTkFrame(printer_frame)
            printer_selection_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            active_printers = self.config_manager.get_active_printers()
            for printer in active_printers:
                ctk.CTkRadioButton(printer_selection_frame, text=printer, 
                                 variable=self.routing_printer_var, value=printer).pack(side="left", padx=10)
            
            if active_printers:
                self.routing_printer_var.set(active_printers[0])
            
            # Control buttons
            control_frame = ctk.CTkFrame(top_section, width=200)
            control_frame.pack(side="right", fill="y")
            control_frame.pack_propagate(False)
            
            ctk.CTkLabel(control_frame, text="Actions", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
            
            buttons = [
                ("Scan Folders", "#4CAF50", "#45a049"),
                ("Auto-Map", "#2196F3", "#0D47A1"),
                ("Save Routing", "#FF9800", "#F57C00"),
                ("Test Routes", "#9C27B0", "#7B1FA2")
            ]
            
            for text, fg_color, hover_color in buttons:
                ctk.CTkButton(control_frame, text=text, 
                             fg_color=fg_color, hover_color=hover_color,
                             command=lambda t=text: self.handle_action(t)).pack(fill="x", padx=10, pady=2)
            
            # Status display
            self.status_label = ctk.CTkLabel(control_frame, text="Select printer and scan folders", wraplength=180)
            self.status_label.pack(fill="x", padx=10, pady=10)
            
            # Content area with tabs
            content_frame = ctk.CTkFrame(main_container)
            content_frame.pack(fill="both", expand=True)
            
            # Create tabview for routing content
            self.routing_tabview = ctk.CTkTabview(content_frame)
            self.routing_tabview.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create routing sub-tabs (placeholders)
            self.folder_overview_tab = self.routing_tabview.add("Folder Overview")
            self.route_builder_tab = self.routing_tabview.add("Route Builder")
            self.rules_management_tab = self.routing_tabview.add("Rules Management")
            self.analysis_tab = self.routing_tabview.add("Analysis")
            
            # Build placeholder content
            self.build_placeholder_routing_content()
            
        except Exception as e:
            print(f"Error building routing UI: {e}")
    
    def build_placeholder_routing_content(self):
        """Build placeholder content for routing tabs"""
        tabs = [
            (self.folder_overview_tab, "Folder Overview"),
            (self.route_builder_tab, "Route Builder"),
            (self.rules_management_tab, "Rules Management"),
            (self.analysis_tab, "Routing Analysis")
        ]
        
        for tab, title in tabs:
            placeholder_frame = ctk.CTkFrame(tab)
            placeholder_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(placeholder_frame, text=title, 
                        font=ctk.CTkFont(weight="bold", size=16)).pack(pady=20)
            
            ctk.CTkLabel(placeholder_frame, 
                        text="This routing section will be implemented\nwhen migrating from the original code.",
                        font=ctk.CTkFont(style="italic")).pack(pady=10)
    
    def handle_action(self, action):
        """Handle action button clicks"""
        actions = {
            "Scan Folders": "Folder scanning functionality coming soon!",
            "Auto-Map": "Auto-mapping functionality coming soon!",
            "Save Routing": "Routing save functionality coming soon!",
            "Test Routes": "Route testing functionality coming soon!"
        }
        
        message = actions.get(action, "Unknown action")
        messagebox.showinfo(action, message)
        self.status_label.configure(text=f"{action} clicked")
    
    def refresh_from_config(self):
        """Refresh UI from configuration changes"""
        try:
            # Refresh printer selection
            active_printers = self.config_manager.get_active_printers()
            print("Routing tab refreshed from config")
        except Exception as e:
            print(f"Error refreshing routing tab: {e}")