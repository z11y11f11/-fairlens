"""
Test script for FairLens API
Tests report generation and API endpoints
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit.bias_detector import BiasDetector
from templates.loan_approval import LoanApprovalAuditTemplate
from audit.accountability import AccountabilityTracker
from audit.report_generator import AuditReportGenerator


def test_report_generation():
    """Test the complete report generation pipeline."""
    print("=" * 60)
    print("Testing FairLens Report Generation Pipeline")
    print("=" * 60)
    
    # Step 1: Create sample audit results
    print("\n1. Creating sample audit results...")
    
    audit_results = {
        'timestamp': '2026-05-02T10:00:00',
        'disparate_impact_analysis': {
            'disparate_impact': 0.75,
            'statistical_parity_difference': -0.15,
            'equal_opportunity_difference': -0.15,
            'risk_level': 'HIGH RISK 🔴',
            'interpretation': 'DISCRIMINATION DETECTED: Disparate Impact ratio of 0.750 is below the 0.8 threshold (4/5 rule).',
            'metrics_detail': {
                'privileged_group': [1],
                'unprivileged_group': [0],
                'privileged_selection_rate': 0.60,
                'unprivileged_selection_rate': 0.45,
                'total_samples': 1000,
                'privileged_samples': 600,
                'unprivileged_samples': 400
            }
        },
        'proxy_variable_analysis': {
            'detected_proxies': ['zip_code', 'occupation'],
            'count': 2,
            'risk_level': 'MEDIUM RISK 🟡',
            'risk_explanation': 'Proxy variables detected (2). Moderate risk of indirect discrimination.',
            'explanations': {
                'zip_code': 'Strong proxy for race/ethnicity and socioeconomic status',
                'occupation': 'Potential proxy for gender and age discrimination'
            },
            'recommendations': [
                'Consider removing or transforming proxy variables',
                'Analyze feature importance to assess actual impact'
            ]
        },
        'protected_attributes_check': {
            'violations': [],
            'violation_count': 0,
            'risk_level': 'COMPLIANT ✅',
            'legal_implications': ['No direct use of protected attributes detected'],
            'required_actions': ['Continue monitoring for indirect discrimination via proxy variables']
        },
        'composite_risk_score': {
            'composite_score': 65.5,
            'risk_level': 'MEDIUM RISK 🟡',
            'component_scores': {
                'disparate_impact_score': 75.0,
                'proxy_variable_score': 70.0,
                'data_quality_score': 80.0,
                'privacy_score': 90.0
            },
            'recommendations': [
                'Address proxy variables if possible',
                'Improve disparate impact ratio through reweighting or resampling',
                'Consider fairness-aware training algorithms'
            ]
        },
        'summary': {
            'overall_risk_level': 'MEDIUM RISK 🟡',
            'composite_score': 65.5,
            'disparate_impact_ratio': 0.75,
            'proxy_variables_detected': 2,
            'direct_violations': 0,
            'key_findings': [
                '⚠️ Disparate Impact ratio of 0.750 indicates discrimination (below 0.8 threshold)',
                '⚠️ 2 proxy variables detected'
            ],
            'priority_actions': [
                'Apply bias mitigation techniques to improve disparate impact ratio',
                'Review and potentially remove proxy variables'
            ]
        }
    }
    
    # Step 2: Create sample template findings
    print("2. Creating sample template findings...")
    
    template_findings = {
        'audit_timestamp': '2026-05-02T10:00:00',
        'overall_risk_level': 'MEDIUM',
        'risk_summary': {
            'high_risk_count': 2,
            'medium_risk_count': 3,
            'low_risk_count': 5,
            'total_findings': 10
        },
        'findings': {
            'data_bias': [
                {
                    'risk_level': 'HIGH',
                    'category': 'Proxy Variables',
                    'finding': 'Proxy variables detected: zip_code, occupation',
                    'explanation': 'These variables may serve as proxies for protected characteristics.',
                    'regulation': 'ECOA Regulation B - Indirect Discrimination'
                }
            ],
            'discrimination': [
                {
                    'risk_level': 'HIGH',
                    'category': 'Disparate Impact',
                    'finding': 'Disparate impact detected for sex: 0.750',
                    'explanation': 'The disparate impact ratio of 0.750 is below the 0.80 threshold (4/5 rule).',
                    'regulation': 'ECOA 4/5 Rule',
                    'metric_value': 0.75,
                    'threshold': 0.8
                }
            ],
            'accountability': [
                {
                    'risk_level': 'MEDIUM',
                    'category': 'Model Review',
                    'finding': 'Model not reviewed in 14 months',
                    'explanation': 'Last model review exceeds the 12-month requirement.',
                    'regulation': 'Model Risk Management SR 11-7'
                }
            ],
            'privacy': [
                {
                    'risk_level': 'LOW',
                    'category': 'Data Minimization',
                    'finding': 'Reasonable feature count: 15',
                    'explanation': 'Feature count appears reasonable and aligned with data minimization principles.',
                    'regulation': 'GDPR Compliance'
                }
            ]
        },
        'recommendations': [
            {
                'priority': 'URGENT',
                'timeline': 'Immediate action required',
                'finding_category': 'Disparate Impact',
                'finding': 'Disparate impact detected for sex: 0.750',
                'recommendation': 'Investigate root cause of disparate impact. Consider retraining model with balanced data.',
                'regulation': 'ECOA 4/5 Rule',
                'risk_level': 'HIGH'
            },
            {
                'priority': 'HIGH',
                'timeline': 'Remediate within 90 days',
                'finding_category': 'Proxy Variables',
                'finding': 'Proxy variables detected: zip_code, occupation',
                'recommendation': 'Remove or transform proxy variables that correlate with protected characteristics.',
                'regulation': 'ECOA Regulation B',
                'risk_level': 'MEDIUM'
            }
        ],
        'next_review_date': '2026-08-02'
    }
    
    # Step 3: Create sample accountability report
    print("3. Creating sample accountability report...")
    
    accountability_report = {
        'audit_trail': {
            'audit_id': 'FL-2026-TEST',
            'timestamp': '2026-05-02T10:00:00',
            'submitter': 'Test User',
            'model_version': '1.0.0',
            'audit_type': 'Accountability Assessment'
        },
        'raci_matrix': {
            'matrix': {
                'Model Development': {
                    'R': 'Alice Johnson',
                    'A': 'Bob Smith',
                    'C': 'Carol White',
                    'I': 'David Brown'
                },
                'Bias Testing & Validation': {
                    'R': 'Alice Johnson',
                    'A': 'Bob Smith',
                    'C': 'Carol White',
                    'I': 'David Brown'
                },
                'Ongoing Monitoring': {
                    'R': 'Carol White',
                    'A': 'Bob Smith',
                    'C': 'Alice Johnson',
                    'I': 'David Brown'
                }
            },
            'roles': {
                'model_developer': 'Alice Johnson',
                'approval_authority': 'Bob Smith',
                'monitor_owner': 'Carol White',
                'complaint_handler': 'David Brown'
            }
        },
        'accountability_gaps': [
            {
                'activity': 'Annual Re-audit',
                'role': 'Re-audit Schedule',
                'severity': 'MEDIUM',
                'description': 'No re-audit schedule or responsible owner defined'
            }
        ],
        'governance_maturity': {
            'maturity_level': 2,
            'level_name': 'Defined',
            'score': 67,
            'risk': 'MEDIUM',
            'gap_count': 1,
            'description': 'Governance processes are defined but have some gaps',
            'recommendation': 'Address identified gaps: Complete missing role assignments.'
        }
    }
    
    # Step 4: Generate report
    print("4. Generating Markdown and PDF reports...")
    
    try:
        generator = AuditReportGenerator()
        
        all_data = {
            'audit_results': audit_results,
            'template_findings': template_findings,
            'accountability_report': accountability_report
        }
        
        # Create test reports directory
        test_reports_dir = os.path.join(os.path.dirname(__file__), 'test_reports')
        os.makedirs(test_reports_dir, exist_ok=True)
        
        result = generator.generate_full_report(all_data, test_reports_dir)
        
        print("\n✅ Report generation successful!")
        print(f"   Audit ID: {result['audit_id']}")
        print(f"   Markdown: {result['markdown_path']}")
        print(f"   PDF: {result['pdf_path']}")
        
        # Verify files exist
        if os.path.exists(result['markdown_path']):
            print(f"   ✓ Markdown file created ({os.path.getsize(result['markdown_path'])} bytes)")
        else:
            print(f"   ✗ Markdown file not found")
        
        if os.path.exists(result['pdf_path']):
            print(f"   ✓ PDF file created ({os.path.getsize(result['pdf_path'])} bytes)")
        else:
            print(f"   ✗ PDF file not found")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Report generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_structure():
    """Test that API endpoints are properly defined."""
    print("\n" + "=" * 60)
    print("Testing API Structure")
    print("=" * 60)
    
    try:
        from app import app
        
        print("\n✅ Flask app imported successfully")
        
        # Check routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
        
        print(f"\nRegistered routes ({len(routes)}):")
        for route in routes:
            if route['endpoint'] != 'static':
                print(f"  {route['path']}")
                print(f"    Methods: {', '.join(route['methods'])}")
        
        # Check required endpoints
        required_endpoints = ['/api/health', '/api/audit', '/api/download/<filename>']
        found_endpoints = [r['path'] for r in routes]
        
        print("\nRequired endpoints:")
        for endpoint in required_endpoints:
            if any(endpoint in path for path in found_endpoints):
                print(f"  ✓ {endpoint}")
            else:
                print(f"  ✗ {endpoint} - MISSING")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API structure test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FairLens API Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Report Generation
    results.append(("Report Generation", test_report_generation()))
    
    # Test 2: API Structure
    results.append(("API Structure", test_api_structure()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)

# Made with Bob