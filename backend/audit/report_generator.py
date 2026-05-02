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
        
        # RACI Matrix
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
        
        recommendations = template_findings.get('recommendations', [])
        if recommendations:
            # Group by priority
            urgent = [r for r in recommendations if r.get('priority') == 'URGENT']
            high = [r for r in recommendations if r.get('priority') == 'HIGH']
            low = [r for r in recommendations if r.get('priority') == 'LOW']
            
            if urgent:
                report.append("### 🔴 URGENT Actions (Immediate)\n")
                for rec in urgent:
                    report.append(f"**{rec.get('finding_category', 'Action')}**")
                    report.append(f"- Finding: {rec.get('finding', '')}")
                    report.append(f"- Action: {rec.get('recommendation', '')}")
                    report.append(f"- Timeline: {rec.get('timeline', 'Immediate')}\n")
            
            if high:
                report.append("### 🟡 HIGH Priority Actions (90 days)\n")
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
    
    def convert_to_pdf(self, markdown_content: str, output_path: str):
        """
        Convert Markdown content to professionally styled PDF using reportlab.
        
        Args:
            markdown_content: Markdown report content
            output_path: Path where PDF should be saved
        
        Returns:
            Path to generated PDF file
        """
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
        
        # Generate PDF
        pdf_filename = f"audit_report_{audit_id}_{timestamp}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        self.convert_to_pdf(markdown_content, pdf_path)
        
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