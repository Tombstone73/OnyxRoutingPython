"""
Filename generation for Titan Automation
Handles creation of standardized filenames based on job data
"""
from typing import Dict, List
from datetime import datetime

class FilenameGenerator:
    """Generates standardized filenames for print jobs"""
    
    def __init__(self):
        self.default_extension = ".pdf"
    
    def generate(self, job_data: Dict, components_order: List[str], 
                 include_flags: Dict[str, bool]) -> str:
        """
        Generate filename from job data
        
        Args:
            job_data: Dictionary containing job information
            components_order: List of component keys in desired order
            include_flags: Dictionary of component -> include boolean
        
        Returns:
            Generated filename string
        """
        try:
            # Build components map from job data
            parts_map = self._build_parts_map(job_data)
            
            # Build ordered parts list
            ordered_parts = []
            for component_key in components_order:
                # Check if this component should be included
                if not include_flags.get(component_key, True):
                    continue
                
                # Get the component value
                part = parts_map.get(component_key, "")
                
                # Skip empty or "none" values
                if not part or part.lower() in ['none', 'no', '']:
                    continue
                
                # Skip size if it's just "x" (empty width/height)
                if component_key == 'size' and part == 'x':
                    continue
                
                # Clean the part (replace spaces with underscores)
                clean_part = str(part).replace(" ", "_").replace("&", "and")
                ordered_parts.append(clean_part)
            
            # Join parts and add extension
            if ordered_parts:
                filename = "_".join(ordered_parts) + self.default_extension
            else:
                filename = "untitled" + self.default_extension
            
            return filename
            
        except Exception as e:
            print(f"Error generating filename: {e}")
            return f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}{self.default_extension}"
    
    def _build_parts_map(self, job_data: Dict) -> Dict[str, str]:
        """Build map of component keys to formatted values"""
        
        # Helper function to get value safely
        def get_value(key, default=""):
            return str(job_data.get(key, default)).strip()
        
        # Build the parts map
        parts_map = {
            "job_number": f"{get_value('job_prefix', 'TIT')}{get_value('job_suffix')}",
            "client": get_value('client'),
            "size": f"{get_value('size_w')}x{get_value('size_h')}",
            "quantity": f"QTY{get_value('quantity', '1')}",
            "finish": get_value('finish'),
            "bleed": get_value('bleed'),
            "rotation": get_value('rotation'),
            "registration": get_value('registration'),
            "grommets": get_value('grommets'),
            "pole_pockets": get_value('pole_pockets'),
            "mirror": get_value('mirror'),
            "date": datetime.now().strftime("%m-%d-%y"),
            "custom_text": get_value('custom_text'),
        }
        
        return parts_map
    
    def preview_filename(self, job_data: Dict, components_order: List[str], 
                        include_flags: Dict[str, bool]) -> str:
        """
        Generate a preview of the filename (same as generate, for consistency)
        """
        return self.generate(job_data, components_order, include_flags)
    
    def validate_filename(self, filename: str) -> tuple[bool, List[str]]:
        """
        Validate a filename for common issues
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        if not filename:
            issues.append("Filename is empty")
            return False, issues
        
        if filename == self.default_extension:
            issues.append("Filename contains only extension")
        
        # Check for invalid characters (Windows/Mac/Linux compatibility)
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in filename:
                issues.append(f"Contains invalid character: '{char}'")
        
        # Check length (Windows has 260 char path limit)
        if len(filename) > 200:
            issues.append("Filename is too long (>200 characters)")
        
        # Check for reserved names (Windows)
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + \
                        [f'COM{i}' for i in range(1, 10)] + \
                        [f'LPT{i}' for i in range(1, 10)]
        
        base_name = filename.replace(self.default_extension, '').upper()
        if base_name in reserved_names:
            issues.append(f"'{base_name}' is a reserved filename")
        
        # Check for double underscores (indicates missing data)
        if '__' in filename:
            issues.append("Contains double underscores (possible missing data)")
        
        return len(issues) == 0, issues
    
    def sanitize_component(self, component: str) -> str:
        """
        Sanitize a single filename component
        """
        if not component:
            return ""
        
        # Convert to string and strip whitespace
        clean = str(component).strip()
        
        # Replace problematic characters
        replacements = {
            ' ': '_',
            '&': 'and',
            '/': '-',
            '\\': '-',
            ':': '-',
            '*': '',
            '?': '',
            '"': '',
            '<': '',
            '>': '',
            '|': '-'
        }
        
        for old, new in replacements.items():
            clean = clean.replace(old, new)
        
        # Remove multiple consecutive underscores
        while '__' in clean:
            clean = clean.replace('__', '_')
        
        # Remove leading/trailing underscores
        clean = clean.strip('_')
        
        return clean
    
    def get_component_display_name(self, component_key: str) -> str:
        """Get display name for a component key"""
        display_names = {
            "job_number": "Job Number",
            "client": "Client Name",
            "size": "Size (WxH)",
            "quantity": "Quantity",
            "finish": "Finish",
            "bleed": "Bleed",
            "rotation": "Rotation",
            "registration": "Registration",
            "grommets": "Grommets",
            "pole_pockets": "Pole Pockets",
            "mirror": "Mirror",
            "date": "Date (MM-DD-YY)",
            "custom_text": "Custom Text",
        }
        
        return display_names.get(component_key, component_key.replace('_', ' ').title())
    
    def analyze_filename(self, filename: str) -> Dict:
        """
        Analyze a filename and try to extract components
        
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "filename": filename,
            "is_valid": True,
            "issues": [],
            "components": [],
            "estimated_parts": []
        }
        
        # Validate filename
        is_valid, issues = self.validate_filename(filename)
        analysis["is_valid"] = is_valid
        analysis["issues"] = issues
        
        if not filename:
            return analysis
        
        # Remove extension
        base_name = filename.replace(self.default_extension, '')
        
        # Split by underscores
        parts = base_name.split('_')
        analysis["estimated_parts"] = parts
        
        # Try to identify common patterns
        for i, part in enumerate(parts):
            component_info = {"index": i, "value": part, "type": "unknown"}
            
            # Check for common patterns
            if part.startswith('QTY'):
                component_info["type"] = "quantity"
            elif 'x' in part and len(part.split('x')) == 2:
                component_info["type"] = "size"
            elif part in ['Glossy', 'Matte', 'Satin']:
                component_info["type"] = "finish"
            elif part in ['Bleed', 'None']:
                component_info["type"] = "bleed"
            elif len(part) == 8 and '-' in part:  # MM-DD-YY format
                component_info["type"] = "date"
            elif part.startswith('TIT'):
                component_info["type"] = "job_number"
            
            analysis["components"].append(component_info)
        
        return analysis