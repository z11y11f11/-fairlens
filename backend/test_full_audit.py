#!/usr/bin/env python3
"""
Test full audit with real UCI data
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit.bias_detector import BiasDetector

def main():
    print("=" * 80)
    print("FairLens Full Audit Test with Real UCI Data")
    print("=" * 80)
    print()
    
    # Initialize detector
    detector = BiasDetector()
    
    # Prepare audit input
    audit_input = {
        'data_path': 'data/adult_train_processed.csv',
        'protected_attribute': 'sex_binary',
        'privileged_group': [1],  # Male = 1
        'feature_list': [
            'age', 'workclass', 'education', 'marital-status', 'occupation',
            'relationship', 'race', 'sex', 'capital-gain', 'capital-loss',
            'hours-per-week', 'native-country'
        ],
        'label_name': 'loan_approved',
        'favorable_label': 1,
        'data_quality_score': 0.85,
        'privacy_score': 0.90
    }
    
    print("Running full bias analysis...")
    print()
    
    # Run full analysis
    results = detector.run_full_analysis(audit_input)
    
    # Display results
    print("=" * 80)
    print("AUDIT RESULTS")
    print("=" * 80)
    print()
    
    # Summary
    summary = results.get('summary', {})
    print("OVERALL RISK ASSESSMENT:")
    print(f"  Risk Level: {summary.get('overall_risk_level', 'N/A')}")
    print(f"  Composite Score: {summary.get('composite_score', 'N/A')}/100")
    print()
    
    # Disparate Impact
    di_analysis = results.get('disparate_impact_analysis', {})
    print("DISPARATE IMPACT ANALYSIS:")
    print(f"  DI Ratio: {di_analysis.get('disparate_impact', 'N/A'):.3f}")
    print(f"  Risk Level: {di_analysis.get('risk_level', 'N/A')}")
    print(f"  Statistical Parity Diff: {di_analysis.get('statistical_parity_difference', 'N/A'):.3f}")
    print()
    
    if 'metrics_detail' in di_analysis:
        details = di_analysis['metrics_detail']
        print("  Detailed Metrics:")
        print(f"    Privileged (Male) approval rate: {details.get('privileged_selection_rate', 0):.1%}")
        print(f"    Unprivileged (Female) approval rate: {details.get('unprivileged_selection_rate', 0):.1%}")
        print(f"    Total samples: {details.get('total_samples', 0):,}")
        print()
    
    print("  Interpretation:")
    print(f"    {di_analysis.get('interpretation', 'N/A')}")
    print()
    
    # Proxy Variables
    proxy_analysis = results.get('proxy_variable_analysis', {})
    print("PROXY VARIABLE DETECTION:")
    print(f"  Detected: {proxy_analysis.get('count', 0)} proxy variables")
    print(f"  Risk Level: {proxy_analysis.get('risk_level', 'N/A')}")
    if proxy_analysis.get('detected_proxies'):
        print(f"  Variables: {', '.join(proxy_analysis['detected_proxies'])}")
    print()
    
    # Protected Attributes
    protected_check = results.get('protected_attributes_check', {})
    print("PROTECTED ATTRIBUTES CHECK:")
    print(f"  Direct violations: {protected_check.get('violation_count', 0)}")
    print(f"  Status: {protected_check.get('risk_level', 'N/A')}")
    print()
    
    # Key Findings
    print("KEY FINDINGS:")
    for i, finding in enumerate(summary.get('key_findings', []), 1):
        print(f"  {i}. {finding}")
    print()
    
    # Priority Actions
    print("PRIORITY ACTIONS:")
    for i, action in enumerate(summary.get('priority_actions', []), 1):
        print(f"  {i}. {action}")
    print()
    
    print("=" * 80)
    print("✓ Full audit completed!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Made with Bob
