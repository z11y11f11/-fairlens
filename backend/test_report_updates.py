"""
Test script to verify report generator updates
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from audit.report_generator import AuditReportGenerator
from datetime import datetime

# Create sample data with DI results
audit_results = {
    'disparate_impact_analysis': {
        'disparate_impact': 0.75,  # Below 0.8 - should trigger HIGH PRIORITY
        'statistical_parity_difference': -0.05,
        'equal_opportunity_difference': -0.03,
        'interpretation': 'DI ratio of 0.75 indicates potential discrimination',
        'metrics_detail': {
            'privileged_selection_rate': 0.60,
            'unprivileged_selection_rate': 0.45,
            'total_samples': 1000,
            'privileged_samples': 600,
            'unprivileged_samples': 400
        },
        'protected_attributes': {
            'gender': {
                'di_ratio': 0.55,  # Below 0.6 - should trigger URGENT
                'group_stats': {
                    'Male': {'rate': 0.65, 'count': 500},
                    'Female': {'rate': 0.36, 'count': 500}
                }
            },
            'ethnicity': {
                'di_ratio': 0.85,  # Between 0.8-0.9 - should trigger MEDIUM
                'group_stats': {
                    'White': {'rate': 0.60, 'count': 400},
                    'Black': {'rate': 0.51, 'count': 300},
                    'Hispanic': {'rate': 0.52, 'count': 300}
                }
            },
            'age_group': {
                'di_ratio': 0.95,  # Above 0.9 - should be COMPLIANT
                'group_stats': {
                    'Young': {'rate': 0.58, 'count': 400},
                    'Middle': {'rate': 0.55, 'count': 400},
                    'Senior': {'rate': 0.55, 'count': 200}
                }
            }
        }
    },
    'proxy_variable_analysis': {},
    'protected_attributes_check': {},
    'composite_risk_score': {
        'composite_score': 65,
        'risk_level': 'MEDIUM RISK 🟡'
    }
}

template_findings = {
    'findings': {
        'discrimination': [],
        'accountability': [],
        'privacy': []
    },
    'recommendations': [],
    'next_review_date': '2026-08-03'
}

accountability_report = {
    'audit_trail': {
        'audit_id': 'TEST-REPORT-001',
        'timestamp': datetime.now().isoformat(),
        'submitter': 'Test User',
        'model_version': '1.0.0'
    },
    'governance_maturity': {
        'level_name': 'Defined',
        'maturity_level': 2,
        'score': 60,
        'risk': 'MEDIUM'
    },
    'raci_matrix': {
        'matrix': {}  # Empty to test standard template
    },
    'accountability_gaps': []
}

# Generate report
print("=" * 80)
print("Testing Report Generator Updates")
print("=" * 80)

generator = AuditReportGenerator()
markdown_report = generator.generate_markdown_report(
    audit_results,
    template_findings,
    accountability_report
)

# Print relevant sections
print("\n" + "=" * 80)
print("SECTION 2: Accountability & Governance (RACI Matrix)")
print("=" * 80)
lines = markdown_report.split('\n')
in_section2 = False
for i, line in enumerate(lines):
    if '## 2. Accountability & Governance' in line:
        in_section2 = True
    elif in_section2 and line.startswith('## 3.'):
        break
    elif in_section2:
        print(line)

print("\n" + "=" * 80)
print("SECTION 3: Data Privacy Compliance (GDPR Checklist)")
print("=" * 80)
in_section3 = False
for i, line in enumerate(lines):
    if '## 3. Data Privacy Compliance' in line:
        in_section3 = True
    elif in_section3 and line.startswith('## 4.'):
        break
    elif in_section3:
        print(line)

print("\n" + "=" * 80)
print("SECTION 4: Remediation Recommendations (Auto-generated from DI)")
print("=" * 80)
in_section4 = False
for i, line in enumerate(lines):
    if '## 4. Remediation Recommendations' in line:
        in_section4 = True
    elif in_section4 and line.startswith('## Audit Trail'):
        break
    elif in_section4:
        print(line)

print("\n" + "=" * 80)
print("✅ Report generation test complete!")
print("=" * 80)

# Save full report for inspection
output_path = 'reports/test_report_with_updates.md'
os.makedirs('reports', exist_ok=True)
with open(output_path, 'w') as f:
    f.write(markdown_report)
print(f"\n📄 Full report saved to: {output_path}")

# Made with Bob
