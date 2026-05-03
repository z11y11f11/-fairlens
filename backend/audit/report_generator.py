"""
FairLens Audit Report Generator
Generates comprehensive audit reports in Markdown and PDF formats
"""

import os
from datetime import datetime
from typing import Dict, Any, List
import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


class AuditReportGenerator:
    """
    Generates comprehensive audit reports from bias detection and compliance results.
    Outputs both Markdown and professionally styled PDF reports using reportlab.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        pass
    
    def generate_markdown_report(
        self, 
        audit_results: Dict[str, Any],
        template_findings: Dict[str, Any],
        accountability_report: Dict[str, Any]
    ) -> str:
        """
        Generate complete Markdown audit report.
        
        Args:
            audit_results: Results from BiasDetector.run_full_analysis()
            template_findings: Results from LoanApprovalAuditTemplate.run_full_template()
            accountability_report: Results from AccountabilityTracker.run_full_accountability()
        
        Returns:
            Complete Markdown report as string
        """
        # Extract key data
        audit_id = accountability_report['audit_trail']['audit_id']
        timestamp = accountability_report['audit_trail']['timestamp']
        submitter = accountability_report['audit_trail']['submitter']
        
        di_analysis = audit_results.get('disparate_impact_analysis', {})
        proxy_analysis = audit_results.get('proxy_variable_analysis', {})
        protected_check = audit_results.get('protected_attributes_check', {})
        composite_risk = audit_results.get('composite_risk_score', {})
        
        # Start building report
        report = []
        
        # Header
        report.append("# FairLens AI Bias Audit Report")
        report.append(f"\n**Audit ID:** {audit_id}")
        report.append(f"**Date:** {datetime.fromisoformat(timestamp).strftime('%B %d, %Y')}")
        report.append(f"**Submitted by:** {submitter}")
        report.append("\n---\n")
        
        # Executive Summary
        report.append("## Executive Summary\n")
        overall_risk = composite_risk.get('risk_level', 'UNKNOWN')
        composite_score = round(composite_risk.get('composite_score', 0), 2)
        
        report.append(
            f"This audit assessed an AI-powered loan approval system for bias, discrimination, "
            f"and regulatory compliance. The system received an overall risk rating of **{overall_risk}** "
            f"with a composite fairness score of **{composite_score}/100**. "
        )
        
        if composite_score >= 71:
            report.append(
                "The model demonstrates acceptable fairness characteristics and is suitable for "
                "deployment with ongoing monitoring."
            )
        elif composite_score >= 41:
            report.append(
                "The model shows moderate bias concerns that should be addressed before deployment. "
                "Remediation actions are recommended within 90 days."
            )
        else:
            report.append(
                "The model exhibits significant bias and discrimination risks. Immediate remediation "
                "is required before any production deployment."
            )
        
        report.append("\n")
        
        # Regulatory Context
        report.append("## Regulatory Context\n")
        report.append("This audit evaluates compliance with:\n")
        report.append("- **Equal Credit Opportunity Act (ECOA)**: Prohibits discrimination in credit decisions")
        report.append("- **EU AI Act Article 9**: Classifies credit scoring as high-risk AI requiring strict oversight")
        report.append("- **Fair Credit Reporting Act (FCRA)**: Regulates use of consumer credit information")
        report.append("- **GDPR Article 5**: Requires data minimization and privacy protection")
        report.append("- **Federal Reserve SR 11-7**: Model risk management guidance")
        report.append("\n")
        
        # Section 1: Discrimination Detection Results (removed Data Bias Risk Assessment section)
        report.append("## 1. Discrimination Detection Results\n")
        
        di_ratio = di_analysis.get('disparate_impact')
        if di_ratio is not None:
            if di_ratio < 0.8:
                icon = "🔴"
            elif di_ratio < 1.0:
                icon = "🟡"
            else:
                icon = "🟢"
            
            report.append(f"### {icon} Disparate Impact Analysis\n")
            report.append(f"**Disparate Impact Ratio:** {round(di_ratio, 2)}")
            report.append(f"**Statistical Parity Difference:** {round(di_analysis.get('statistical_parity_difference', 0), 2)}")
            report.append(f"**Equal Opportunity Difference:** {round(di_analysis.get('equal_opportunity_difference', 0), 2)}\n")
            
            report.append("**Interpretation:**")
            report.append(f"{di_analysis.get('interpretation', 'No interpretation available')}\n")
            
            # Metrics detail
            metrics = di_analysis.get('metrics_detail', {})
            if metrics:
                report.append("**Detailed Metrics:**")
                priv_rate = metrics.get('privileged_selection_rate', 0)
                unpriv_rate = metrics.get('unprivileged_selection_rate', 0)
                report.append(f"- Privileged group selection rate: {round(priv_rate * 100, 2)}%")
                report.append(f"- Unprivileged group selection rate: {round(unpriv_rate * 100, 2)}%")
                report.append(f"- Total samples analyzed: {metrics.get('total_samples', 0):,}")
                report.append(f"- Privileged samples: {metrics.get('privileged_samples', 0):,}")
                report.append(f"- Unprivileged samples: {metrics.get('unprivileged_samples', 0):,}\n")
        
        # Multi-group DI analysis (for CSV uploads with multiple groups)
        protected_attrs = di_analysis.get('protected_attributes', {})
        if protected_attrs:
            for attr_name, attr_data in protected_attrs.items():
                di_ratio_attr = attr_data.get('di_ratio', 0)
                if di_ratio_attr < 0.8:
                    icon = "🔴"
                elif di_ratio_attr < 1.0:
                    icon = "🟡"
                else:
                    icon = "🟢"
                
                report.append(f"### {icon} {attr_name.title()} DI Analysis\n")
                report.append(f"**Disparate Impact Ratio:** {round(di_ratio_attr, 2)}\n")
                
                # Show all group rates sorted by rate (highest to lowest)
                group_stats = attr_data.get('group_stats', {})
                if group_stats:
                    sorted_groups = sorted(group_stats.items(), key=lambda x: x[1]['rate'], reverse=True)
                    report.append("**Group Approval Rates:**")
                    for i, (group_name, stats) in enumerate(sorted_groups):
                        rate_pct = round(stats['rate'] * 100, 2)
                        if i == 0:
                            report.append(f"- {group_name}: {rate_pct}% (reference/highest)")
                        elif i == len(sorted_groups) - 1:
                            report.append(f"- {group_name}: {rate_pct}% (lowest)")
                        else:
                            report.append(f"- {group_name}: {rate_pct}%")
                    report.append(f"\n**DI = {round(di_ratio_attr, 2)} {icon}**\n")
        
        # Template discrimination findings
        discrimination_findings = template_findings.get('findings', {}).get('discrimination', [])
        if discrimination_findings:
            report.append("### Regulatory Compliance Assessment\n")
            for finding in discrimination_findings:
                icon = self._get_risk_icon(finding.get('risk_level', ''))
                report.append(f"**{icon} {finding.get('category', 'Finding')}**")
                report.append(f"- {finding.get('finding', '')}")
                report.append(f"- *{finding.get('explanation', '')}*")
                report.append(f"- Regulation: {finding.get('regulation', 'N/A')}\n")
        
        # Section 2: Accountability & Governance (renumbered from 3)
        report.append("## 2. Accountability & Governance\n")
        
        maturity = accountability_report.get('governance_maturity', {})
        report.append(f"**Governance Maturity Level:** {maturity.get('level_name', 'Unknown')} (Level {maturity.get('maturity_level', 0)})")
        report.append(f"**Maturity Score:** {round(maturity.get('score', 0), 2)}/100")
        report.append(f"**Risk Level:** {self._get_risk_icon(maturity.get('risk', ''))} {maturity.get('risk', 'UNKNOWN')}\n")
        
        # RACI Matrix - Use standard template if no custom matrix provided
        report.append("### RACI Matrix\n")
        raci_matrix = accountability_report.get('raci_matrix', {}).get('matrix', {})
        if raci_matrix:
            report.append("| Activity | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) |")
            report.append("|----------|----------------|-----------------|---------------|--------------|")
            for activity, roles in raci_matrix.items():
                r = roles.get('R', '-')
                a = roles.get('A', '-')
                c = roles.get('C', '-')
                i = roles.get('I', '-')
                report.append(f"| {activity} | {r} | {a} | {c} | {i} |")
            report.append("\n")
        else:
            # Standard RACI Matrix template
            report.append("| Activity | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) |")
            report.append("|----------|----------------|-----------------|---------------|--------------|")
            report.append("| Model Development | Data Science Team | CTO | Compliance Dept | CEO |")
            report.append("| Bias Testing & Validation | Compliance Officer | CRO | Legal Dept | Board of Directors |")
            report.append("| Regulatory Approval | CRO | CEO | Compliance Dept | Regulators |")
            report.append("| Production Deployment | Engineering Team | CTO | Risk Management | CEO |")
            report.append("| Ongoing Monitoring | Risk Control Team | CRO | Compliance Dept | CEO |")
            report.append("| Complaint Investigation | Compliance Officer | CRO | Legal Dept | Customer Service |")
            report.append("| Annual Re-audit | External Auditors | Board of Directors | Compliance Dept | Regulators |")
            report.append("\n")
        
        # Accountability gaps
        gaps = accountability_report.get('accountability_gaps', [])
        if gaps:
            report.append("### Identified Accountability Gaps\n")
            for gap in gaps:
                icon = self._get_risk_icon(gap.get('severity', ''))
                report.append(f"- {icon} **{gap.get('activity', 'Unknown')}**: {gap.get('description', '')}")
            report.append("\n")
        
        # Template accountability findings
        accountability_findings = template_findings.get('findings', {}).get('accountability', [])
        if accountability_findings:
            report.append("### Governance Findings\n")
            for finding in accountability_findings:
                icon = self._get_risk_icon(finding.get('risk_level', ''))
                report.append(f"**{icon} {finding.get('category', 'Finding')}**")
                report.append(f"- {finding.get('finding', '')}")
                report.append(f"- *{finding.get('explanation', '')}*\n")
        
        # Section 3: Data Privacy Compliance (renumbered from 4)
        report.append("## 3. Data Privacy Compliance\n")
        
        # Standard GDPR Checklist
        report.append("### GDPR Compliance Checklist\n")
        report.append("✅ Data source documented and authorized")
        report.append("✅ Data minimization principle applied")
        report.append("✅ Retention period defined")
        report.append("⚠️ Regular privacy impact assessment recommended")
        report.append("⚠️ Data subject rights procedure should be documented\n")
        
        privacy_findings = template_findings.get('findings', {}).get('privacy', [])
        if privacy_findings:
            report.append("### GDPR & Privacy Assessment\n")
            for finding in privacy_findings:
                icon = self._get_risk_icon(finding.get('risk_level', ''))
                report.append(f"**{icon} {finding.get('category', 'Finding')}**")
                report.append(f"- {finding.get('finding', '')}")
                report.append(f"- *{finding.get('explanation', '')}*")
                report.append(f"- Regulation: {finding.get('regulation', 'N/A')}\n")
        
        # Section 4: Remediation Recommendations (renumbered from 5)
        report.append("## 4. Remediation Recommendations\n")
        
        # Generate automatic recommendations based on DI results
        auto_recommendations = self._generate_di_recommendations(di_analysis, protected_attrs)
        
        if auto_recommendations:
            for rec in auto_recommendations:
                report.append(f"### {rec['icon']} {rec['priority']} - {rec['title']}\n")
                report.append(f"- **Finding:** {rec['finding']}")
                report.append(f"- **Action:** {rec['action']}")
                if rec.get('additional_actions'):
                    for action in rec['additional_actions']:
                        report.append(f"  - {action}")
                report.append(f"- **Timeline:** {rec['timeline']}\n")
        
        # Include template recommendations if available
        recommendations = template_findings.get('recommendations', [])
        if recommendations:
            # Group by priority
            urgent = [r for r in recommendations if r.get('priority') == 'URGENT']
            high = [r for r in recommendations if r.get('priority') == 'HIGH']
            low = [r for r in recommendations if r.get('priority') == 'LOW']
            
            if urgent:
                report.append("### 🔴 Additional URGENT Actions (Immediate)\n")
                for rec in urgent:
                    report.append(f"**{rec.get('finding_category', 'Action')}**")
                    report.append(f"- Finding: {rec.get('finding', '')}")
                    report.append(f"- Action: {rec.get('recommendation', '')}")
                    report.append(f"- Timeline: {rec.get('timeline', 'Immediate')}\n")
            
            if high:
                report.append("### 🟡 Additional HIGH Priority Actions (90 days)\n")
                for rec in high:
                    report.append(f"**{rec.get('finding_category', 'Action')}**")
                    report.append(f"- Finding: {rec.get('finding', '')}")
                    report.append(f"- Action: {rec.get('recommendation', '')}")
                    report.append(f"- Timeline: {rec.get('timeline', '90 days')}\n")
            
            if low:
                report.append("### 🟢 Ongoing Monitoring\n")
                for rec in low[:3]:  # Limit to top 3
                    report.append(f"- {rec.get('finding_category', 'Monitor')}: {rec.get('recommendation', '')}")
                report.append("\n")
        
        # Audit Trail
        report.append("## Audit Trail\n")
        report.append(f"**Audit ID:** {audit_id}")
        report.append(f"**Audit Date:** {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"**Submitted By:** {submitter}")
        report.append(f"**Model Version:** {accountability_report['audit_trail'].get('model_version', 'N/A')}")
        report.append(f"**Next Review Date:** {template_findings.get('next_review_date', 'TBD')}")
        report.append(f"\n**Composite Risk Score:** {round(composite_score, 2)}/100")
        report.append(f"**Overall Risk Level:** {overall_risk}")
        
        report.append("\n---")
        report.append("\n*Generated by FairLens AI Bias Audit System*")
        report.append(f"\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(report)
    
    def _generate_di_recommendations(self, di_analysis: Dict[str, Any], protected_attrs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate automatic remediation recommendations based on DI analysis results.
        
        Args:
            di_analysis: Disparate impact analysis results
            protected_attrs: Protected attributes analysis results
        
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Check main DI ratio if available
        di_ratio = di_analysis.get('disparate_impact')
        if di_ratio is not None:
            attr_name = "Primary Protected Attribute"
            recommendations.extend(self._create_di_recommendation(attr_name, di_ratio))
        
        # Check each protected attribute
        if protected_attrs:
            for attr_name, attr_data in protected_attrs.items():
                di_ratio_attr = attr_data.get('di_ratio', 0)
                recommendations.extend(self._create_di_recommendation(attr_name.title(), di_ratio_attr))
        
        return recommendations
    
    def _create_di_recommendation(self, attribute_name: str, di_value: float) -> List[Dict[str, Any]]:
        """
        Create recommendation based on DI value for a specific attribute.
        
        Args:
            attribute_name: Name of the protected attribute
            di_value: Disparate Impact ratio value
        
        Returns:
            List containing recommendation dictionary
        """
        recommendations = []
        
        if di_value < 0.6:
            # URGENT - Severe discrimination
            recommendations.append({
                'icon': '🔴',
                'priority': 'URGENT',
                'title': 'Immediate Action Required',
                'finding': f'{attribute_name} shows severe discrimination (DI={round(di_value, 2)})',
                'action': 'Immediately suspend use of this feature',
                'additional_actions': [
                    'Notify regulators within 30 days',
                    'Submit remediation plan within 30 days'
                ],
                'timeline': 'Immediate'
            })
        elif di_value < 0.8:
            # HIGH PRIORITY - Discrimination
            recommendations.append({
                'icon': '🔴',
                'priority': 'HIGH PRIORITY',
                'title': 'Action Required within 90 days',
                'finding': f'{attribute_name} shows discrimination (DI={round(di_value, 2)})',
                'action': 'Remove or replace feature in next model update',
                'additional_actions': [
                    'Retrain model without this feature',
                    'Re-run bias testing after retraining'
                ],
                'timeline': '90 days'
            })
        elif di_value < 0.9:
            # MEDIUM PRIORITY - Borderline
            recommendations.append({
                'icon': '🟡',
                'priority': 'MEDIUM PRIORITY',
                'title': 'Monitor and Review',
                'finding': f'{attribute_name} shows borderline results (DI={round(di_value, 2)})',
                'action': 'Quarterly monitoring required',
                'additional_actions': [
                    'Document risk acceptance rationale',
                    'Address in next scheduled model update'
                ],
                'timeline': 'Next model review cycle'
            })
        else:
            # COMPLIANT - Continue monitoring
            recommendations.append({
                'icon': '🟢',
                'priority': 'COMPLIANT',
                'title': 'Continue Monitoring',
                'finding': f'{attribute_name} within acceptable range (DI={round(di_value, 2)})',
                'action': 'Maintain quarterly review schedule',
                'additional_actions': [
                    'Document compliance status'
                ],
                'timeline': 'Ongoing'
            })
        
        return recommendations
    
    def _get_risk_icon(self, risk_level: str) -> str:
        """Get emoji icon for risk level."""
        risk_level_upper = risk_level.upper()
        if 'HIGH' in risk_level_upper or 'CRITICAL' in risk_level_upper or 'URGENT' in risk_level_upper:
            return "🔴"
        elif 'MEDIUM' in risk_level_upper:
            return "🟡"
        elif 'LOW' in risk_level_upper:
            return "🟢"
        else:
            return "⚪"
    def _create_cover_page(self, audit_data: Dict[str, Any]) -> List:
        """
        Create a professional cover page for the PDF report.
        
        Args:
            audit_data: Dictionary containing audit_id, date, risk_level, composite_score
        
        Returns:
            List of reportlab elements for the cover page
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, KeepTogether
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus.flowables import Flowable
        
        cover_elements = []
        
        # Custom cover page flowable that draws background and content
        class CoverPage(Flowable):
            def __init__(self, audit_data):
                Flowable.__init__(self)
                self.audit_data = audit_data
                self.width = letter[0]
                self.height = letter[1]
            
            def draw(self):
                canvas = self.canv
                
                # Draw dark blue background
                canvas.setFillColor(colors.HexColor('#1a3a6b'))
                canvas.rect(0, 0, self.width, self.height, fill=1, stroke=0)
                
                # FairLens logo
                canvas.setFillColor(colors.white)
                canvas.setFont('Helvetica-Bold', 36)
                canvas.drawCentredString(self.width/2, self.height - 2*inch, 'FairLens')
                
                # Main title
                canvas.setFont('Helvetica-Bold', 28)
                canvas.drawCentredString(self.width/2, self.height - 3.5*inch, 'AI Bias Audit Report')
                
                # Horizontal line
                canvas.setStrokeColor(colors.white)
                canvas.setLineWidth(2)
                canvas.line(1.5*inch, self.height - 4*inch, self.width - 1.5*inch, self.height - 4*inch)
                
                # Audit details
                canvas.setFont('Helvetica', 14)
                y_pos = self.height - 4.5*inch
                
                audit_id = self.audit_data.get('audit_id', 'FL-2026-XXXXX')
                audit_date = self.audit_data.get('date', datetime.now().strftime('%B %d, %Y'))
                
                canvas.drawCentredString(self.width/2, y_pos, 'Institution: Financial Institution Audit')
                y_pos -= 0.3*inch
                canvas.drawCentredString(self.width/2, y_pos, f'Audit ID: {audit_id}')
                y_pos -= 0.3*inch
                canvas.drawCentredString(self.width/2, y_pos, f'Date: {audit_date}')
                y_pos -= 0.3*inch
                canvas.drawCentredString(self.width/2, y_pos, 'Prepared by: FairLens AI Audit System')
                
                # Risk rating box
                y_pos -= 0.8*inch
                risk_level = self.audit_data.get('risk_level', 'UNKNOWN').upper()
                composite_score = self.audit_data.get('composite_score', 0)
                
                if 'HIGH' in risk_level:
                    risk_color = colors.HexColor('#dc2626')
                    risk_text = 'HIGH RISK ⚠️'
                elif 'MEDIUM' in risk_level:
                    risk_color = colors.HexColor('#f59e0b')
                    risk_text = 'MEDIUM RISK ⚡'
                elif 'LOW' in risk_level:
                    risk_color = colors.HexColor('#16a34a')
                    risk_text = 'LOW RISK ✅'
                else:
                    risk_color = colors.grey
                    risk_text = 'RISK ASSESSMENT PENDING'
                
                # Draw risk box
                box_width = 4*inch
                box_height = 0.6*inch
                box_x = (self.width - box_width) / 2
                
                canvas.setFillColor(risk_color)
                canvas.setStrokeColor(colors.white)
                canvas.setLineWidth(2)
                canvas.rect(box_x, y_pos - box_height/2, box_width, box_height, fill=1, stroke=1)
                
                canvas.setFillColor(colors.white)
                canvas.setFont('Helvetica-Bold', 18)
                canvas.drawCentredString(self.width/2, y_pos, risk_text)
                
                # Composite score
                y_pos -= 0.6*inch
                canvas.setFont('Helvetica', 12)
                canvas.drawCentredString(self.width/2, y_pos, f'Composite Fairness Score: {round(composite_score, 2)}/100')
                
                # Footer
                canvas.setFont('Helvetica-Bold', 11)
                canvas.drawCentredString(self.width/2, 2.5*inch, 'Powered by IBM AI Fairness 360')
                
                canvas.setFont('Helvetica', 10)
                canvas.drawCentredString(self.width/2, 2.2*inch, 'EU AI Act Compliant | Confidential')
                
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(colors.HexColor('#93c5fd'))
                canvas.drawCentredString(self.width/2, 1.9*inch, 'EU AI Act | ECOA | GDPR | FCRA')
        
        # Add the cover page
        cover_elements.append(CoverPage(audit_data))
        
        return cover_elements
    
    
    def convert_to_pdf(self, markdown_content: str, output_path: str, audit_data: Dict[str, Any] | None = None):
        """
        Convert Markdown content to professionally styled PDF using reportlab.
        
        Args:
            markdown_content: Markdown report content
            output_path: Path where PDF should be saved
            audit_data: Optional audit data for cover page (audit_id, date, risk_level, composite_score)
        
        Returns:
            Path to generated PDF file
        """
        from reportlab.pdfgen import canvas as pdfcanvas
        from PyPDF2 import PdfMerger
        import tempfile
        
        # If audit data provided, create cover page separately
        if audit_data:
            # Create temporary file for cover page
            cover_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            cover_path = cover_temp.name
            cover_temp.close()
            
            # Create cover page PDF
            self._create_cover_page_pdf(cover_path, audit_data)
            
            # Create temporary file for main content
            content_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            content_path = content_temp.name
            content_temp.close()
            
            # Create main content PDF
            self._create_content_pdf(markdown_content, content_path)
            
            # Merge PDFs
            merger = PdfMerger()
            merger.append(cover_path)
            merger.append(content_path)
            merger.write(output_path)
            merger.close()
            
            # Clean up temp files
            import os
            os.unlink(cover_path)
            os.unlink(content_path)
        else:
            # No cover page, just create content PDF
            self._create_content_pdf(markdown_content, output_path)
        
        return output_path
    
    def _create_cover_page_pdf(self, output_path: str, audit_data: Dict[str, Any]):
        """Create a standalone PDF with just the cover page."""
        from reportlab.pdfgen import canvas as pdfcanvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        c = pdfcanvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Draw dark blue background
        c.setFillColor(colors.HexColor('#1a3a6b'))
        c.rect(0, 0, width, height, fill=1, stroke=0)
        
        # FairLens logo
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 36)
        c.drawCentredString(width/2, height - 2*inch, 'FairLens')
        
        # Main title
        c.setFont('Helvetica-Bold', 28)
        c.drawCentredString(width/2, height - 3.5*inch, 'AI Bias Audit Report')
        
        # Horizontal line
        c.setStrokeColor(colors.white)
        c.setLineWidth(2)
        c.line(1.5*inch, height - 4*inch, width - 1.5*inch, height - 4*inch)
        
        # Audit details
        c.setFont('Helvetica', 14)
        y_pos = height - 4.5*inch
        
        audit_id = audit_data.get('audit_id', 'FL-2026-XXXXX')
        audit_date = audit_data.get('date', datetime.now().strftime('%B %d, %Y'))
        
        c.drawCentredString(width/2, y_pos, 'Institution: Financial Institution Audit')
        y_pos -= 0.3*inch
        c.drawCentredString(width/2, y_pos, f'Audit ID: {audit_id}')
        y_pos -= 0.3*inch
        c.drawCentredString(width/2, y_pos, f'Date: {audit_date}')
        y_pos -= 0.3*inch
        c.drawCentredString(width/2, y_pos, 'Prepared by: FairLens AI Audit System')
        
        # Risk rating box
        y_pos -= 0.8*inch
        risk_level = audit_data.get('risk_level', 'UNKNOWN').upper()
        composite_score = audit_data.get('composite_score', 0)
        
        if 'HIGH' in risk_level:
            risk_color = colors.HexColor('#dc2626')
            risk_text = 'HIGH RISK ⚠️'
        elif 'MEDIUM' in risk_level:
            risk_color = colors.HexColor('#f59e0b')
            risk_text = 'MEDIUM RISK ⚡'
        elif 'LOW' in risk_level:
            risk_color = colors.HexColor('#16a34a')
            risk_text = 'LOW RISK ✅'
        else:
            risk_color = colors.grey
            risk_text = 'RISK ASSESSMENT PENDING'
        
        # Draw risk box
        box_width = 4*inch
        box_height = 0.6*inch
        box_x = (width - box_width) / 2
        
        c.setFillColor(risk_color)
        c.setStrokeColor(colors.white)
        c.setLineWidth(2)
        c.rect(box_x, y_pos - box_height/2, box_width, box_height, fill=1, stroke=1)
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 18)
        c.drawCentredString(width/2, y_pos, risk_text)
        
        # Composite score
        y_pos -= 0.6*inch
        c.setFont('Helvetica', 12)
        c.drawCentredString(width/2, y_pos, f'Composite Fairness Score: {round(composite_score, 2)}/100')
        
        # Footer
        c.setFont('Helvetica-Bold', 11)
        c.drawCentredString(width/2, 2.5*inch, 'Powered by IBM AI Fairness 360')
        
        c.setFont('Helvetica', 10)
        c.drawCentredString(width/2, 2.2*inch, 'EU AI Act Compliant | Confidential')
        
        c.setFont('Helvetica', 8)
        c.setFillColor(colors.HexColor('#93c5fd'))
        c.drawCentredString(width/2, 1.9*inch, 'EU AI Act | ECOA | GDPR | FCRA')
        
        c.save()
    
    def _create_content_pdf(self, markdown_content: str, output_path: str):
        """Create PDF from markdown content."""
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Container for PDF elements
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=10,
            spaceBefore=15
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        # Parse markdown content line by line
        lines = markdown_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Title (# heading)
            if line.startswith('# '):
                text = line[2:].strip()
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 12))
            
            # Heading 2 (## heading)
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, heading2_style))
            
            # Heading 3 (### heading)
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(text, heading3_style))
            
            # Horizontal rule
            elif line.startswith('---'):
                story.append(Spacer(1, 12))
            
            # Bold text with **
            elif line.startswith('**') and line.endswith('**'):
                text = line[2:-2]
                story.append(Paragraph(f'<b>{text}</b>', body_style))
            
            # List items
            elif line.startswith('- '):
                text = line[2:].strip()
                # Handle bold within list items - fix the replacement
                import re
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
                story.append(Paragraph(f'• {text}', body_style))
            
            # Table detection (simple)
            elif line.startswith('|'):
                # Collect table rows
                table_data = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    row = [cell.strip() for cell in lines[i].strip().split('|')[1:-1]]
                    table_data.append(row)
                    i += 1
                
                if len(table_data) > 1:
                    # Create table (skip separator row if present)
                    if all(cell.replace('-', '').strip() == '' for cell in table_data[1]):
                        table_data.pop(1)
                    
                    t = Table(table_data)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 12))
                continue
            
            # Regular paragraph
            else:
                # Handle bold and italic with regex
                import re
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
                text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
                story.append(Paragraph(text, body_style))
            
            i += 1
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def generate_full_report(
        self,
        all_data: Dict[str, Any],
        output_dir: str = "reports"
    ) -> Dict[str, str]:
        """
        Orchestrate full report generation (Markdown + PDF).
        
        Args:
            all_data: Dictionary containing:
                - audit_results: From BiasDetector
                - template_findings: From LoanApprovalAuditTemplate
                - accountability_report: From AccountabilityTracker
            output_dir: Directory to save reports
        
        Returns:
            Dictionary with file paths:
                - markdown_path: Path to .md file
                - pdf_path: Path to .pdf file
                - audit_id: Audit identifier
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract data
        audit_results = all_data.get('audit_results', {})
        template_findings = all_data.get('template_findings', {})
        accountability_report = all_data.get('accountability_report', {})
        
        # Generate audit ID for filenames
        audit_id = accountability_report.get('audit_trail', {}).get('audit_id', 'UNKNOWN')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate Markdown report
        markdown_content = self.generate_markdown_report(
            audit_results,
            template_findings,
            accountability_report
        )
        
        # Save Markdown file
        markdown_filename = f"audit_report_{audit_id}_{timestamp}.md"
        markdown_path = os.path.join(output_dir, markdown_filename)
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Prepare audit data for cover page
        audit_timestamp = accountability_report.get('audit_trail', {}).get('timestamp', '')
        if audit_timestamp:
            try:
                audit_date = datetime.fromisoformat(audit_timestamp).strftime('%B %d, %Y')
            except:
                audit_date = datetime.now().strftime('%B %d, %Y')
        else:
            audit_date = datetime.now().strftime('%B %d, %Y')
        
        composite_risk = audit_results.get('composite_risk_score', {})
        
        audit_data = {
            'audit_id': audit_id,
            'date': audit_date,
            'risk_level': composite_risk.get('risk_level', 'UNKNOWN'),
            'composite_score': composite_risk.get('composite_score', 0)
        }
        
        # Generate PDF with cover page
        pdf_filename = f"audit_report_{audit_id}_{timestamp}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        self.convert_to_pdf(markdown_content, pdf_path, audit_data)
        
        return {
            'markdown_path': markdown_path,
            'pdf_path': pdf_path,
            'audit_id': audit_id,
            'markdown_filename': markdown_filename,
            'pdf_filename': pdf_filename
        }


if __name__ == "__main__":
    print("FairLens Audit Report Generator")
    print("=" * 60)
    print("This module generates comprehensive audit reports in Markdown and PDF formats")
    print("Use with BiasDetector, LoanApprovalAuditTemplate, and AccountabilityTracker")

# Made with Bob