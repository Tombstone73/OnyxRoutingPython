"""
Job data model for Titan Automation
Represents a print job with all its properties
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

@dataclass
class Job:
    """Represents a print job with all its properties"""
    
    # Basic job info
    job_prefix: str = "TIT"
    job_suffix: str = ""
    client: str = ""
    file_path: str = ""
    
    # Size and quantity
    size_w: str = "24"
    size_h: str = "36"
    quantity: str = "1"
    
    # Print settings
    printer: str = ""
    print_mode: str = "Roll"  # Roll or Flatbed
    ssds_mode: str = "SS"     # SS or DS (for flatbed)
    
    # Media settings
    media_group: str = "Vinyl"
    media: str = "Glossy"
    job_type: str = "Standard"
    
    # Processing options
    bleed: str = "None"
    registration: str = "None"  # None, Graphtec, iCut
    rotation: str = "None"      # None, 90 CW
    finish: str = "Glossy"      # Glossy, Matte
    
    # Hardware options
    grommets: str = "None"      # None, All, Top, Bottom, Sides, Corners
    pole_pockets: str = "None"  # None, Top & Bottom, Top, Bottom, Sides
    mirror: str = "No"          # No, Yes
    
    # Custom options
    custom_text: str = ""
    
    # Metadata
    inject_metadata: bool = True
    quickset_override: bool = False
    quickset: str = "QuickSet1"
    
    # Timestamps
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Job':
        """Create Job from dictionary"""
        # Only include fields that exist in the Job class
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def to_dict(self) -> Dict:
        """Convert Job to dictionary"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
    
    def get_job_number(self) -> str:
        """Get complete job number"""
        return f"{self.job_prefix}{self.job_suffix}"
    
    def get_size_string(self) -> str:
        """Get size as WxH string"""
        return f"{self.size_w}x{self.size_h}"
    
    def get_routing_criteria(self) -> Dict[str, str]:
        """Get job criteria for routing rules"""
        criteria = {
            "Print Mode": self.print_mode,
            "Media Group": self.media_group,
            "Job Type": self.job_type,
            "Bleed": self.bleed,
            "Registration": self.registration,
            "Rotation": self.rotation,
            "Finish": self.finish,
            "Grommets": self.grommets,
            "Pole Pockets": self.pole_pockets,
            "Mirror": self.mirror
        }
        
        # Add SSDS mode for flatbed jobs
        if self.print_mode == "Flatbed":
            criteria["SSDS Mode"] = self.ssds_mode
        
        # Remove empty values
        return {k: v for k, v in criteria.items() if v and v not in ["None", "No", ""]}
    
    def get_filename_data(self) -> Dict[str, str]:
        """Get data for filename generation"""
        return {
            "job_number": self.get_job_number(),
            "client": self.client,
            "size": self.get_size_string(),
            "quantity": f"QTY{self.quantity}",
            "finish": self.finish,
            "bleed": self.bleed,
            "rotation": self.rotation,
            "registration": self.registration,
            "grommets": self.grommets,
            "pole_pockets": self.pole_pockets,
            "mirror": self.mirror,
            "date": datetime.now().strftime("%m-%d-%y"),
            "custom_text": self.custom_text,
        }
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate job data and return (is_valid, errors)"""
        errors = []
        
        if not self.file_path:
            errors.append("No file selected")
        
        if not self.client.strip():
            errors.append("Client name is required")
        
        if not self.printer:
            errors.append("Printer must be selected")
        
        try:
            float(self.size_w)
            float(self.size_h)
        except ValueError:
            errors.append("Size dimensions must be numeric")
        
        try:
            int(self.quantity)
        except ValueError:
            errors.append("Quantity must be a number")
        
        return len(errors) == 0, errors
    
    def __str__(self) -> str:
        """String representation of job"""
        return f"Job({self.get_job_number()}, {self.client}, {self.get_size_string()})"