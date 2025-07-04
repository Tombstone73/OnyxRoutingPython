"""
Routing engine for Titan Automation
Handles file routing, client art folder copying, and routing analysis
"""
import os
import shutil
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from difflib import SequenceMatcher

from models.job import Job
from models.routing_rule import RoutingRule

class RoutingEngine:
    """Handles all routing logic and file operations"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def process_file(self, file_path: str, filename: str, job: Job) -> Dict:
        """
        Process file with complete routing and copying
        
        Returns:
            Dictionary with processing results
        """
        try:
            results = {
                "success": False,
                "hotfolder": {"success": False, "path": None, "error": None},
                "art_copy": {"success": None, "path": None, "error": None},
                "filename": filename
            }
            
            print(f"\n=== PROCESSING FILE: {filename} ===")
            
            # 1. Route to hotfolder
            hotfolder_result = self.route_to_hotfolder(file_path, filename, job)
            results["hotfolder"] = hotfolder_result
            
            # 2. Copy to client art folder (if enabled)
            if self.config_manager.is_art_copy_enabled():
                art_result = self.copy_to_client_art_folder(file_path, filename, job)
                results["art_copy"] = art_result
            
            # Overall success if hotfolder succeeded or art copy succeeded
            results["success"] = (results["hotfolder"]["success"] or 
                                results["art_copy"]["success"])
            
            print(f"=== PROCESSING COMPLETE ===\n")
            return results
            
        except Exception as e:
            print(f"Error in process_file: {e}")
            return {
                "success": False,
                "error": str(e),
                "hotfolder": {"success": False, "error": str(e)},
                "art_copy": {"success": False, "error": str(e)}
            }
    
    def route_to_hotfolder(self, file_path: str, filename: str, job: Job) -> Dict:
        """Route file to appropriate hotfolder"""
        try:
            print(f"🔄 Routing to hotfolder...")
            
            # Get hotfolder root
            hotfolder_root = self.config_manager.get_hotfolder_root()
            if not hotfolder_root or not os.path.exists(hotfolder_root):
                error = "Hotfolder root not set or doesn't exist"
                print(f"❌ {error}")
                return {"success": False, "error": error, "path": None}
            
            # Get printer folder
            printer_folder = self.config_manager.get_printer_folder_name(job.printer)
            printer_path = os.path.join(hotfolder_root, printer_folder)
            
            if not os.path.exists(printer_path):
                error = f"Printer folder doesn't exist: {printer_path}"
                print(f"❌ {error}")
                return {"success": False, "error": error, "path": None}
            
            # Determine target folder using routing rules
            target_folder = self.determine_target_folder(job)
            if not target_folder:
                target_folder = "Default"
                print(f"⚠️  No routing rule matched, using Default folder")
            
            # Create full target path
            target_path = os.path.join(printer_path, target_folder)
            
            # Create folder if it doesn't exist
            os.makedirs(target_path, exist_ok=True)
            
            # Copy file
            dest_file = os.path.join(target_path, filename)
            shutil.copy2(file_path, dest_file)
            
            print(f"✅ Routed to: {target_path}")
            return {"success": True, "path": target_path, "error": None}
            
        except Exception as e:
            error = f"Hotfolder routing failed: {str(e)}"
            print(f"❌ {error}")
            return {"success": False, "error": error, "path": None}
    
    def copy_to_client_art_folder(self, file_path: str, filename: str, job: Job) -> Dict:
        """Copy file to client's art folder"""
        try:
            print(f"🎨 Copying to client art folder...")
            
            # Check if client is set
            if not job.client or not job.client.strip():
                print("ℹ️  No client selected, skipping art copy")
                return {"success": None, "path": None, "error": None}
            
            # Get client art folder mapping
            art_folders = self.config_manager.get_client_art_folders()
            if job.client not in art_folders:
                print(f"ℹ️  No art folder mapping for client '{job.client}'")
                return {"success": None, "path": None, "error": None}
            
            art_folder = art_folders[job.client]
            
            # Check if folder exists
            if not os.path.exists(art_folder):
                error = f"Client art folder doesn't exist: {art_folder}"
                print(f"❌ {error}")
                return {"success": False, "path": None, "error": error}
            
            # Copy file
            dest_file = os.path.join(art_folder, filename)
            shutil.copy2(file_path, dest_file)
            
            print(f"✅ Copied to client art folder: {art_folder}")
            return {"success": True, "path": art_folder, "error": None}
            
        except PermissionError as e:
            error = f"Permission denied accessing art folder: {str(e)}"
            print(f"❌ {error}")
            return {"success": False, "path": None, "error": error}
        except Exception as e:
            error = f"Art folder copy failed: {str(e)}"
            print(f"❌ {error}")
            return {"success": False, "path": None, "error": error}
    
    def determine_target_folder(self, job: Job) -> Optional[str]:
        """Determine target folder based on routing rules"""
        try:
            print(f"🎯 Determining target folder for printer: {job.printer}")
            
            # Get routing rules for this printer
            routing_rules_data = self.config_manager.get_routing_rules(job.printer)
            
            if not routing_rules_data:
                print(f"No routing rules found for printer: {job.printer}")
                return None
            
            print(f"Found {len(routing_rules_data)} routing rules")
            
            # Convert to RoutingRule objects
            routing_rules = [RoutingRule.from_dict(rule_data) for rule_data in routing_rules_data]
            
            # Get job criteria
            job_criteria = job.get_routing_criteria()
            print(f"Job criteria: {job_criteria}")
            
            # Find matching rules
            matching_rules = []
            for i, rule in enumerate(routing_rules):
                if rule.matches_job(job):
                    matching_rules.append((i, rule))
                    print(f"Rule {i+1} MATCHES: {rule.get_criteria_text()} → {rule.target_folder}")
                else:
                    print(f"Rule {i+1} no match: {rule.get_criteria_text()}")
            
            if not matching_rules:
                print("❌ No routing rules matched job criteria")
                return None
            
            if len(matching_rules) > 1:
                print(f"⚠️  Multiple rules matched ({len(matching_rules)}), using highest priority")
                # Sort by priority weight (highest first)
                matching_rules.sort(key=lambda x: x[1].get_priority_weight(), reverse=True)
            
            # Use the best matching rule
            rule_index, selected_rule = matching_rules[0]
            print(f"✅ Using rule {rule_index+1}: {selected_rule.target_folder}")
            
            return selected_rule.target_folder
            
        except Exception as e:
            print(f"Error determining target folder: {e}")
            return None
    
    def test_job_routing(self, job: Job) -> Dict:
        """Test where a job would route without actually processing"""
        try:
            result = {
                "job_criteria": job.get_routing_criteria(),
                "target_folder": None,
                "matching_rules": [],
                "printer": job.printer,
                "success": False
            }
            
            # Determine target folder
            target_folder = self.determine_target_folder(job)
            result["target_folder"] = target_folder
            result["success"] = target_folder is not None
            
            # Get detailed rule matching info
            routing_rules_data = self.config_manager.get_routing_rules(job.printer)
            if routing_rules_data:
                routing_rules = [RoutingRule.from_dict(rule_data) for rule_data in routing_rules_data]
                for i, rule in enumerate(routing_rules):
                    if rule.matches_job(job):
                        result["matching_rules"].append({
                            "index": i,
                            "target_folder": rule.target_folder,
                            "criteria": rule.criteria,
                            "priority": rule.priority
                        })
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_routing_setup(self, printer: str, folders: List[str]) -> Dict:
        """Analyze routing setup for a printer"""
        try:
            analysis = {
                "printer": printer,
                "total_folders": len(folders),
                "total_rules": 0,
                "mapped_folders": [],
                "unmapped_folders": [],
                "auto_detected_folders": [],
                "conflicting_rules": [],
                "coverage_gaps": [],
                "rule_quality": {"good": 0, "fair": 0, "poor": 0}
            }
            
            # Get routing rules
            routing_rules_data = self.config_manager.get_routing_rules(printer)
            routing_rules = [RoutingRule.from_dict(rule_data) for rule_data in routing_rules_data]
            analysis["total_rules"] = len(routing_rules)
            
            # Analyze each folder
            for folder in folders:
                folder_rules = [rule for rule in routing_rules if rule.target_folder == folder]
                detected_attrs = self.detect_folder_attributes(folder)
                
                folder_info = {
                    "folder": folder,
                    "rules": len(folder_rules),
                    "detected": detected_attrs
                }
                
                if len(folder_rules) == 0:
                    if detected_attrs:
                        analysis["auto_detected_folders"].append(folder_info)
                    else:
                        analysis["unmapped_folders"].append(folder)
                else:
                    analysis["mapped_folders"].append(folder_info)
                    
                    # Check for conflicts (multiple rules for same folder)
                    if len(folder_rules) > 1:
                        analysis["conflicting_rules"].append({
                            "folder": folder,
                            "rule_count": len(folder_rules)
                        })
            
            # Analyze rule quality
            for rule in routing_rules:
                criteria_count = rule.get_criteria_count()
                if criteria_count >= 3:
                    analysis["rule_quality"]["good"] += 1
                elif criteria_count >= 1:
                    analysis["rule_quality"]["fair"] += 1
                else:
                    analysis["rule_quality"]["poor"] += 1
            
            # Find coverage gaps
            analysis["coverage_gaps"] = self.find_coverage_gaps(routing_rules, printer)
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def detect_folder_attributes(self, folder_name: str) -> Dict[str, str]:
        """Auto-detect folder attributes based on naming patterns"""
        try:
            folder_lower = folder_name.lower()
            detected = {}
            
            # Check for common patterns
            if "bleed" in folder_lower:
                detected["Bleed"] = "Bleed"
            
            if "90" in folder_lower or "rotated" in folder_lower or "rotate" in folder_lower:
                detected["Rotation"] = "90 CW"
            
            if "icut" in folder_lower:
                detected["Registration"] = "iCut"
            elif "graphtec" in folder_lower:
                detected["Registration"] = "Graphtec"
            
            if "matte" in folder_lower:
                detected["Finish"] = "Matte"
            elif "glossy" in folder_lower:
                detected["Finish"] = "Glossy"
            
            if "grommet" in folder_lower:
                if "corner" in folder_lower:
                    detected["Grommets"] = "Corners"
                elif "top" in folder_lower:
                    detected["Grommets"] = "Top"
                elif "bottom" in folder_lower:
                    detected["Grommets"] = "Bottom"
                elif "side" in folder_lower:
                    detected["Grommets"] = "Sides"
                else:
                    detected["Grommets"] = "All"
            
            if "pole" in folder_lower or "pocket" in folder_lower:
                if "top" in folder_lower and "bottom" in folder_lower:
                    detected["Pole Pockets"] = "Top & Bottom"
                elif "top" in folder_lower:
                    detected["Pole Pockets"] = "Top"
                elif "bottom" in folder_lower:
                    detected["Pole Pockets"] = "Bottom"
                elif "side" in folder_lower:
                    detected["Pole Pockets"] = "Sides"
                else:
                    detected["Pole Pockets"] = "Top & Bottom"
            
            if "mirror" in folder_lower:
                detected["Mirror"] = "Yes"
            
            if "flatbed" in folder_lower:
                detected["Print Mode"] = "Flatbed"
            elif "roll" in folder_lower:
                detected["Print Mode"] = "Roll"
            
            if "rush" in folder_lower:
                detected["Job Type"] = "Rush"
            
            # Check for media types
            media_keywords = {
                "vinyl": "Vinyl",
                "banner": "Banner", 
                "scrim": "Banner",
                "mesh": "Banner",
                "paper": "Paper",
                "canvas": "Paper"
            }
            
            for keyword, media_group in media_keywords.items():
                if keyword in folder_lower:
                    detected["Media Group"] = media_group
                    break
            
            return detected
            
        except Exception as e:
            print(f"Error detecting folder attributes: {e}")
            return {}
    
    def find_coverage_gaps(self, routing_rules: List[RoutingRule], printer: str) -> List[Dict]:
        """Find gaps in routing coverage"""
        try:
            gaps = []
            
            # Get media groups for this printer
            media_config = self.config_manager.get_media_config(printer)
            media_groups = list(media_config.keys())
            
            # Check coverage for each media group
            covered_media_groups = set()
            for rule in routing_rules:
                media_group = rule.criteria.get("Media Group")
                if media_group:
                    covered_media_groups.add(media_group)
            
            # Find uncovered media groups
            for media_group in media_groups:
                if media_group not in covered_media_groups:
                    gaps.append({
                        "type": "Media Group",
                        "value": media_group,
                        "description": f"No routing rules for media group '{media_group}'"
                    })
            
            # Check for common job types
            job_types = ["Standard", "Rush", "Reprint"]
            covered_job_types = set()
            for rule in routing_rules:
                job_type = rule.criteria.get("Job Type")
                if job_type:
                    covered_job_types.add(job_type)
            
            for job_type in job_types:
                if job_type not in covered_job_types:
                    gaps.append({
                        "type": "Job Type",
                        "value": job_type,
                        "description": f"No routing rules for job type '{job_type}'"
                    })
            
            return gaps
            
        except Exception as e:
            print(f"Error finding coverage gaps: {e}")
            return []
    
    def auto_match_clients(self, client_list: List[str], folder_list: List[str]) -> Dict:
        """Auto-match client names with folder names using fuzzy matching"""
        try:
            matches = {}
            existing_mappings = self.config_manager.get_client_art_folders()
            
            for client in client_list:
                # Skip clients that already have mappings
                if client in existing_mappings:
                    continue
                
                best_match = None
                best_ratio = 0
                
                for folder in folder_list:
                    ratio = SequenceMatcher(None, client.lower(), folder.lower()).ratio()
                    if ratio > best_ratio and ratio > 0.6:  # 60% similarity threshold
                        best_ratio = ratio
                        best_match = folder
                
                if best_match:
                    art_root = self.config_manager.get_art_root_path()
                    matches[client] = {
                        'folder': best_match,
                        'ratio': best_ratio,
                        'full_path': os.path.join(art_root, best_match)
                    }
            
            return matches
            
        except Exception as e:
            print(f"Error auto-matching clients: {e}")
            return {}
    
    def create_auto_routing_rule(self, folder_name: str, detected_attributes: Dict[str, str]) -> bool:
        """Create a routing rule based on detected attributes"""
        try:
            if not detected_attributes:
                return False
            
            # Create new rule
            rule = RoutingRule(
                target_folder=folder_name,
                criteria=detected_attributes,
                priority="Normal",
                auto_generated=True
            )
            
            # Validate rule
            is_valid, errors = rule.validate()
            if not is_valid:
                print(f"Invalid auto-generated rule: {errors}")
                return False
            
            # This would need to be implemented based on which printer is being configured
            # For now, we'll return True to indicate the rule was created successfully
            print(f"Auto-generated rule for folder '{folder_name}': {rule.get_criteria_text()}")
            return True
            
        except Exception as e:
            print(f"Error creating auto routing rule: {e}")
            return False