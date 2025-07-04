"""
Complete Job setup interface for Titan Automation
Handles all job input controls, presets, filename preview, and file processing
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime

from models.job import Job
from config.constants import FILENAME_COMPONENTS

class JobSetupTab(ctk.CTkFrame):
    """Complete job setup tab with all functionality"""
    
    def __init__(self, parent, config_manager, routing_engine, filename_generator):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        # Store service references
        self.config_manager = config_manager
        self.routing_engine = routing_engine
        self.filename_generator = filename_generator
        
        # Initialize variables
        self.init_variables()
        
        # Build UI
        self.build_ui()
        
        # Setup variable traces for filename preview
        self.setup_traces()
        
        # Initial filename preview update
        self.update_filename_preview()
    
    def init_variables(self):
        """Initialize all UI variables"""
        # File selection
        self.file_path = ""
        
        # Basic job info
        self.job_prefix = tk.StringVar(value="TIT")
        self.job_suffix = tk.StringVar(value="")
        self.client_var = tk.StringVar(value="")
        
        # Size and quantity
        self.size_w = tk.StringVar(value="24")
        self.size_h = tk.StringVar(value="36")
        self.quantity = tk.StringVar(value="1")
        
        # Print settings
        self.printer_var = tk.StringVar()
        self.print_mode = tk.StringVar(value="Roll")
        self.ssds_mode = tk.StringVar(value="SS")
        
        # Media settings
        self.media_group_var = tk.StringVar(value="Vinyl")
        self.media_var = tk.StringVar(value="Glossy")
        self.job_type_var = tk.StringVar(value="Standard")
        
        # Processing options
        self.bleed = tk.StringVar(value="None")
        self.reg_marks = tk.StringVar(value="None")
        self.rotation = tk.StringVar(value="None")
        self.finish = tk.StringVar(value="Glossy")
        
        # Hardware options
        self.grommets = tk.StringVar(value="None")
        self.pole_pockets = tk.StringVar(value="None")
        self.mirror = tk.StringVar(value="No")
        
        # Custom options
        self.custom_text = tk.StringVar(value="")
        
        # Metadata options
        self.inject_metadata = tk.BooleanVar(value=True)
        self.quickset_override_var = tk.BooleanVar(value=False)
        self.quickset = tk.StringVar(value="QuickSet1")
        
        # Filename preview
        self.filename_preview_var = tk.StringVar()
        self.user_editing_filename = False
        
        # Include filename components
        self.include_filename_vars = {}
        filename_config = self.config_manager.get_filename_components()
        for comp_name, comp_key in FILENAME_COMPONENTS:
            self.include_filename_vars[comp_key] = tk.BooleanVar(
                value=filename_config["include_vars"].get(comp_key, True)
            )
        
        # Set initial printer
        active_printers = self.config_manager.get_active_printers()
        if active_printers:
            self.printer_var.set(active_printers[0])
    
    def build_ui(self):
        """Build the complete job setup interface"""
        try:
            # Main container
            main_frame = ctk.CTkFrame(self)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create main content area and right panel
            content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            content_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            # Right panel for presets and include panel
            right_panel = ctk.CTkFrame(main_frame, width=280, corner_radius=8)
            right_panel.pack(side="right", fill="y")
            right_panel.pack_propagate(False)
            
            # Build sections
            self.build_job_inputs(content_frame)
            self.build_right_panel(right_panel)
            
        except Exception as e:
            print(f"Error building job setup UI: {e}")
    
    # ===== MAIN JOB INPUTS SECTION =====
    def build_job_inputs(self, parent):
        """Build main job input controls"""
        try:
            # Print mode selection
            self.build_print_mode_section(parent)
            
            # Printer selection
            self.build_printer_section(parent)
            
            # Job type and media
            self.build_media_section(parent)
            
            # File selection
            self.build_file_section(parent)
            
            # Job details
            self.build_job_details_section(parent)
            
            # Processing options
            self.build_processing_options_section(parent)
            
            # Filename preview
            self.build_filename_section(parent)
            
            # QuickSet override
            self.build_quickset_section(parent)
            
            # Actions
            self.build_actions_section(parent)
            
        except Exception as e:
            print(f"Error building job inputs: {e}")
    
    def build_print_mode_section(self, parent):
        """Build print mode selection"""
        top_frame = ctk.CTkFrame(parent)
        top_frame.pack(fill="x", pady=(0, 10))
        
        # Print mode
        pm_frame = ctk.CTkFrame(top_frame)
        pm_frame.pack(side="left")
        
        ctk.CTkLabel(pm_frame, text="Print Mode:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkRadioButton(pm_frame, text="Roll", variable=self.print_mode, value="Roll", 
                          command=self.on_print_mode_change).pack(side="left", padx=10)
        ctk.CTkRadioButton(pm_frame, text="Flatbed", variable=self.print_mode, value="Flatbed", 
                          command=self.on_print_mode_change).pack(side="left", padx=10)
        
        # SSDS mode (for flatbed)
        self.ssds_frame = ctk.CTkFrame(top_frame)
        ctk.CTkLabel(self.ssds_frame, text="SSDS:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkRadioButton(self.ssds_frame, text="SS", variable=self.ssds_mode, value="SS").pack(side="left", padx=5)
        ctk.CTkRadioButton(self.ssds_frame, text="DS", variable=self.ssds_mode, value="DS").pack(side="left", padx=5)
        
        self.on_print_mode_change()
    
    def build_printer_section(self, parent):
        """Build printer selection"""
        printer_frame = ctk.CTkFrame(parent)
        printer_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(printer_frame, text="Printer:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 20))
        
        active_printers = self.config_manager.get_active_printers()
        for printer in active_printers:
            ctk.CTkRadioButton(printer_frame, text=printer, variable=self.printer_var, value=printer).pack(side="left", padx=10)
    
    def build_media_section(self, parent):
        """Build job type and media selection"""
        # Job type
        job_type_frame = ctk.CTkFrame(parent)
        job_type_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(job_type_frame, text="Job Type:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 20))
        ctk.CTkComboBox(job_type_frame, values=["Standard", "Rush", "Reprint"], 
                       variable=self.job_type_var, width=150).pack(side="left")
        
        # Media selection
        media_frame = ctk.CTkFrame(parent)
        media_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(media_frame, text="Media Group:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 10))
        
        media_groups = list(self.config_manager.get_media_config().keys())
        ctk.CTkComboBox(media_frame, values=media_groups, variable=self.media_group_var, 
                       command=self.on_media_group_change, width=120).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(media_frame, text="Media:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
        self.media_cb = ctk.CTkComboBox(media_frame, values=[], variable=self.media_var, width=120)
        self.media_cb.pack(side="left")
        
        self.on_media_group_change()
    
    def build_file_section(self, parent):
        """Build file selection"""
        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(pady=10, fill="x")
        
        ctk.CTkButton(file_frame, text="Select PDF File", command=self.pick_file, height=35).pack(side="left", padx=10)
        self.selected_file_label = ctk.CTkLabel(file_frame, text="No file selected")
        self.selected_file_label.pack(side="left", padx=10)
    
    def build_job_details_section(self, parent):
        """Build job details inputs"""
        # Job number
        job_frame = ctk.CTkFrame(parent)
        job_frame.pack(pady=5, fill="x")
        ctk.CTkLabel(job_frame, text="Job Number:", width=110, anchor="w", 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkEntry(job_frame, textvariable=self.job_prefix, width=60).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(job_frame, textvariable=self.job_suffix, width=120).pack(side="left")
        
        # Client
        client_frame = ctk.CTkFrame(parent)
        client_frame.pack(pady=5, fill="x")
        
        ctk.CTkLabel(client_frame, text="Client Name:", width=110, anchor="w", 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        
        client_list = self.config_manager.get_client_list()
        self.client_combo = ctk.CTkComboBox(client_frame, values=client_list, variable=self.client_var, width=300)
        self.client_combo.pack(side="left", padx=10)
        
        ctk.CTkButton(client_frame, text="Save Client", command=self.save_client, width=100).pack(side="left", padx=10)
        
        # Size
        size_row = ctk.CTkFrame(parent)
        size_row.pack(pady=5, fill="x")
        ctk.CTkLabel(size_row, text="Size (W x H):", width=110, anchor="w", 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkEntry(size_row, textvariable=self.size_w, width=60).pack(side="left")
        ctk.CTkLabel(size_row, text="x").pack(side="left", padx=5)
        ctk.CTkEntry(size_row, textvariable=self.size_h, width=60).pack(side="left")
        
        # Quantity
        qty_row = ctk.CTkFrame(parent)
        qty_row.pack(pady=5, fill="x")
        ctk.CTkLabel(qty_row, text="Quantity:", width=110, anchor="w", 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkEntry(qty_row, textvariable=self.quantity, width=100).pack(side="left")
    
    def build_processing_options_section(self, parent):
        """Build processing options with radio buttons"""
        def build_radio_row(label, var, options):
            row = ctk.CTkFrame(parent)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, width=110, anchor="w", 
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            for opt in options:
                ctk.CTkRadioButton(row, text=opt, variable=var, value=opt).pack(side="left", padx=10)
        
        # All processing options
        build_radio_row("Bleed:", self.bleed, ["None", "Bleed"])
        build_radio_row("Registration:", self.reg_marks, ["None", "Graphtec", "iCut"])
        build_radio_row("Rotation:", self.rotation, ["None", "90 CW"])
        build_radio_row("Finish:", self.finish, ["Glossy", "Matte"])
        build_radio_row("Grommets:", self.grommets, ["None", "All", "Top", "Bottom", "Sides", "Corners"])
        build_radio_row("Pole Pockets:", self.pole_pockets, ["None", "Top & Bottom", "Top", "Bottom", "Sides"])
        build_radio_row("Mirror:", self.mirror, ["No", "Yes"])
        
        # Custom text
        custom_text_row = ctk.CTkFrame(parent)
        custom_text_row.pack(pady=5, fill="x")
        ctk.CTkLabel(custom_text_row, text="Custom Text:", width=110, anchor="w", 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkEntry(custom_text_row, textvariable=self.custom_text, width=300).pack(side="left")
    
    def build_filename_section(self, parent):
        """Build filename preview section"""
        filename_frame = ctk.CTkFrame(parent)
        filename_frame.pack(pady=10, fill="x")
        
        ctk.CTkLabel(filename_frame, text="Filename Preview:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.filename_preview_entry = ctk.CTkEntry(filename_frame, textvariable=self.filename_preview_var)
        self.filename_preview_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.filename_preview_entry.bind("<FocusIn>", self.on_filename_focus_in)
        self.filename_preview_entry.bind("<FocusOut>", self.on_filename_focus_out)
    
    def build_quickset_section(self, parent):
        """Build QuickSet override section"""
        self.quickset_override_frame = ctk.CTkFrame(parent)
        self.quickset_override_frame.pack(pady=10, fill="x")
        
        ctk.CTkCheckBox(self.quickset_override_frame, text="QuickSet Override", 
                       variable=self.quickset_override_var, 
                       command=self.on_quickset_override_toggle).pack(side="left", padx=10, pady=10)
        
        quickset_list = ["QuickSet1", "QuickSet2", "QuickSet3"]
        self.quickset_dropdown = ctk.CTkComboBox(self.quickset_override_frame, values=quickset_list, 
                                                variable=self.quickset, width=200)
        self.quickset_dropdown.pack(side="left", padx=20, pady=10)
        
        self.on_quickset_override_toggle()
    
    def build_actions_section(self, parent):
        """Build action buttons and status"""
        actions_frame = ctk.CTkFrame(parent)
        actions_frame.pack(pady=15, fill="x")
        
        # Options
        ctk.CTkCheckBox(actions_frame, text="Inject Metadata into PDF", 
                       variable=self.inject_metadata).pack(anchor="w", padx=10, pady=5)
        
        # Test buttons (for debugging)
        test_frame = ctk.CTkFrame(actions_frame)
        test_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(test_frame, text="🔍 Test Routing", command=self.test_routing, 
                     fg_color="#9C27B0", hover_color="#7B1FA2", width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(test_frame, text="📁 Test Art Copy", command=self.test_art_copy, 
                     fg_color="#FF5722", hover_color="#D84315", width=150).pack(side="left", padx=5)
        
        # Main process button
        ctk.CTkButton(actions_frame, text="Process File", command=self.process_file, 
                     height=40, font=ctk.CTkFont(weight="bold")).pack(pady=10, padx=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(actions_frame, text="")
        self.status_label.pack(pady=10)
    
    # ===== RIGHT PANEL SECTION =====
    def build_right_panel(self, parent):
        """Build right panel with presets and filename components"""
        try:
            # User Presets section
            self.build_presets_section(parent)
            
            # Include in Filename panel
            filename_config = self.config_manager.get_filename_components()
            if filename_config["show_panel"]:
                self.build_include_panel_section(parent)
            
        except Exception as e:
            print(f"Error building right panel: {e}")
    
    def build_presets_section(self, parent):
        """Build user presets section"""
        presets_frame = ctk.CTkFrame(parent)
        presets_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(presets_frame, text="User Presets", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        # Preset buttons
        presets = ["Banner Standard", "Banner 38\""]
        for preset in presets:
            btn = ctk.CTkButton(presets_frame, text=preset, command=lambda p=preset: self.apply_preset(p))
            btn.pack(fill="x", padx=10, pady=2)
        
        # Save Preset button
        ctk.CTkButton(presets_frame, text="Save Preset", command=self.save_preset, 
                     fg_color="#4CAF50", hover_color="#45a049").pack(fill="x", padx=10, pady=(10, 10))
    
    def build_include_panel_section(self, parent):
        """Build include in filename panel section"""
        self.include_panel_frame = ctk.CTkFrame(parent)
        self.include_panel_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.build_include_panel()
    
    def build_include_panel(self):
        """Build the include in filename panel content"""
        try:
            if not hasattr(self, 'include_panel_frame'):
                return
                
            # Clear existing content
            for widget in self.include_panel_frame.winfo_children():
                widget.destroy()
            
            ctk.CTkLabel(self.include_panel_frame, text="Include in Filename", 
                        font=ctk.CTkFont(weight="bold")).pack(pady=10, padx=10)
            
            filename_config = self.config_manager.get_filename_components()
            component_order = filename_config["order"]
            
            for component_key in component_order:
                # Find the display name
                display_name = next((comp[0] for comp in FILENAME_COMPONENTS if comp[1] == component_key), component_key)
                
                if component_key in self.include_filename_vars:
                    ctk.CTkCheckBox(self.include_panel_frame, text=display_name, 
                                   variable=self.include_filename_vars[component_key]).pack(anchor="w", padx=20, pady=5)
        except Exception as e:
            print(f"Error building include panel: {e}")
    
    # ===== FILENAME PREVIEW SECTION =====
    def setup_traces(self):
        """Setup variable traces for filename preview"""
        try:
            variables_to_trace = [
                self.job_prefix, self.job_suffix, self.client_var, self.size_w, self.size_h,
                self.quantity, self.finish, self.bleed, self.rotation, self.reg_marks, 
                self.custom_text, self.grommets, self.pole_pockets, self.mirror
            ]
            
            for var in variables_to_trace:
                var.trace_add("write", self.update_filename_preview)
            
            for var in self.include_filename_vars.values():
                var.trace_add("write", self.update_filename_preview)
                
        except Exception as e:
            print(f"Error setting up traces: {e}")
    
    def update_filename_preview(self, *args):
        """Update the filename preview"""
        try:
            if self.user_editing_filename:
                return
            
            job_data = self.get_job_data()
            filename_config = self.config_manager.get_filename_components()
            include_flags = {key: var.get() for key, var in self.include_filename_vars.items()}
            
            filename = self.filename_generator.generate(
                job_data, 
                filename_config["order"], 
                include_flags
            )
            
            self.filename_preview_var.set(filename)
            
        except Exception as e:
            print(f"Error updating filename preview: {e}")
    
    # ===== DATA METHODS =====
    def get_job_data(self):
        """Get current job data as dictionary"""
        return {
            "job_prefix": self.job_prefix.get(),
            "job_suffix": self.job_suffix.get(),
            "client": self.client_var.get(),
            "size_w": self.size_w.get(),
            "size_h": self.size_h.get(),
            "quantity": self.quantity.get(),
            "printer": self.printer_var.get(),
            "print_mode": self.print_mode.get(),
            "ssds_mode": self.ssds_mode.get(),
            "media_group": self.media_group_var.get(),
            "media": self.media_var.get(),
            "job_type": self.job_type_var.get(),
            "bleed": self.bleed.get(),
            "registration": self.reg_marks.get(),
            "rotation": self.rotation.get(),
            "finish": self.finish.get(),
            "grommets": self.grommets.get(),
            "pole_pockets": self.pole_pockets.get(),
            "mirror": self.mirror.get(),
            "custom_text": self.custom_text.get(),
            "file_path": self.file_path,
            "inject_metadata": self.inject_metadata.get(),
            "quickset_override": self.quickset_override_var.get(),
            "quickset": self.quickset.get()
        }
    
    def create_job_object(self):
        """Create Job object from current UI state"""
        return Job.from_dict(self.get_job_data())
    
    # ===== EVENT HANDLERS =====
    def on_print_mode_change(self):
        """Handle print mode change"""
        if self.print_mode.get() == "Flatbed":
            self.ssds_frame.pack(side="left", padx=20)
        else:
            self.ssds_frame.pack_forget()
    
    def on_media_group_change(self, *args):
        """Handle media group change"""
        try:
            selected_printer = self.printer_var.get()
            media_config = self.config_manager.get_media_config(selected_printer)
            options = media_config.get(self.media_group_var.get(), [])
            
            self.media_cb.configure(values=options)
            if options and self.media_var.get() not in options:
                self.media_var.set(options[0])
        except Exception as e:
            print(f"Error changing media group: {e}")
    
    def on_quickset_override_toggle(self):
        """Handle QuickSet override toggle"""
        state = "normal" if self.quickset_override_var.get() else "disabled"
        self.quickset_dropdown.configure(state=state)
        
        if self.quickset_override_var.get():
            self.quickset_override_frame.configure(fg_color="#8B0000")
        else:
            self.quickset_override_frame.configure(fg_color=("gray75", "gray25"))
    
    def on_filename_focus_in(self, event):
        """Handle filename entry focus in"""
        self.user_editing_filename = True
    
    def on_filename_focus_out(self, event):
        """Handle filename entry focus out"""
        self.user_editing_filename = False
    
    # ===== ACTION METHODS =====
    def pick_file(self):
        """Select PDF file"""
        try:
            path = filedialog.askopenfilename(
                title="Select PDF File",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if path:
                self.file_path = path
                self.selected_file_label.configure(text=os.path.basename(path))
        except Exception as e:
            print(f"Error picking file: {e}")
    
    def save_client(self):
        """Save new client to list"""
        try:
            new_client = self.client_var.get().strip()
            if not new_client:
                messagebox.showwarning("Invalid Client", "Please enter a client name.")
                return
            
            client_list = self.config_manager.get_client_list()
            if new_client not in client_list:
                client_list.append(new_client)
                self.config_manager.set("client_list", client_list)
                self.client_combo.configure(values=client_list)
                self.status_label.configure(text=f"Client '{new_client}' saved.")
            else:
                messagebox.showinfo("Client Exists", "Client already exists in the list.")
                
        except Exception as e:
            print(f"Error saving client: {e}")
    
    def apply_preset(self, preset_name):
        """Apply a user preset"""
        try:
            # Define preset configurations
            presets = {
                "Banner Standard": {
                    "media_group": "Banner",
                    "media": "Scrim",
                    "size_w": "48",
                    "size_h": "96",
                    "grommets": "Corners",
                    "pole_pockets": "None",
                    "finish": "Matte"
                },
                "Banner 38\"": {
                    "media_group": "Banner", 
                    "media": "Scrim",
                    "size_w": "38",
                    "size_h": "72",
                    "grommets": "Top",
                    "pole_pockets": "Bottom",
                    "finish": "Matte"
                }
            }
            
            if preset_name in presets:
                preset = presets[preset_name]
                
                # Apply preset values
                self.media_group_var.set(preset.get("media_group", "Vinyl"))
                self.on_media_group_change()
                self.media_var.set(preset.get("media", "Glossy"))
                self.size_w.set(preset.get("size_w", "24"))
                self.size_h.set(preset.get("size_h", "36"))
                self.grommets.set(preset.get("grommets", "None"))
                self.pole_pockets.set(preset.get("pole_pockets", "None"))
                self.finish.set(preset.get("finish", "Glossy"))
                
                self.status_label.configure(text=f"Applied preset: {preset_name}")
                
        except Exception as e:
            print(f"Error applying preset: {e}")
    
    def save_preset(self):
        """Save current settings as preset"""
        messagebox.showinfo("Save Preset", "Preset saving functionality coming soon!")
    
    # ===== TESTING METHODS =====
    def test_routing(self):
        """Test routing with current job settings"""
        try:
            if not self.printer_var.get():
                messagebox.showerror("Error", "Please select a printer first.")
                return
            
            job = self.create_job_object()
            result = self.routing_engine.test_job_routing(job)
            
            if result["success"]:
                target = result["target_folder"]
                matching_rules = result["matching_rules"]
                
                message = f"✅ Job would route to folder: '{target}'\n\n"
                if matching_rules:
                    message += f"Matched {len(matching_rules)} rule(s):\n"
                    for rule in matching_rules[:3]:  # Show first 3
                        message += f"• Priority: {rule['priority']}\n"
                        message += f"  Criteria: {', '.join([f'{k}={v}' for k, v in rule['criteria'].items()])}\n"
                
                messagebox.showinfo("Routing Test", message)
            else:
                message = f"❌ No routing rule matches current job criteria.\n\nJob would use 'Default' folder.\n\nCriteria: {', '.join([f'{k}={v}' for k, v in result['job_criteria'].items()])}"
                messagebox.showwarning("Routing Test", message)
                
        except Exception as e:
            messagebox.showerror("Test Error", f"Error testing routing: {str(e)}")
    
    def test_art_copy(self):
        """Test client art folder copying"""
        try:
            client = self.client_var.get().strip()
            if not client:
                messagebox.showerror("Error", "Please select a client first.")
                return
            
            if not self.config_manager.is_art_copy_enabled():
                messagebox.showwarning("Art Copy Disabled", "Client art copying is disabled in settings.")
                return
            
            art_folders = self.config_manager.get_client_art_folders()
            if client not in art_folders:
                messagebox.showwarning("No Mapping", f"No art folder mapping found for '{client}'.\n\nPlease add mapping in Settings > Client Art.")
                return
            
            art_folder = art_folders[client]
            
            if os.path.exists(art_folder):
                messagebox.showinfo("Art Copy Test", f"✅ Art folder exists and is accessible:\n\nClient: {client}\nFolder: {art_folder}")
            else:
                messagebox.showerror("Art Copy Test", f"❌ Art folder does not exist:\n\nClient: {client}\nFolder: {art_folder}")
            
        except Exception as e:
            messagebox.showerror("Test Error", f"Error testing art copy: {str(e)}")
    
    # ===== FILE PROCESSING =====
    def process_file(self):
        """Process the selected file"""
        try:
            # Validate inputs
            if not self.file_path:
                messagebox.showerror("Error", "Please select a PDF file.")
                return
            
            if not os.path.exists(self.file_path):
                messagebox.showerror("Error", "Selected file does not exist.")
                return
            
            # Create job object
            job = self.create_job_object()
            
            # Validate job
            is_valid, errors = job.validate()
            if not is_valid:
                messagebox.showerror("Validation Error", "Job validation failed:\n\n" + "\n".join(errors))
                return
            
            # Generate filename
            filename_config = self.config_manager.get_filename_components()
            include_flags = {key: var.get() for key, var in self.include_filename_vars.items()}
            filename = self.filename_generator.generate(job.to_dict(), filename_config["order"], include_flags)
            
            # Validate filename
            is_valid_filename, filename_issues = self.filename_generator.validate_filename(filename)
            if not is_valid_filename:
                if not messagebox.askyesno("Filename Issues", 
                                         f"Filename has issues:\n\n" + "\n".join(filename_issues) + "\n\nContinue anyway?"):
                    return
            
            # Process file
            self.status_label.configure(text="Processing file...")
            self.update()  # Update UI
            
            results = self.routing_engine.process_file(self.file_path, filename, job)
            
            # Show results
            self.show_processing_results(results, filename)
            
        except Exception as e:
            print(f"Error processing file: {e}")
            messagebox.showerror("Processing Error", f"Error processing file: {str(e)}")
            self.status_label.configure(text="Processing failed.")
    
    def show_processing_results(self, results, filename):
        """Show file processing results"""
        try:
            status_parts = []
            
            # Check hotfolder result
            if results["hotfolder"]["success"]:
                status_parts.append("✅ Routed to printer")
            else:
                status_parts.append("❌ Failed to route to printer")
            
            # Check art copy result
            art_result = results["art_copy"]
            if art_result["success"] is True:
                status_parts.append("✅ Copied to client folder")
            elif art_result["success"] is False:
                status_parts.append("❌ Failed to copy to client folder")
            # None means no client mapping (don't show anything)
            
            # Update status
            status_text = " | ".join(status_parts)
            self.status_label.configure(text=status_text)
            
            # Show dialog
            if results["success"]:
                message = f"File processing completed!\n\nFilename: {filename}\n\n" + "\n".join(status_parts)
                
                # Add paths if available
                if results["hotfolder"]["path"]:
                    message += f"\n\nPrinter folder: {results['hotfolder']['path']}"
                if art_result["path"]:
                    message += f"\nClient folder: {art_result['path']}"
                
                messagebox.showinfo("Processing Complete", message)
            else:
                error_details = []
                if results["hotfolder"]["error"]:
                    error_details.append(f"Hotfolder: {results['hotfolder']['error']}")
                if art_result["error"]:
                    error_details.append(f"Art copy: {art_result['error']}")
                
                message = f"File processing failed!\n\n" + "\n".join(status_parts)
                if error_details:
                    message += f"\n\nErrors:\n" + "\n".join(error_details)
                
                messagebox.showerror("Processing Failed", message)
                
        except Exception as e:
            print(f"Error showing results: {e}")
            messagebox.showerror("Error", f"Error displaying results: {str(e)}")
    
    # ===== UTILITY METHODS =====
    def refresh_from_config(self):
        """Refresh UI from configuration changes"""
        try:
            # Refresh printer list
            active_printers = self.config_manager.get_active_printers()
            
            # Update client combo
            client_list = self.config_manager.get_client_list()
            self.client_combo.configure(values=client_list)
            
            # Refresh media options
            self.on_media_group_change()
            
            # Rebuild include panel if it exists
            if hasattr(self, 'include_panel_frame'):
                self.build_include_panel()
            
            # Update filename preview
            self.update_filename_preview()
            
            print("Job setup tab refreshed from config")
            
        except Exception as e:
            print(f"Error refreshing job setup tab: {e}")
    
    def reset_form(self):
        """Reset form to default values"""
        try:
            # Reset basic info
            self.job_prefix.set("TIT")
            self.job_suffix.set("")
            self.client_var.set("")
            
            # Reset size and quantity
            self.size_w.set("24")
            self.size_h.set("36")
            self.quantity.set("1")
            
            # Reset print settings
            self.print_mode.set("Roll")
            self.ssds_mode.set("SS")
            
            # Reset media
            self.media_group_var.set("Vinyl")
            self.media_var.set("Glossy")
            self.job_type_var.set("Standard")
            
            # Reset processing options
            self.bleed.set("None")
            self.reg_marks.set("None")
            self.rotation.set("None")
            self.finish.set("Glossy")
            self.grommets.set("None")
            self.pole_pockets.set("None")
            self.mirror.set("No")
            
            # Reset custom text
            self.custom_text.set("")
            
            # Reset metadata options
            self.inject_metadata.set(True)
            self.quickset_override_var.set(False)
            self.quickset.set("QuickSet1")
            
            # Clear file selection
            self.file_path = ""
            self.selected_file_label.configure(text="No file selected")
            
            # Update UI
            self.on_print_mode_change()
            self.on_media_group_change()
            self.on_quickset_override_toggle()
            
            self.status_label.configure(text="Form reset to defaults")
            
        except Exception as e:
            print(f"Error resetting form: {e}")
    
    def get_current_settings_summary(self):
        """Get a summary of current settings for debugging"""
        try:
            job = self.create_job_object()
            summary = {
                "job_info": f"{job.get_job_number()} - {job.client}",
                "size": job.get_size_string(),
                "print_settings": f"{job.printer} - {job.print_mode}",
                "media": f"{job.media_group} / {job.media}",
                "routing_criteria": job.get_routing_criteria(),
                "filename_preview": self.filename_preview_var.get()
            }
            return summary
        except Exception as e:
            return {"error": str(e)}