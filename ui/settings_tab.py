"""
Complete Settings tab for Titan Automation
Handles all configuration management interfaces
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from difflib import SequenceMatcher

from config.constants import FILENAME_COMPONENTS

class SettingsTab(ctk.CTkFrame):
    """Complete settings tab with all configuration interfaces"""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        self.config_manager = config_manager
        
        # Initialize variables
        self.init_variables()
        
        # Build UI
        self.build_ui()
    
    def init_variables(self):
        """Initialize settings variables"""
        # General settings
        self.show_include_panel_var = tk.BooleanVar(value=self.config_manager.get("show_panel", True))
        self.hotfolder_var = tk.StringVar(value=self.config_manager.get_hotfolder_root())
        
        # Client art folder settings
        self.art_root_var = tk.StringVar(value=self.config_manager.get_art_root_path())
        self.enable_art_copy_var = tk.BooleanVar(value=self.config_manager.is_art_copy_enabled())
        self.client_art_mappings = self.config_manager.get_client_art_folders().copy()
        
        # New mapping inputs
        self.new_mapping_client_var = tk.StringVar()
        self.new_mapping_path_var = tk.StringVar()
        
        # New client input
        self.new_client_var = tk.StringVar()
        
        # New media inputs
        self.new_media_group_var = tk.StringVar()
        self.new_media_type_var = tk.StringVar()
        self.selected_media_printer_var = tk.StringVar()
        self.selected_media_group_var = tk.StringVar()
        self.clone_source_var = tk.StringVar()
        
        # Printer widgets storage
        self.printer_widgets = {}
        
        # Component order
        self.filename_components_order = self.config_manager.get("order", [comp[1] for comp in FILENAME_COMPONENTS])
    
    def build_ui(self):
        """Build the complete settings interface"""
        try:
            # Create main container
            main_container = ctk.CTkFrame(self, fg_color="transparent")
            main_container.pack(fill="both", expand=True)
            
            # Create sub-tabview for settings
            self.settings_tabview = ctk.CTkTabview(main_container)
            self.settings_tabview.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create sub-tabs
            self.general_settings_tab = self.settings_tabview.add("General")
            self.printer_settings_tab = self.settings_tabview.add("Printers")
            self.client_settings_tab = self.settings_tabview.add("Clients")
            self.media_settings_tab = self.settings_tabview.add("Media Types")
            self.filename_settings_tab = self.settings_tabview.add("Filename")
            self.client_art_settings_tab = self.settings_tabview.add("Client Art")
            
            # Build each settings section
            self.build_general_settings()
            self.build_printer_settings()
            self.build_client_settings()
            self.build_media_settings()
            self.build_filename_settings()
            self.build_client_art_settings()
            
            # Fixed footer for save button
            footer_frame = ctk.CTkFrame(main_container)
            footer_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            # Save button
            ctk.CTkButton(footer_frame, text="Save All Settings", command=self.save_config, 
                         height=40, font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10, pady=10)
            
            # Status label
            self.settings_status_label = ctk.CTkLabel(footer_frame, text="")
            self.settings_status_label.pack(side="left", padx=10, pady=10)
            
        except Exception as e:
            print(f"Error building settings UI: {e}")
            # Fall back to simple settings
            self.build_settings_ui_simple()
    
    # ===== GENERAL SETTINGS =====
    def build_general_settings(self):
        """Build general settings tab"""
        try:
            content_scroll = ctk.CTkScrollableFrame(self.general_settings_tab)
            content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(content_scroll, text="General Settings", 
                        font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(0, 20), anchor="w")
            
            # Show include panel option
            ctk.CTkCheckBox(content_scroll, text="Show 'Include in Filename' Panel", 
                           variable=self.show_include_panel_var).pack(anchor="w", pady=10)

            # Hotfolder settings
            ctk.CTkLabel(content_scroll, text="Onyx Hotfolder Root:", 
                        font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), anchor="w")
            
            path_row = ctk.CTkFrame(content_scroll)
            path_row.pack(fill="x", pady=(0, 10))
            
            ctk.CTkEntry(path_row, textvariable=self.hotfolder_var).pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkButton(path_row, text="Browse", command=self.browse_hotfolder).pack(side="left")
            ctk.CTkButton(path_row, text="Scan Printers", command=self.scan_hotfolder_printers).pack(side="left", padx=(10, 0))
            
        except Exception as e:
            print(f"Error building general settings: {e}")
    
    # ===== PRINTER SETTINGS =====
    def build_printer_settings(self):
        """Build printer management tab"""
        try:
            content_scroll = ctk.CTkScrollableFrame(self.printer_settings_tab)
            content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(content_scroll, text="Printer Management", 
                        font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(0, 20), anchor="w")
            
            # Scan printers button at the top
            scan_frame = ctk.CTkFrame(content_scroll)
            scan_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(scan_frame, text="Scan hotfolder for printers:", 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
            ctk.CTkButton(scan_frame, text="Scan Printers", command=self.scan_hotfolder_printers, 
                         fg_color="#4CAF50", hover_color="#45a049", width=150).pack(side="left", padx=10, pady=10)
            
            # Printer configuration headers
            printer_header = ctk.CTkFrame(content_scroll)
            printer_header.pack(fill="x", pady=(0, 5))
            
            ctk.CTkLabel(printer_header, text="Folder Name", width=120, 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(printer_header, text="Display Name", width=150, 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(printer_header, text="Roll", width=60, 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(printer_header, text="Flatbed", width=80, 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(printer_header, text="Active", width=60, 
                        font=ctk.CTkFont(weight="bold")).pack(side="left")
            
            # Printer list container
            self.printer_container = ctk.CTkScrollableFrame(content_scroll, height=400)
            self.printer_container.pack(fill="both", expand=True, pady=5)
            
            self.build_printer_management()
            
        except Exception as e:
            print(f"Error building printer settings: {e}")
    
    def build_printer_management(self):
        """Build printer management interface"""
        try:
            # Clear existing widgets
            for widget in self.printer_container.winfo_children():
                widget.destroy()
            
            self.printer_widgets = {}
            printers_config = self.config_manager.get_printers()
            
            for printer_name, pdata in printers_config.items():
                row = ctk.CTkFrame(self.printer_container)
                row.pack(fill="x", pady=4)
                
                # Folder name (non-editable)
                ctk.CTkLabel(row, text=printer_name, width=120, anchor="w").pack(side="left", padx=(0, 10))
                
                # Display name (editable)
                disp_var = tk.StringVar(value=pdata.get("display_name", printer_name))
                ctk.CTkEntry(row, textvariable=disp_var, width=150).pack(side="left", padx=(0, 10))
                
                # Roll checkbox
                roll_var = tk.BooleanVar(value="Roll" in pdata.get("types", []))
                ctk.CTkCheckBox(row, text="", variable=roll_var, width=60).pack(side="left", padx=(0, 10))
                
                # Flatbed checkbox
                flat_var = tk.BooleanVar(value="Flatbed" in pdata.get("types", []))
                ctk.CTkCheckBox(row, text="", variable=flat_var, width=80).pack(side="left", padx=(0, 10))
                
                # Active checkbox
                active_var = tk.BooleanVar(value=pdata.get("active", True))
                ctk.CTkCheckBox(row, text="", variable=active_var, width=60).pack(side="left")
                
                self.printer_widgets[printer_name] = {
                    "display": disp_var, 
                    "roll": roll_var, 
                    "flatbed": flat_var, 
                    "active": active_var
                }
                
        except Exception as e:
            print(f"Error building printer management: {e}")
    
    # ===== CLIENT SETTINGS =====
    def build_client_settings(self):
        """Build client management tab"""
        try:
            content_scroll = ctk.CTkScrollableFrame(self.client_settings_tab)
            content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(content_scroll, text="Client Management", 
                        font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(0, 20), anchor="w")
            
            # Add new client
            add_client_frame = ctk.CTkFrame(content_scroll)
            add_client_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(add_client_frame, text="Add New Client:", 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
            
            ctk.CTkEntry(add_client_frame, textvariable=self.new_client_var, width=300).pack(side="left", padx=10, pady=10)
            ctk.CTkButton(add_client_frame, text="Add Client", command=self.add_new_client).pack(side="left", padx=10, pady=10)
            
            # Client list management
            client_frame = ctk.CTkFrame(content_scroll)
            client_frame.pack(fill="both", expand=True)
            
            ctk.CTkLabel(client_frame, text="Existing Clients:", 
                        font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
            
            list_frame = ctk.CTkFrame(client_frame)
            list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            self.client_listbox = tk.Listbox(list_frame, background="#2a2a2a", foreground="white", 
                                           selectbackground="#1f6aa5", relief="flat", borderwidth=0, height=12)
            self.client_listbox.pack(side="left", fill="both", expand=True)
            
            client_buttons_frame = ctk.CTkFrame(list_frame, width=120)
            client_buttons_frame.pack(side="right", fill="y", padx=(10, 0))
            client_buttons_frame.pack_propagate(False)
            
            ctk.CTkButton(client_buttons_frame, text="Delete Selected", command=self.delete_client).pack(fill="x", padx=5, pady=5)
            
            self.refresh_client_listbox()
            
        except Exception as e:
            print(f"Error building client settings: {e}")
    
    # ===== MEDIA SETTINGS =====
    def build_media_settings(self):
        """Build media type management tab"""
        try:
            content_scroll = ctk.CTkScrollableFrame(self.media_settings_tab)
            content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(content_scroll, text="Media Type Management", 
                        font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(0, 20), anchor="w")
            
            # Printer selection for media configuration
            printer_select_frame = ctk.CTkFrame(content_scroll)
            printer_select_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(printer_select_frame, text="Configure Media For Printer:", 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
            
            active_printers = self.config_manager.get_active_printers()
            self.media_printer_combo = ctk.CTkComboBox(printer_select_frame, variable=self.selected_media_printer_var, 
                                                      values=active_printers, command=self.on_media_printer_change, width=200)
            self.media_printer_combo.pack(side="left", padx=10, pady=10)
            
            if active_printers and not self.selected_media_printer_var.get():
                self.selected_media_printer_var.set(active_printers[0])
            
            # Clone functionality
            clone_frame = ctk.CTkFrame(printer_select_frame)
            clone_frame.pack(side="right", padx=10, pady=10)
            
            ctk.CTkLabel(clone_frame, text="Clone from:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 5))
            
            self.clone_source_combo = ctk.CTkComboBox(clone_frame, variable=self.clone_source_var, 
                                                     values=active_printers, width=150)
            self.clone_source_combo.pack(side="left", padx=5)
            
            ctk.CTkButton(clone_frame, text="Clone Media", command=self.clone_media_config, 
                         fg_color="#FF9800", hover_color="#F57C00", width=100).pack(side="left", padx=5)
            
            # Media group management
            group_frame = ctk.CTkFrame(content_scroll)
            group_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(group_frame, text="Add Media Group:", 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
            ctk.CTkEntry(group_frame, textvariable=self.new_media_group_var, width=200).pack(side="left", padx=10, pady=10)
            ctk.CTkButton(group_frame, text="Add Group", command=self.add_media_group).pack(side="left", padx=10, pady=10)
            
            # Media type management
            type_frame = ctk.CTkFrame(content_scroll)
            type_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(type_frame, text="Media Group:", 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
            self.media_group_combo = ctk.CTkComboBox(type_frame, variable=self.selected_media_group_var, 
                                                    command=self.on_media_group_selection_change, width=150)
            self.media_group_combo.pack(side="left", padx=10, pady=10)
            
            ctk.CTkLabel(type_frame, text="Add Media Type:", 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(20, 10), pady=10)
            ctk.CTkEntry(type_frame, textvariable=self.new_media_type_var, width=200).pack(side="left", padx=10, pady=10)
            ctk.CTkButton(type_frame, text="Add Type", command=self.add_media_type).pack(side="left", padx=10, pady=10)
            
            # Media configuration display
            self.media_config_frame = ctk.CTkScrollableFrame(content_scroll, height=300)
            self.media_config_frame.pack(fill="both", expand=True)
            
            self.refresh_media_display()
            
        except Exception as e:
            print(f"Error building media settings: {e}")
    
    # ===== FILENAME SETTINGS =====
    def build_filename_settings(self):
        """Build filename component settings tab"""
        try:
            content_scroll = ctk.CTkScrollableFrame(self.filename_settings_tab)
            content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(content_scroll, text="Filename Component Settings", 
                        font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(0, 20), anchor="w")
            
            # Component ordering
            order_frame = ctk.CTkFrame(content_scroll)
            order_frame.pack(fill="both", expand=True)
            
            ctk.CTkLabel(order_frame, text="Component Order:", 
                        font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
            
            list_container = ctk.CTkFrame(order_frame)
            list_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            self.order_listbox = tk.Listbox(list_container, background="#2a2a2a", foreground="white", 
                                          selectbackground="#1f6aa5", relief="flat", borderwidth=0, 
                                          height=len(FILENAME_COMPONENTS))
            self.order_listbox.pack(side="left", fill="both", expand=True)
            
            btn_frame = ctk.CTkFrame(list_container, width=120)
            btn_frame.pack(side="right", fill="y", padx=(10, 0))
            btn_frame.pack_propagate(False)
            
            ctk.CTkButton(btn_frame, text="Move Up", command=self.move_order_up).pack(fill="x", padx=5, pady=5)
            ctk.CTkButton(btn_frame, text="Move Down", command=self.move_order_down).pack(fill="x", padx=5, pady=5)
            ctk.CTkButton(btn_frame, text="Reset Order", command=self.reset_component_order).pack(fill="x", padx=5, pady=(20, 5))
            
            self.refresh_order_listbox()
            
        except Exception as e:
            print(f"Error building filename settings: {e}")
    
    # ===== CLIENT ART SETTINGS =====
    def build_client_art_settings(self):
        """Build client art folder settings tab"""
        try:
            content_scroll = ctk.CTkScrollableFrame(self.client_art_settings_tab)
            content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(content_scroll, text="Client Art Folder Settings", 
                        font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(0, 20), anchor="w")
            
            # Enable art copying
            enable_frame = ctk.CTkFrame(content_scroll)
            enable_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkCheckBox(enable_frame, text="Enable copying to client art folders", 
                           variable=self.enable_art_copy_var).pack(anchor="w", padx=10, pady=10)
            
            # Art root path
            root_frame = ctk.CTkFrame(content_scroll)
            root_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(root_frame, text="Client Art Root Path:", 
                        font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
            
            path_row = ctk.CTkFrame(root_frame)
            path_row.pack(fill="x", padx=10, pady=(0, 10))
            
            ctk.CTkEntry(path_row, textvariable=self.art_root_var, 
                        placeholder_text="\\\\server\\art\\ or C:\\ClientArt\\").pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkButton(path_row, text="Browse", command=self.browse_art_root).pack(side="left", padx=(0, 10))
            ctk.CTkButton(path_row, text="Scan", command=self.scan_client_folders).pack(side="left")
            
            # Client mappings
            mapping_frame = ctk.CTkFrame(content_scroll)
            mapping_frame.pack(fill="both", expand=True)
            
            ctk.CTkLabel(mapping_frame, text="Client Folder Mappings:", 
                        font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
            
            # Mapping list container
            self.mapping_container = ctk.CTkScrollableFrame(mapping_frame, height=250)
            self.mapping_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            # Add new mapping
            add_frame = ctk.CTkFrame(mapping_frame)
            add_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            ctk.CTkLabel(add_frame, text="Add mapping:").pack(side="left", padx=10)
            
            client_list = self.config_manager.get_client_list()
            client_combo = ctk.CTkComboBox(add_frame, variable=self.new_mapping_client_var, 
                                          values=client_list, width=150)
            client_combo.pack(side="left", padx=5)
            
            ctk.CTkEntry(add_frame, textvariable=self.new_mapping_path_var, 
                        placeholder_text="Folder path...", width=300).pack(side="left", padx=5)
            
            ctk.CTkButton(add_frame, text="Browse", width=70,
                         command=self.browse_client_art_folder).pack(side="left", padx=5)
            ctk.CTkButton(add_frame, text="Add", width=60,
                         command=self.add_client_mapping).pack(side="left", padx=5)
            
            # Refresh mappings display
            self.refresh_client_mappings()
            
        except Exception as e:
            print(f"Error building client art settings: {e}")
    
    # ===== FALLBACK SIMPLE UI =====
    def build_settings_ui_simple(self):
        """Fallback simple settings UI"""
        try:
            print("Building simple settings UI...")
            
            content_scroll = ctk.CTkScrollableFrame(self)
            content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(content_scroll, text="Settings (Simple Mode)", 
                        font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10, anchor="w")
            
            # Hotfolder setting
            ctk.CTkLabel(content_scroll, text="Hotfolder Root:").pack(anchor="w", pady=(10, 5))
            hotfolder_frame = ctk.CTkFrame(content_scroll)
            hotfolder_frame.pack(fill="x", pady=(0, 20))
            ctk.CTkEntry(hotfolder_frame, textvariable=self.hotfolder_var).pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkButton(hotfolder_frame, text="Browse", command=self.browse_hotfolder).pack(side="left")
            ctk.CTkButton(hotfolder_frame, text="Scan Printers", command=self.scan_hotfolder_printers).pack(side="left", padx=(10, 0))
            
            # Show include panel option
            ctk.CTkCheckBox(content_scroll, text="Show 'Include in Filename' Panel", 
                           variable=self.show_include_panel_var).pack(anchor="w", pady=10)
            
            # Save button
            ctk.CTkButton(content_scroll, text="Save Settings", command=self.save_config, height=40).pack(pady=20)
            
        except Exception as e:
            print(f"Error building simple settings UI: {e}")
    
    # ===== EVENT HANDLERS =====
    
    # General Settings Events
    def browse_hotfolder(self):
        """Browse for hotfolder directory"""
        try:
            path = filedialog.askdirectory(title="Select Hotfolder Root Directory")
            if path:
                self.hotfolder_var.set(path)
        except Exception as e:
            print(f"Error browsing hotfolder: {e}")
    
    def scan_hotfolder_printers(self):
        """Scan hotfolder for printer directories"""
        try:
            hotfolder_path = self.hotfolder_var.get()
            if not hotfolder_path or not os.path.isdir(hotfolder_path):
                messagebox.showerror("Error", "Please set a valid hotfolder root path first.")
                return
            
            # Get all directories in the hotfolder
            printer_folders = [item for item in os.listdir(hotfolder_path) 
                             if os.path.isdir(os.path.join(hotfolder_path, item))]
            
            if not printer_folders:
                messagebox.showwarning("No Printers Found", "No printer folders found in the hotfolder directory.")
                return
            
            # Get current printer config
            current_printers = self.config_manager.get_printers()
            
            # Add new printers found in hotfolder
            for folder_name in printer_folders:
                if folder_name not in current_printers:
                    current_printers[folder_name] = {
                        "display_name": folder_name,
                        "types": ["Roll"],
                        "active": True
                    }
            
            # Remove printers that no longer exist in hotfolder
            existing_printers = list(current_printers.keys())
            missing_printers = [p for p in existing_printers if p not in printer_folders]
            
            if missing_printers:
                remove_missing = messagebox.askyesno(
                    "Missing Printers", 
                    f"The following printers are in your config but not found in the hotfolder:\n\n" +
                    "\n".join(missing_printers) + 
                    "\n\nWould you like to remove them from your configuration?"
                )
                if remove_missing:
                    for printer in missing_printers:
                        del current_printers[printer]
            
            # Update config
            self.config_manager.set("printers", current_printers)
            
            # Rebuild printer management
            self.build_printer_management()
            
            messagebox.showinfo("Scan Complete", 
                              f"Found {len(printer_folders)} printer folders.\n" +
                              "Please review the printer settings and save your configuration.")
        
        except Exception as e:
            messagebox.showerror("Scan Error", f"Error scanning hotfolder: {str(e)}")
    
    # Client Settings Events
    def add_new_client(self):
        """Add new client to list"""
        try:
            new_client = self.new_client_var.get().strip()
            if new_client:
                client_list = self.config_manager.get_client_list()
                if new_client not in client_list:
                    client_list.append(new_client)
                    self.config_manager.set("client_list", client_list)
                    self.refresh_client_listbox()
                    
                    # Update combo boxes that use client list
                    if hasattr(self, 'new_mapping_client_var'):
                        # Find the combo box and update it
                        for widget in self.client_art_settings_tab.winfo_children():
                            self._update_client_combos_recursive(widget, client_list)
                    
                    self.new_client_var.set("")
                    self.set_status_message(f"Client '{new_client}' added.", "#4CAF50")
                else:
                    self.set_status_message("Client name already exists.", "#FF9800")
            else:
                self.set_status_message("Client name cannot be empty.", "#FF9800")
        except Exception as e:
            print(f"Error adding client: {e}")
    
    def _update_client_combos_recursive(self, widget, client_list):
        """Recursively update client combo boxes"""
        try:
            if isinstance(widget, ctk.CTkComboBox) and widget.cget("variable") == str(self.new_mapping_client_var):
                widget.configure(values=client_list)
            
            for child in widget.winfo_children():
                self._update_client_combos_recursive(child, client_list)
        except:
            pass  # Ignore errors in recursive traversal
    
    def delete_client(self):
        """Delete selected client"""
        try:
            selected_indices = self.client_listbox.curselection()
            if not selected_indices:
                return
            
            client_to_delete = self.client_listbox.get(selected_indices[0])
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{client_to_delete}'?"):
                client_list = self.config_manager.get_client_list()
                client_list.remove(client_to_delete)
                self.config_manager.set("client_list", client_list)
                self.refresh_client_listbox()
                
                # Remove from art folder mappings if exists
                if client_to_delete in self.client_art_mappings:
                    del self.client_art_mappings[client_to_delete]
                    self.refresh_client_mappings()
                
        except Exception as e:
            print(f"Error deleting client: {e}")
    
    def refresh_client_listbox(self):
        """Refresh client listbox"""
        try:
            self.client_listbox.delete(0, tk.END)
            client_list = self.config_manager.get_client_list()
            client_list.sort()
            for client in client_list:
                self.client_listbox.insert(tk.END, client)
        except Exception as e:
            print(f"Error refreshing client listbox: {e}")
    
    # Media Settings Events
    def on_media_printer_change(self, *args):
        """Handle printer selection change for media configuration"""
        try:
            self.refresh_media_display()
        except Exception as e:
            print(f"Error handling media printer change: {e}")
    
    def clone_media_config(self):
        """Clone media configuration from one printer to another"""
        try:
            source_printer = self.clone_source_var.get()
            target_printer = self.selected_media_printer_var.get()
            
            if not source_printer or not target_printer:
                messagebox.showerror("Error", "Please select both source and target printers.")
                return
            
            if source_printer == target_printer:
                messagebox.showerror("Error", "Source and target printers cannot be the same.")
                return
            
            # Get printer-specific media config
            printer_media_config = self.config_manager.get("printer_media_config", {})
            
            # Check if source has configuration
            if source_printer not in printer_media_config:
                messagebox.showwarning("No Configuration", f"Printer '{source_printer}' has no media configuration to clone.")
                return
            
            # Clone the configuration
            if messagebox.askyesno("Confirm Clone", 
                                  f"Clone media configuration from '{source_printer}' to '{target_printer}'?\n\n" +
                                  "This will overwrite any existing media configuration for the target printer."):
                
                source_config = printer_media_config[source_printer].copy()
                printer_media_config[target_printer] = source_config
                self.config_manager.set("printer_media_config", printer_media_config)
                
                # Refresh display
                self.refresh_media_display()
                self.set_status_message(f"Media config cloned from {source_printer} to {target_printer}.", "#4CAF50")
                
        except Exception as e:
            print(f"Error cloning media config: {e}")
            messagebox.showerror("Clone Error", f"Error cloning media configuration: {str(e)}")
    
    def add_media_group(self):
        """Add new media group"""
        try:
            new_group = self.new_media_group_var.get().strip()
            selected_printer = self.selected_media_printer_var.get()
            
            if not selected_printer:
                messagebox.showerror("Error", "Please select a printer first.")
                return
            
            if new_group:
                media_config = self.get_printer_media_config(selected_printer)
                if new_group not in media_config:
                    media_config[new_group] = ["Default"]
                    self.set_printer_media_config(selected_printer, media_config)
                    self.new_media_group_var.set("")
                    self.refresh_media_display()
                    self.set_status_message(f"Media group '{new_group}' added to {selected_printer}.", "#4CAF50")
                else:
                    self.set_status_message("Media group already exists for this printer.", "#FF9800")
        except Exception as e:
            print(f"Error adding media group: {e}")
    
    def add_media_type(self):
        """Add new media type"""
        try:
            selected_group = self.selected_media_group_var.get()
            new_type = self.new_media_type_var.get().strip()
            selected_printer = self.selected_media_printer_var.get()
            
            if not selected_printer:
                messagebox.showerror("Error", "Please select a printer first.")
                return
            
            if selected_group and new_type:
                media_config = self.get_printer_media_config(selected_printer)
                if selected_group in media_config:
                    if new_type not in media_config[selected_group]:
                        media_config[selected_group].append(new_type)
                        self.set_printer_media_config(selected_printer, media_config)
                        self.new_media_type_var.set("")
                        self.refresh_media_display()
                        self.set_status_message(f"Media type '{new_type}' added to {selected_group} for {selected_printer}.", "#4CAF50")
                    else:
                        self.set_status_message("Media type already exists in this group.", "#FF9800")
        except Exception as e:
            print(f"Error adding media type: {e}")
    
    def delete_media_group(self, group_name):
        """Delete media group"""
        try:
            selected_printer = self.selected_media_printer_var.get()
            if not selected_printer:
                return
            
            if messagebox.askyesno("Confirm Delete", f"Delete media group '{group_name}' and all its types from {selected_printer}?"):
                media_config = self.get_printer_media_config(selected_printer)
                if group_name in media_config:
                    del media_config[group_name]
                    self.set_printer_media_config(selected_printer, media_config)
                    self.refresh_media_display()
                    self.set_status_message(f"Media group '{group_name}' deleted from {selected_printer}.", "#4CAF50")
        except Exception as e:
            print(f"Error deleting media group: {e}")
    
    def delete_media_type(self, group_name, type_name):
        """Delete media type"""
        try:
            selected_printer = self.selected_media_printer_var.get()
            if not selected_printer:
                return
            
            if messagebox.askyesno("Confirm Delete", f"Delete media type '{type_name}' from {group_name} on {selected_printer}?"):
                media_config = self.get_printer_media_config(selected_printer)
                if group_name in media_config and type_name in media_config[group_name]:
                    media_config[group_name].remove(type_name)
                    self.set_printer_media_config(selected_printer, media_config)
                    self.refresh_media_display()
                    self.set_status_message(f"Media type '{type_name}' deleted from {selected_printer}.", "#4CAF50")
        except Exception as e:
            print(f"Error deleting media type: {e}")
    
    def on_media_group_selection_change(self, *args):
        """Handle media group selection change"""
        pass  # Could be used to filter or highlight the selected group
    
    # Filename Settings Events
    def move_order_up(self):
        """Move selected component up in order"""
        try:
            sel = self.order_listbox.curselection()
            if not sel or sel[0] == 0:
                return
            idx = sel[0]
            self.filename_components_order.insert(idx - 1, self.filename_components_order.pop(idx))
            self.refresh_order_listbox()
            self.order_listbox.selection_set(idx - 1)
        except Exception as e:
            print(f"Error moving order up: {e}")
    
    def move_order_down(self):
        """Move selected component down in order"""
        try:
            sel = self.order_listbox.curselection()
            if not sel or sel[0] == self.order_listbox.size() - 1:
                return
            idx = sel[0]
            self.filename_components_order.insert(idx + 1, self.filename_components_order.pop(idx))
            self.refresh_order_listbox()
            self.order_listbox.selection_set(idx + 1)
        except Exception as e:
            print(f"Error moving order down: {e}")
    
    def reset_component_order(self):
        """Reset component order to default"""
        try:
            if messagebox.askyesno("Reset Order", "Reset filename component order to default?"):
                self.filename_components_order = [comp[1] for comp in FILENAME_COMPONENTS]
                self.refresh_order_listbox()
                self.set_status_message("Component order reset to default.", "#4CAF50")
        except Exception as e:
            print(f"Error resetting component order: {e}")
    
    def refresh_order_listbox(self):
        """Refresh order listbox"""
        try:
            self.order_listbox.delete(0, tk.END)
            for key in self.filename_components_order:
                name, _ = next((c for c in FILENAME_COMPONENTS if c[1] == key), (key, None))
                if name:
                    self.order_listbox.insert(tk.END, name)
        except Exception as e:
            print(f"Error refreshing order listbox: {e}")
    
    # Client Art Settings Events
    def browse_art_root(self):
        """Browse for art root directory"""
        try:
            path = filedialog.askdirectory(title="Select Client Art Root Directory")
            if path:
                self.art_root_var.set(path)
        except Exception as e:
            print(f"Error browsing art root: {e}")
    
    def browse_client_art_folder(self):
        """Browse for individual client art folder"""
        try:
            path = filedialog.askdirectory(title="Select Client Art Folder")
            if path:
                self.new_mapping_path_var.set(path)
        except Exception as e:
            print(f"Error browsing client folder: {e}")
    
    def scan_client_folders(self):
        """Scan art root for client folders"""
        try:
            root_path = self.art_root_var.get().strip()
            if not root_path:
                messagebox.showerror("Error", "Please set the art root path first.")
                return
            
            if not os.path.exists(root_path):
                messagebox.showerror("Error", f"Art root path does not exist:\n{root_path}")
                return
            
            # Get folders in art root
            folders = []
            try:
                for item in os.listdir(root_path):
                    item_path = os.path.join(root_path, item)
                    if os.path.isdir(item_path):
                        folders.append(item)
            except PermissionError:
                messagebox.showerror("Error", f"Permission denied accessing:\n{root_path}")
                return
            
            if not folders:
                messagebox.showinfo("No Folders", "No folders found in the art root directory.")
                return
            
            # Auto-match with existing clients
            matches = self.auto_match_clients(folders)
            
            if matches:
                # Show matching dialog
                self.show_client_matching_dialog(matches)
            else:
                messagebox.showinfo("No Matches", "No automatic matches found between clients and folders.")
            
        except Exception as e:
            print(f"Error scanning client folders: {e}")
            messagebox.showerror("Error", f"Error scanning folders: {str(e)}")
    
    def auto_match_clients(self, folder_list):
        """Auto-match client names with folder names"""
        try:
            matches = {}
            client_list = self.config_manager.get_client_list()
            
            for client in client_list:
                if client in self.client_art_mappings:
                    continue  # Skip already mapped clients
                
                best_match = None
                best_ratio = 0
                
                for folder in folder_list:
                    ratio = SequenceMatcher(None, client.lower(), folder.lower()).ratio()
                    if ratio > best_ratio and ratio > 0.6:  # 60% similarity threshold
                        best_ratio = ratio
                        best_match = folder
                
                if best_match:
                    matches[client] = {
                        'folder': best_match,
                        'ratio': best_ratio,
                        'full_path': os.path.join(self.art_root_var.get(), best_match)
                    }
            
            return matches
            
        except Exception as e:
            print(f"Error auto-matching clients: {e}")
            return {}
    
    def show_client_matching_dialog(self, matches):
        """Show dialog to confirm auto-matched clients"""
        try:
            dialog = ctk.CTkToplevel(self)
            dialog.title("Confirm Client Folder Matches")
            dialog.geometry("600x400")
            dialog.transient(self)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (300)
            y = (dialog.winfo_screenheight() // 2) - (200)
            dialog.geometry(f"+{x}+{y}")
            
            # Header
            header = ctk.CTkLabel(dialog, text="Confirm Auto-Matched Client Folders", 
                                 font=ctk.CTkFont(weight="bold", size=14))
            header.pack(pady=10)
            
            # Matches list
            scroll_frame = ctk.CTkScrollableFrame(dialog, height=250)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            dialog.match_vars = {}
            
            for client, match_info in matches.items():
                match_frame = ctk.CTkFrame(scroll_frame)
                match_frame.pack(fill="x", pady=5)
                
                # Checkbox for this match
                var = tk.BooleanVar(value=True)
                dialog.match_vars[client] = var
                
                checkbox = ctk.CTkCheckBox(match_frame, text="", variable=var, width=30)
                checkbox.pack(side="left", padx=10)
                
                # Match info
                info_text = f"{client} → {match_info['folder']} ({match_info['ratio']:.0%} match)"
                ctk.CTkLabel(match_frame, text=info_text, anchor="w").pack(side="left", fill="x", expand=True, padx=10)
            
            # Buttons
            button_frame = ctk.CTkFrame(dialog)
            button_frame.pack(fill="x", padx=20, pady=10)
            
            def apply_matches():
                for client, var in dialog.match_vars.items():
                    if var.get() and client in matches:
                        self.client_art_mappings[client] = matches[client]['full_path']
                
                self.refresh_client_mappings()
                dialog.destroy()
                messagebox.showinfo("Success", f"Added {sum(v.get() for v in dialog.match_vars.values())} client mappings.")
            
            ctk.CTkButton(button_frame, text="Apply Selected", command=apply_matches).pack(side="left", padx=10)
            ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=10)
            
        except Exception as e:
            print(f"Error showing matching dialog: {e}")
    
    def add_client_mapping(self):
        """Add new client mapping"""
        try:
            client = self.new_mapping_client_var.get().strip()
            path = self.new_mapping_path_var.get().strip()
            
            if not client:
                messagebox.showerror("Error", "Please select a client.")
                return
            
            if not path:
                messagebox.showerror("Error", "Please enter a folder path.")
                return
            
            if not os.path.exists(path):
                if not messagebox.askyesno("Folder Not Found", 
                                         f"The folder does not exist:\n{path}\n\nAdd mapping anyway?"):
                    return
            
            self.client_art_mappings[client] = path
            self.new_mapping_client_var.set("")
            self.new_mapping_path_var.set("")
            self.refresh_client_mappings()
            
            self.set_status_message(f"Added mapping for {client}.", "#4CAF50")
            
        except Exception as e:
            print(f"Error adding client mapping: {e}")
    
    def delete_client_mapping(self, client):
        """Delete client mapping"""
        try:
            if messagebox.askyesno("Confirm Delete", f"Delete art folder mapping for '{client}'?"):
                del self.client_art_mappings[client]
                self.refresh_client_mappings()
        except Exception as e:
            print(f"Error deleting client mapping: {e}")
    
    # ===== REFRESH METHODS =====
    def refresh_media_display(self):
        """Refresh media configuration display"""
        try:
            # Clear existing content
            for widget in self.media_config_frame.winfo_children():
                widget.destroy()
            
            selected_printer = self.selected_media_printer_var.get()
            if not selected_printer:
                ctk.CTkLabel(self.media_config_frame, text="Please select a printer to configure media types.", 
                           font=ctk.CTkFont(style="italic")).pack(pady=50)
                return
            
            # Get media config for selected printer
            media_config = self.get_printer_media_config(selected_printer)
            
            # Header
            header_frame = ctk.CTkFrame(self.media_config_frame)
            header_frame.pack(fill="x", padx=10, pady=(10, 20))
            ctk.CTkLabel(header_frame, text=f"Media Configuration for: {selected_printer}", 
                        font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10)
            
            # Update combo box values
            groups = list(media_config.keys())
            self.media_group_combo.configure(values=groups)
            if groups and not self.selected_media_group_var.get():
                self.selected_media_group_var.set(groups[0])
            
            # Display current configuration
            for group, types in media_config.items():
                group_frame = ctk.CTkFrame(self.media_config_frame)
                group_frame.pack(fill="x", padx=10, pady=5)
                
                # Group header
                header_frame = ctk.CTkFrame(group_frame)
                header_frame.pack(fill="x", padx=10, pady=(10, 5))
                
                ctk.CTkLabel(header_frame, text=group, font=ctk.CTkFont(weight="bold")).pack(side="left")
                ctk.CTkButton(header_frame, text="Delete Group", width=100, 
                             command=lambda g=group: self.delete_media_group(g)).pack(side="right", padx=5)
                
                # Types
                types_frame = ctk.CTkFrame(group_frame)
                types_frame.pack(fill="x", padx=10, pady=(0, 10))
                
                for media_type in types:
                    type_row = ctk.CTkFrame(types_frame)
                    type_row.pack(fill="x", padx=5, pady=2)
                    
                    ctk.CTkLabel(type_row, text=f"  • {media_type}", anchor="w").pack(side="left", fill="x", expand=True, padx=10)
                    ctk.CTkButton(type_row, text="Delete", width=80, 
                                 command=lambda g=group, t=media_type: self.delete_media_type(g, t)).pack(side="right", padx=5)
                
        except Exception as e:
            print(f"Error refreshing media display: {e}")
    
    def refresh_client_mappings(self):
        """Refresh the client mappings display"""
        try:
            # Clear existing widgets
            for widget in self.mapping_container.winfo_children():
                widget.destroy()
            
            if not self.client_art_mappings:
                ctk.CTkLabel(self.mapping_container, text="No client mappings configured.", 
                            font=ctk.CTkFont(style="italic")).pack(pady=20)
                return
            
            # Header
            header_frame = ctk.CTkFrame(self.mapping_container)
            header_frame.pack(fill="x", padx=5, pady=(0, 10))
            
            ctk.CTkLabel(header_frame, text="Client", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Art Folder Path", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            
            # Mappings
            for client, folder_path in self.client_art_mappings.items():
                mapping_frame = ctk.CTkFrame(self.mapping_container)
                mapping_frame.pack(fill="x", padx=5, pady=2)
                
                # Client name
                ctk.CTkLabel(mapping_frame, text=client, width=150, anchor="w").pack(side="left", padx=5)
                
                # Folder path
                path_label = ctk.CTkLabel(mapping_frame, text=folder_path, anchor="w")
                path_label.pack(side="left", fill="x", expand=True, padx=5)
                
                # Status indicator
                if os.path.exists(folder_path):
                    status_color = "#4CAF50"
                    status_text = "✓"
                else:
                    status_color = "#F44336" 
                    status_text = "✗"
                
                ctk.CTkLabel(mapping_frame, text=status_text, width=30, text_color=status_color).pack(side="left")
                
                # Delete button
                ctk.CTkButton(mapping_frame, text="Delete", width=60, height=25,
                             command=lambda c=client: self.delete_client_mapping(c)).pack(side="right", padx=5)
            
        except Exception as e:
            print(f"Error refreshing client mappings: {e}")
    
    # ===== UTILITY METHODS =====
    def get_printer_media_config(self, printer_name):
        """Get media configuration for a specific printer"""
        try:
            printer_media_config = self.config_manager.get("printer_media_config", {})
            
            # If printer doesn't have specific config, use default
            if printer_name not in printer_media_config:
                return self.config_manager.get_media_config().copy()
            
            return printer_media_config[printer_name]
        except Exception as e:
            print(f"Error getting printer media config: {e}")
            return self.config_manager.get_media_config().copy()

    def set_printer_media_config(self, printer_name, media_config):
        """Set media configuration for a specific printer"""
        try:
            printer_media_config = self.config_manager.get("printer_media_config", {})
            printer_media_config[printer_name] = media_config
            self.config_manager.set("printer_media_config", printer_media_config)
        except Exception as e:
            print(f"Error setting printer media config: {e}")
    
    def set_status_message(self, message, color="#4CAF50"):
        """Set status message with color"""
        try:
            if hasattr(self, 'settings_status_label'):
                self.settings_status_label.configure(text=message, text_color=color)
                self.after(3000, lambda: self.settings_status_label.configure(text=""))
        except Exception as e:
            print(f"Error setting status message: {e}")
    
    # ===== SAVE CONFIGURATION =====
    def save_config(self):
        """Save all configuration changes"""
        try:
            # Update printer settings from widgets
            if hasattr(self, 'printer_widgets'):
                printers_config = self.config_manager.get_printers()
                for printer_name, widgets in self.printer_widgets.items():
                    if printer_name in printers_config:
                        printers_config[printer_name]["display_name"] = widgets["display"].get()
                        types = []
                        if widgets["roll"].get():
                            types.append("Roll")
                        if widgets["flatbed"].get():
                            types.append("Flatbed")
                        printers_config[printer_name]["types"] = types
                        printers_config[printer_name]["active"] = widgets["active"].get()
                self.config_manager.set("printers", printers_config)
            
            # Update all settings
            updates = {
                "show_panel": self.show_include_panel_var.get(),
                "hotfolder_root": self.hotfolder_var.get(),
                "art_root_path": self.art_root_var.get(),
                "client_art_folders": self.client_art_mappings,
                "enable_art_copy": self.enable_art_copy_var.get(),
                "order": self.filename_components_order
            }
            
            self.config_manager.update(updates)
            
            # Save to file
            success = self.config_manager.save_config()
            
            if success:
                self.set_status_message("Settings saved successfully!", "#4CAF50")
            else:
                self.set_status_message("Failed to save settings.", "#F44336")
                
        except Exception as e:
            print(f"Error saving config: {e}")
            messagebox.showerror("Save Error", f"Error saving settings: {str(e)}")
    
    def refresh_from_config(self):
        """Refresh UI from configuration changes"""
        try:
            # Reload values from config
            self.show_include_panel_var.set(self.config_manager.get("show_panel", True))
            self.hotfolder_var.set(self.config_manager.get_hotfolder_root())
            self.art_root_var.set(self.config_manager.get_art_root_path())
            self.enable_art_copy_var.set(self.config_manager.is_art_copy_enabled())
            self.client_art_mappings = self.config_manager.get_client_art_folders().copy()
            self.filename_components_order = self.config_manager.get("order", [comp[1] for comp in FILENAME_COMPONENTS])
            
            # Refresh displays
            self.refresh_client_listbox()
            self.refresh_client_mappings()
            self.refresh_order_listbox()
            if hasattr(self, 'media_config_frame'):
                self.refresh_media_display()
            if hasattr(self, 'printer_container'):
                self.build_printer_management()
            
            print("Settings tab refreshed from config")
            
        except Exception as e:
            print(f"Error refreshing settings tab: {e}")
