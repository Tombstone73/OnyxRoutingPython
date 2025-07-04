"""
Routing rule model for Titan Automation
Represents a routing rule for directing jobs to specific folders
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

@dataclass
class RoutingRule:
    """Represents a routing rule for job processing"""
    
    # Rule identification
    target_folder: str = ""
    priority: str = "Normal"  # High, Normal, Low
    
    # Matching criteria
    criteria: Dict[str, str] = field(default_factory=dict)
    
    # Metadata
    auto_generated: bool = False
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    modified: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RoutingRule':
        """Create RoutingRule from dictionary"""
        # Handle the case where criteria might be missing
        if 'criteria' not in data:
            data['criteria'] = {}
        
        return cls(
            target_folder=data.get('target_folder', ''),
            priority=data.get('priority', 'Normal'),
            criteria=data.get('criteria', {}),
            auto_generated=data.get('auto_generated', False),
            created=data.get('created', datetime.now().isoformat()),
            modified=data.get('modified')
        )
    
    def to_dict(self) -> Dict:
        """Convert RoutingRule to dictionary"""
        result = {
            'target_folder': self.target_folder,
            'priority': self.priority,
            'criteria': self.criteria,
            'auto_generated': self.auto_generated,
            'created': self.created
        }
        
        if self.modified:
            result['modified'] = self.modified
        
        return result
    
    def matches_job(self, job) -> bool:
        """Check if this rule matches a job"""
        if not self.criteria:
            return False
        
        job_criteria = job.get_routing_criteria()
        
        # Rule matches if ALL rule criteria are satisfied by the job
        for rule_key, rule_value in self.criteria.items():
            job_value = job_criteria.get(rule_key)
            if job_value != rule_value:
                return False
        
        return True
    
    def get_priority_weight(self) -> int:
        """Get numeric weight for priority (higher = more important)"""
        priority_weights = {
            "High": 3,
            "Normal": 2,
            "Low": 1
        }
        return priority_weights.get(self.priority, 2)
    
    def get_criteria_count(self) -> int:
        """Get number of criteria in this rule"""
        return len(self.criteria)
    
    def get_criteria_text(self) -> str:
        """Get human-readable criteria description"""
        if not self.criteria:
            return "No criteria"
        
        return ", ".join([f"{k}: {v}" for k, v in self.criteria.items()])
    
    def is_specific(self) -> bool:
        """Check if rule is specific (has multiple criteria)"""
        return len(self.criteria) >= 3
    
    def conflicts_with(self, other_rule) -> bool:
        """Check if this rule conflicts with another rule"""
        if not isinstance(other_rule, RoutingRule):
            return False
        
        if self.target_folder == other_rule.target_folder:
            return False  # Same target, no conflict
        
        # Check if criteria overlap significantly
        common_criteria = set(self.criteria.keys()) & set(other_rule.criteria.keys())
        if not common_criteria:
            return False  # No common criteria, no conflict
        
        # Check if all common criteria have same values
        for key in common_criteria:
            if self.criteria[key] != other_rule.criteria[key]:
                return False  # Different values, no conflict
        
        # All common criteria match but different targets = conflict
        return True
    
    def update_criteria(self, new_criteria: Dict[str, str]):
        """Update rule criteria and mark as modified"""
        self.criteria = new_criteria.copy()
        self.modified = datetime.now().isoformat()
    
    def update_target(self, new_target: str):
        """Update target folder and mark as modified"""
        self.target_folder = new_target
        self.modified = datetime.now().isoformat()
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate rule and return (is_valid, errors)"""
        errors = []
        
        if not self.target_folder.strip():
            errors.append("Target folder is required")
        
        if not self.criteria:
            errors.append("At least one criteria is required")
        
        if self.priority not in ["High", "Normal", "Low"]:
            errors.append("Priority must be High, Normal, or Low")
        
        # Check for empty criteria values
        for key, value in self.criteria.items():
            if not value or value.strip() == "":
                errors.append(f"Criteria '{key}' has empty value")
        
        return len(errors) == 0, errors
    
    def __str__(self) -> str:
        """String representation of routing rule"""
        criteria_str = self.get_criteria_text()
        return f"RoutingRule({self.target_folder}, {self.priority}, {criteria_str})"
    
    def __repr__(self) -> str:
        """Developer representation of routing rule"""
        return (f"RoutingRule(target_folder='{self.target_folder}', "
                f"priority='{self.priority}', criteria={self.criteria})")