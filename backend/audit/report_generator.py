"""
FairLens Audit Report Generator
Generates comprehensive audit reports in Markdown and PDF formats
"""

import os
from datetime import datetime
from typing import Dict, Any, List
import markdown

# Make weasyprint optional for PDF generation
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("Warning: weasyprint not available. PDF generation will be disabled.")


class AuditReportGenerator:
    """
    Generates comprehensive audit reports from bias detection and compliance results.
    Outputs both Markdown and professionally styled PDF reports.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        if WEASYPRINT_AVAILABLE:
            self.font_config = FontConfiguration()
        else:
            self.font_config = None
    
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
        composite_score = composite_risk.get('composite_score', 0)
        
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
        
        # Section 1: Data Bias Risk Assessment
        report.append("## 1. Data Bias Risk Assessment\n")
        
        # Protected attributes check
        if protected_check.get('violation_count', 0) > 0:
            report.append(f"### 🔴 CRITICAL: Protected Attributes Detected\n")
            for violation in protected_check.get('violations', []):
                report.append(f"- **{violation['feature']}** (maps to {violation['protected_attribute']})")
            report.append("\n**Legal Implications:**")
            for implication in protected_check.get('legal_implications', []):
                report.append(f"- {implication}")
            report.append("\n")
        else:
            report.append(f"### {protected_check.get('risk_level', '🟢 COMPLIANT')}\n")
            report.append("No direct use of protected attributes detected in model features.\n")
        
        # Proxy variables
        proxy_count = proxy_analysis.get('count', 0)
        if proxy_count > 0:
            risk_icon = "🔴" if proxy_count >= 3 else "🟡"
            report.append(f"### {risk_icon} Proxy Variables Detected: {proxy_count}\n")
            report.append("The following proxy variables may indirectly encode protected characteristics:\n")
            for proxy in proxy_analysis.get('detected_proxies', []):
                explanation = proxy_analysis.get('explanations', {}).get(proxy, '')
                report.append(f"- **{proxy}**: {explanation}")
            report.append("\n")
        else:
            report.append("### 🟢 No Proxy Variables Detected\n")
            report.append("No obvious proxy variables found in the feature set.\n")
        
        # Template findings - Data Bias
        data_bias_findings = template_findings.get('findings', {}).get('data_bias', [])
        if data_bias_findings:
            report.append("### Additional Data Quality Findings\n")
            for finding in data_bias_findings:
                icon = self._get_risk_icon(finding.get('risk_level', ''))
                report.append(f"**{icon} {finding.get('category', 'Finding')}**")
                report.append(f"- {finding.get('finding', '')}")
                report.append(f"- *{finding.get('explanation', '')}*")
                report.append(f"- Regulation: {finding.get('regulation', 'N/A')}\n")
        
        # Section 2: Discrimination Detection Results
        report.append("## 2. Discrimination Detection Results\n")
        
        di_ratio = di_analysis.get('disparate_impact')
        if di_ratio is not None:
            if di_ratio < 0.8:
                icon = "🔴"
            elif di_ratio < 1.0:
                icon = "🟡"
            else:
                icon = "🟢"
            
            report.append(f"### {icon} Disparate Impact Analysis\n")
            report.append(f"**Disparate Impact Ratio:** {di_ratio:.3f}")
            report.append(f"**Statistical Parity Difference:** {di_analysis.get('statistical_parity_difference', 0):.3f}")
            report.append(f"**Equal Opportunity Difference:** {di_analysis.get('equal_opportunity_difference', 0):.3f}\n")
            
            report.append("**Interpretation:**")
            report.append(f"{di_analysis.get('interpretation', 'No interpretation available')}\n")
            
            # Metrics detail
            metrics = di_analysis.get('metrics_detail', {})
            if metrics:
                report.append("**Detailed Metrics:**")
                report.append(f"- Privileged group selection rate: {metrics.get('privileged_selection_rate', 0):.1%}")
                report.append(f"- Unprivileged group selection rate: {metrics.get('unprivileged_selection_rate', 0):.1%}")
                report.append(f"- Total samples analyzed: {metrics.get('total_samples', 0):,}")
                report.append(f"- Privileged samples: {metrics.get('privileged_samples', 0):,}")
                report.append(f"- Unprivileged samples: {metrics.get('unprivileged_samples', 0):,}\n")
        
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
        
        # Section 3: Accountability & Governance
        report.append("## 3. Accountability & Governance\n")
        
        maturity = accountability_report.get('governance_maturity', {})
        report.append(f"**Governance Maturity Level:** {maturity.get('level_name', 'Unknown')} (Level {maturity.get('maturity_level', 0)})")
        report.append(f"**Maturity Score:** {maturity.get('score', 0)}/100")
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
        
        # Section 4: Data Privacy Compliance
        report.append("## 4. Data Privacy Compliance\n")
        
        privacy_findings = template_findings.get('findings', {}).get('privacy', [])
        if privacy_findings:
            report.append("### GDPR & Privacy Assessment\n")
            for finding in privacy_findings:
                icon = self._get_risk_icon(finding.get('risk_level', ''))
                report.append(f"**{icon} {finding.get('category', 'Finding')}**")
                report.append(f"- {finding.get('finding', '')}")
                report.append(f"- *{finding.get('explanation', '')}*")
                report.append(f"- Regulation: {finding.get('regulation', 'N/A')}\n")
        
        # Section 5: Remediation Recommendations
        report.append("## 5. Remediation Recommendations\n")
        
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
        report.append(f"\n**Composite Risk Score:** {composite_score}/100")
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
        Convert Markdown content to professionally styled PDF.
        
        Args:
            markdown_content: Markdown report content
            output_path: Path where PDF should be saved
        
        Returns:
            Path to generated PDF file or None if weasyprint not available
        """
        if not WEASYPRINT_AVAILABLE:
            print("Warning: weasyprint not available. Skipping PDF generation.")
            return None
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'nl2br']
        )
        
        # Add professional CSS styling
        css_style = """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "FairLens AI Bias Audit Report";
                font-size: 10pt;
                color: #666;
            }
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }
        
        h1 {
            color: #1e3a8a;
            font-size: 24pt;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 10px;
            margin-top: 0;
            margin-bottom: 20px;
        }
        
        h2 {
            color: #1e40af;
            font-size: 18pt;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #93c5fd;
            padding-bottom: 5px;
        }
        
        h3 {
            color: #1e40af;
            font-size: 14pt;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        
        p {
            margin-bottom: 10px;
            text-align: justify;
        }
        
        strong {
            color: #1f2937;
        }
        
        em {
            color: #4b5563;
        }
        
        ul, ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        
        li {
            margin-bottom: 5px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 10pt;
        }
        
        th {
            background-color: #3b82f6;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: bold;
        }
        
        td {
            border: 1px solid #e5e7eb;
            padding: 8px;
        }
        
        tr:nth-child(even) {
            background-color: #f9fafb;
        }
        
        hr {
            border: none;
            border-top: 1px solid #d1d5db;
            margin: 30px 0;
        }
        
        code {
            background-color: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        
        .risk-high {
            color: #dc2626;
            font-weight: bold;
        }
        
        .risk-medium {
            color: #f59e0b;
            font-weight: bold;
        }
        
        .risk-low {
            color: #10b981;
            font-weight: bold;
        }
        """
        
        # Wrap HTML with proper structure
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>FairLens AI Bias Audit Report</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        if WEASYPRINT_AVAILABLE:
            HTML(string=full_html).write_pdf(
                output_path,
                stylesheets=[CSS(string=css_style, font_config=self.font_config)],
                font_config=self.font_config
            )
            return output_path
        return None
    
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