"""
Accountability Tracker for AI Audit Reports
Generates RACI matrix and governance maturity assessment
"""

from datetime import datetime
import random
import string


class AccountabilityTracker:
    """
    Tracks accountability and governance for AI model audits.
    Generates RACI matrices, identifies gaps, and assesses governance maturity.
    """
    
    def __init__(self):
        """Initialize the AccountabilityTracker."""
        self.activities = [
            "Model Development",
            "Bias Testing & Validation",
            "Regulatory Approval",
            "Production Deployment",
            "Ongoing Monitoring",
            "Complaint Investigation",
            "Annual Re-audit"
        ]
        self.raci_roles = ["R", "A", "C", "I"]
    
    def build_raci_matrix(self, raci_input):
        """
        Build a RACI accountability matrix for AI lifecycle activities.
        
        Args:
            raci_input (dict): Contains role assignments:
                - model_developer: Person/team responsible for model development
                - approval_authority: Person/team with approval authority
                - monitor_owner: Person/team responsible for monitoring
                - complaint_handler: Person/team handling complaints
        
        Returns:
            dict: Structured RACI matrix with activities and role assignments
        """
        model_developer = raci_input.get("model_developer", "")
        approval_authority = raci_input.get("approval_authority", "")
        monitor_owner = raci_input.get("monitor_owner", "")
        complaint_handler = raci_input.get("complaint_handler", "")
        
        # Build RACI matrix with standard assignments
        matrix = {
            "Model Development": {
                "R": model_developer,
                "A": approval_authority,
                "C": monitor_owner,
                "I": complaint_handler
            },
            "Bias Testing & Validation": {
                "R": model_developer,
                "A": approval_authority,
                "C": monitor_owner,
                "I": complaint_handler
            },
            "Regulatory Approval": {
                "R": approval_authority,
                "A": approval_authority,
                "C": model_developer,
                "I": monitor_owner
            },
            "Production Deployment": {
                "R": model_developer,
                "A": approval_authority,
                "C": monitor_owner,
                "I": complaint_handler
            },
            "Ongoing Monitoring": {
                "R": monitor_owner,
                "A": approval_authority,
                "C": model_developer,
                "I": complaint_handler
            },
            "Complaint Investigation": {
                "R": complaint_handler,
                "A": approval_authority,
                "C": model_developer,
                "I": monitor_owner
            },
            "Annual Re-audit": {
                "R": model_developer,
                "A": approval_authority,
                "C": monitor_owner,
                "I": complaint_handler
            }
        }
        
        return {
            "matrix": matrix,
            "roles": {
                "model_developer": model_developer,
                "approval_authority": approval_authority,
                "monitor_owner": monitor_owner,
                "complaint_handler": complaint_handler
            }
        }
    
    def identify_accountability_gaps(self, raci_matrix):
        """
        Identify gaps in the RACI matrix where critical roles are missing.
        
        Args:
            raci_matrix (dict): The RACI matrix from build_raci_matrix()
        
        Returns:
            list: List of gap dictionaries with activity, role, and severity
        """
        gaps = []
        matrix = raci_matrix.get("matrix", {})
        roles = raci_matrix.get("roles", {})
        
        # Check each activity for missing Responsible and Accountable owners
        for activity, assignments in matrix.items():
            responsible = assignments.get("R", "").strip()
            accountable = assignments.get("A", "").strip()
            
            if not responsible:
                gaps.append({
                    "activity": activity,
                    "role": "Responsible (R)",
                    "severity": "HIGH",
                    "description": f"No Responsible owner assigned for {activity}"
                })
            
            if not accountable:
                gaps.append({
                    "activity": activity,
                    "role": "Accountable (A)",
                    "severity": "HIGH",
                    "description": f"No Accountable owner assigned for {activity}"
                })
        
        # Check for missing complaint handler
        if not roles.get("complaint_handler", "").strip():
            gaps.append({
                "activity": "Complaint Investigation",
                "role": "Complaint Handler",
                "severity": "HIGH",
                "description": "No complaint handler assigned"
            })
        
        # Check for re-audit schedule (Annual Re-audit activity)
        reaudit_responsible = matrix.get("Annual Re-audit", {}).get("R", "").strip()
        if not reaudit_responsible:
            gaps.append({
                "activity": "Annual Re-audit",
                "role": "Re-audit Schedule",
                "severity": "MEDIUM",
                "description": "No re-audit schedule or responsible owner defined"
            })
        
        return gaps
    
    def generate_audit_trail(self, raci_input):
        """
        Generate an audit trail record for this accountability assessment.
        
        Args:
            raci_input (dict): The input containing role assignments and metadata
        
        Returns:
            dict: Audit trail with ID, timestamp, submitter, and model version
        """
        # Generate unique audit ID (format: FL-2026-XXXX)
        year = datetime.now().year
        random_suffix = ''.join(random.choices(string.digits, k=4))
        audit_id = f"FL-{year}-{random_suffix}"
        
        # Extract submitter info
        submitter = raci_input.get("model_developer", "Unknown")
        model_version = raci_input.get("model_version", "1.0.0")
        
        # Generate timestamp
        timestamp = datetime.now().isoformat()
        
        return {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "submitter": submitter,
            "model_version": model_version,
            "audit_type": "Accountability Assessment"
        }
    
    def assess_governance_maturity(self, raci_matrix, gaps):
        """
        Assess the governance maturity level based on RACI completeness.
        
        Args:
            raci_matrix (dict): The RACI matrix
            gaps (list): List of identified gaps
        
        Returns:
            dict: Maturity level, score, and risk assessment
        """
        gap_count = len(gaps)
        
        # Determine maturity level based on gaps
        if gap_count > 3:
            level = 1
            level_name = "Ad-hoc"
            risk = "HIGH"
            score = 33
            description = "Governance is ad-hoc with significant accountability gaps"
        elif gap_count >= 1:
            level = 2
            level_name = "Defined"
            risk = "MEDIUM"
            score = 67
            description = "Governance processes are defined but have some gaps"
        else:
            level = 3
            level_name = "Managed"
            risk = "LOW"
            score = 100
            description = "Governance is well-managed with clear accountability"
        
        return {
            "maturity_level": level,
            "level_name": level_name,
            "score": score,
            "risk": risk,
            "gap_count": gap_count,
            "description": description,
            "recommendation": self._get_maturity_recommendation(level)
        }
    
    def _get_maturity_recommendation(self, level):
        """
        Get recommendations based on maturity level.
        
        Args:
            level (int): Maturity level (1-3)
        
        Returns:
            str: Recommendation text
        """
        recommendations = {
            1: "Immediate action required: Assign clear owners for all activities, "
               "establish formal governance processes, and document accountability structures.",
            2: "Address identified gaps: Complete missing role assignments and "
               "strengthen governance documentation.",
            3: "Maintain current governance standards and conduct regular reviews "
               "to ensure continued compliance."
        }
        return recommendations.get(level, "Continue monitoring governance practices.")
    
    def run_full_accountability(self, raci_input):
        """
        Run complete accountability assessment orchestrating all methods.
        
        Args:
            raci_input (dict): Input containing all role assignments and metadata
        
        Returns:
            dict: Complete accountability report with all assessments
        """
        # Build RACI matrix
        raci_matrix = self.build_raci_matrix(raci_input)
        
        # Identify gaps
        gaps = self.identify_accountability_gaps(raci_matrix)
        
        # Generate audit trail
        audit_trail = self.generate_audit_trail(raci_input)
        
        # Assess governance maturity
        maturity = self.assess_governance_maturity(raci_matrix, gaps)
        
        # Compile complete report
        report = {
            "audit_trail": audit_trail,
            "raci_matrix": raci_matrix,
            "accountability_gaps": gaps,
            "governance_maturity": maturity,
            "summary": {
                "total_activities": len(self.activities),
                "total_gaps": len(gaps),
                "maturity_level": maturity["level_name"],
                "risk_level": maturity["risk"],
                "audit_id": audit_trail["audit_id"]
            }
        }
        
        return report


# Example usage and testing
if __name__ == "__main__":
    # Example RACI input
    sample_input = {
        "model_developer": "Alice Johnson",
        "approval_authority": "Bob Smith",
        "monitor_owner": "Carol White",
        "complaint_handler": "David Brown",
        "model_version": "2.1.0"
    }
    
    tracker = AccountabilityTracker()
    report = tracker.run_full_accountability(sample_input)
    
    print("=== Accountability Report ===")
    print(f"Audit ID: {report['audit_trail']['audit_id']}")
    print(f"Timestamp: {report['audit_trail']['timestamp']}")
    print(f"\nGovernance Maturity: {report['governance_maturity']['level_name']}")
    print(f"Risk Level: {report['governance_maturity']['risk']}")
    print(f"Score: {report['governance_maturity']['score']}/100")
    print(f"\nTotal Gaps: {len(report['accountability_gaps'])}")
    
    if report['accountability_gaps']:
        print("\nIdentified Gaps:")
        for gap in report['accountability_gaps']:
            print(f"  - [{gap['severity']}] {gap['description']}")
    
    print(f"\nRecommendation: {report['governance_maturity']['recommendation']}")

# Made with Bob
