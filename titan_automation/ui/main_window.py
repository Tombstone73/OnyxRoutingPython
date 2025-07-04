"""
Main application window for Titan Automation
Coordinates all UI components and core services
"""
import customtkinter as ctk
from config.manager import ConfigManager
from config.constants import WINDOW_TITLE, WINDOW_SIZE, UI_THEME, UI_MODE
from core.routing_engine import RoutingEngine
from core.filename_generator import FilenameGenerator
from .job_setup_tab import JobSetupTab
from .settings_tab import SettingsTab
from .routing_tab import RoutingTab

class TitanAutomationApp(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        try:
            print("Starting application...")
            super().__init__()
            print("1. CTk initialized")
            
            # Configure window
            self.title(WINDOW_TITLE)
            self.geometry(WINDOW_SIZE)
            ctk.set_appearance_mode(UI_MODE)
            ctk.set_default_color_theme(UI_THEME)
            print("2. Window setup complete")
            
            # Initialize core services
            self.config_manager = ConfigManager()
            self.routing_engine = RoutingEngine(self.config_manager)
            self.filename_generator = FilenameGenerator()
            print("3. Core services initialized")
            
            # Build UI
            self.build_ui()
            print("4. UI built successfully")
            
            # Setup close protocol
            self.protocol("WM_DELETE_WINDOW", self.on_close)
            print("5. Application ready")
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def build_ui(self):
        """Build the main user interface"""
        try:
            # Create main tabview
            self.tabview = ctk.CTkTabview(self, width=1100, height=900)
            self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create tab frames
            job_setup_frame = self.tabview.add("Job Setup")
            settings_frame = self.tabview.add("Settings")
            routing_frame = self.tabview.add("Routing")
            
            # Initialize tab components with dependencies
            self.job_setup_tab = JobSetupTab(
                parent=job_setup_frame,
                config_manager=self.config_manager,
                routing_engine=self.routing_engine,
                filename_generator=self.filename_generator
            )
            
            self.settings_tab = SettingsTab(
                parent=settings_frame,
                config_manager=self.config_manager
            )
            
            self.routing_tab = RoutingTab(
                parent=routing_frame,
                config_manager=self.config_manager,
                routing_engine=self.routing_engine
            )
            
            print("All tabs initialized successfully")
            
        except Exception as e:
            print(f"Error building UI: {e}")
            raise
    
    def on_close(self):
        """Handle application closure"""
        try:
            print("Saving configuration before exit...")
            self.config_manager.save_config()
            print("Configuration saved")
        except Exception as e:
            print(f"Error saving configuration: {e}")
        finally:
            self.destroy()
    
    def get_config_manager(self):
        """Get config manager (for external access if needed)"""
        return self.config_manager
    
    def get_routing_engine(self):
        """Get routing engine (for external access if needed)"""
        return self.routing_engine
    
    def get_filename_generator(self):
        """Get filename generator (for external access if needed)"""
        return self.filename_generator
    
    def refresh_all_tabs(self):
        """Refresh all tabs (useful after config changes)"""
        try:
            if hasattr(self, 'job_setup_tab'):
                self.job_setup_tab.refresh_from_config()
            
            if hasattr(self, 'settings_tab'):
                self.settings_tab.refresh_from_config()
            
            if hasattr(self, 'routing_tab'):
                self.routing_tab.refresh_from_config()
            
            print("All tabs refreshed")
            
        except Exception as e:
            print(f"Error refreshing tabs: {e}")