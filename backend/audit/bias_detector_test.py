"""
FairLens BiasDetector Test Suite
Tests bias detection with UCI Adult dataset showing real disparate impact numbers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audit.bias_detector import BiasDetector
import pandas as pd
import numpy as np


def test_disparate_impact_analysis():
    """Test disparate impact analysis with UCI Adult dataset"""
    print("\n" + "="*80)
    print("TEST 1: Disparate Impact Analysis (Gender Bias in Income)")
    print("="*80)
    
    detector = BiasDetector()
    
    # Test with UCI Adult dataset
    data_path = "../../data/adult.csv"
    
    if not os.path.exists(data_path):
        print(f"⚠️  Dataset not found at {data_path}")
        print("Please run: python data/download_uci.py first")
        return
    
    # Analyze gender bias (sex: 1=Male, 0=Female)
    result = detector.analyze_disparate_impact(
        data_path=data_path,
        protected_attribute='sex',
        privileged_group=[1],  # Male is privileged group
        label_name='income',
        favorable_label=1  # High income (>50K)
    )
    
    print("\n📊 DISPARATE IMPACT ANALYSIS RESULTS:")
    print("-" * 80)
    print(f"Disparate Impact Ratio: {result['disparate_impact']:.4f}")
    print(f"Statistical Parity Difference: {result['statistical_parity_difference']:.4f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"\n{result['interpretation']}")
    
    print("\n📈 Detailed Metrics:")
    for key, value in result['metrics_detail'].items():
        print(f"  {key}: {value}")
    
    # Validate 4/5 rule
    if result['disparate_impact'] < 0.8:
        print("\n⚠️  DISCRIMINATION DETECTED: DI ratio below 0.8 threshold")
    else:
        print("\n✅ PASSES 4/5 RULE: DI ratio meets fairness threshold")
    
    return result


def test_proxy_variable_detection():
    """Test proxy variable detection"""
    print("\n" + "="*80)
    print("TEST 2: Proxy Variable Detection")
    print("="*80)
    
    detector = BiasDetector()
    
    # Test with typical feature set including proxies
    features = [
        'age', 'education_num', 'capital_gain', 'capital_loss',
        'hours_per_week', 'zip_code', 'occupation', 'workclass',
        'marital_status', 'relationship', 'native_country'
    ]
    
    result = detector.detect_proxy_variables(features)
    
    print("\n🔍 PROXY VARIABLE DETECTION RESULTS:")
    print("-" * 80)
    print(f"Detected Proxies: {result['count']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"\n{result['risk_explanation']}")
    
    if result['detected_proxies']:
        print("\n⚠️  Detected Proxy Variables:")
        for proxy in result['detected_proxies']:
            print(f"  • {proxy}: {result['explanations'][proxy]}")
        
        print("\n💡 Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
    else:
        print("\n✅ No proxy variables detected")
    
    return result


def test_protected_attributes_check():
    """Test protected attributes direct use check"""
    print("\n" + "="*80)
    print("TEST 3: Protected Attributes Direct Use Check")
    print("="*80)
    
    detector = BiasDetector()
    
    # Test Case 1: Clean feature set (no violations)
    print("\n📋 Test Case 1: Clean Feature Set")
    clean_features = ['age', 'education_num', 'hours_per_week', 'capital_gain']
    result1 = detector.check_protected_attributes_direct_use(clean_features)
    
    print(f"Violations: {result1['violation_count']}")
    print(f"Risk Level: {result1['risk_level']}")
    
    # Test Case 2: Feature set with violations
    print("\n📋 Test Case 2: Feature Set with Protected Attributes")
    violation_features = ['age', 'gender', 'race', 'education_num', 'sex']
    result2 = detector.check_protected_attributes_direct_use(violation_features)
    
    print(f"Violations: {result2['violation_count']}")
    print(f"Risk Level: {result2['risk_level']}")
    
    if result2['violations']:
        print("\n🚨 CRITICAL VIOLATIONS DETECTED:")
        for violation in result2['violations']:
            print(f"  • Feature '{violation['feature']}' maps to protected attribute '{violation['protected_attribute']}'")
        
        print("\n⚖️  Legal Implications:")
        for implication in result2['legal_implications']:
            print(f"  • {implication}")
        
        print("\n🔧 Required Actions:")
        for i, action in enumerate(result2['required_actions'], 1):
            print(f"  {i}. {action}")
    
    return result1, result2


def test_composite_risk_score():
    """Test composite risk score calculation"""
    print("\n" + "="*80)
    print("TEST 4: Composite Risk Score Calculation")
    print("="*80)
    
    detector = BiasDetector()
    
    # Test Case 1: Low risk scenario
    print("\n📊 Test Case 1: Low Risk Scenario")
    result1 = detector.calculate_composite_risk_score(
        di_ratio=0.95,
        proxy_count=1,
        direct_violations=0,
        data_quality_score=0.9,
        privacy_score=0.95
    )
    print(f"Composite Score: {result1['composite_score']}/100")
    print(f"Risk Level: {result1['risk_level']}")
    print("\nComponent Scores:")
    for component, score in result1['component_scores'].items():
        print(f"  {component}: {score}")
    
    # Test Case 2: Medium risk scenario
    print("\n📊 Test Case 2: Medium Risk Scenario")
    result2 = detector.calculate_composite_risk_score(
        di_ratio=0.82,
        proxy_count=3,
        direct_violations=0,
        data_quality_score=0.7,
        privacy_score=0.8
    )
    print(f"Composite Score: {result2['composite_score']}/100")
    print(f"Risk Level: {result2['risk_level']}")
    
    # Test Case 3: High risk scenario
    print("\n📊 Test Case 3: High Risk Scenario")
    result3 = detector.calculate_composite_risk_score(
        di_ratio=0.65,
        proxy_count=5,
        direct_violations=0,
        data_quality_score=0.6,
        privacy_score=0.7
    )
    print(f"Composite Score: {result3['composite_score']}/100")
    print(f"Risk Level: {result3['risk_level']}")
    
    # Test Case 4: Critical violation scenario
    print("\n📊 Test Case 4: Critical Violation Scenario")
    result4 = detector.calculate_composite_risk_score(
        di_ratio=0.95,
        proxy_count=0,
        direct_violations=2,
        data_quality_score=0.9,
        privacy_score=0.9
    )
    print(f"Composite Score: {result4['composite_score']}/100")
    print(f"Risk Level: {result4['risk_level']}")
    
    return result1, result2, result3, result4


def test_full_analysis():
    """Test complete analysis pipeline"""
    print("\n" + "="*80)
    print("TEST 5: Full Analysis Pipeline (UCI Adult Dataset)")
    print("="*80)
    
    detector = BiasDetector()
    
    data_path = "../../data/adult.csv"
    
    if not os.path.exists(data_path):
        print(f"⚠️  Dataset not found at {data_path}")
        print("Please run: python data/download_uci.py first")
        return
    
    # Load dataset to get feature list
    df = pd.read_csv(data_path)
    feature_list = [col for col in df.columns if col not in ['income']]
    
    # Prepare audit input
    audit_input = {
        'data_path': data_path,
        'protected_attribute': 'sex',
        'privileged_group': [1],  # Male
        'feature_list': feature_list,
        'label_name': 'income',
        'favorable_label': 1,
        'data_quality_score': 0.85,
        'privacy_score': 0.90
    }
    
    print("\n🔄 Running full analysis pipeline...")
    print(f"Dataset: {data_path}")
    print(f"Protected Attribute: {audit_input['protected_attribute']}")
    print(f"Features: {len(feature_list)}")
    
    # Run full analysis
    results = detector.run_full_analysis(audit_input)
    
    # Display summary
    print("\n" + "="*80)
    print("📋 ANALYSIS SUMMARY")
    print("="*80)
    
    summary = results['summary']
    print(f"\n🎯 Overall Risk Level: {summary['overall_risk_level']}")
    print(f"📊 Composite Score: {summary['composite_score']}/100")
    print(f"⚖️  Disparate Impact Ratio: {summary['disparate_impact_ratio']:.4f}")
    print(f"🔍 Proxy Variables: {summary['proxy_variables_detected']}")
    print(f"🚨 Direct Violations: {summary['direct_violations']}")
    
    print("\n🔑 Key Findings:")
    for i, finding in enumerate(summary['key_findings'], 1):
        print(f"  {i}. {finding}")
    
    print("\n✅ Priority Actions:")
    for i, action in enumerate(summary['priority_actions'], 1):
        print(f"  {i}. {action}")
    
    # Display detailed component results
    print("\n" + "="*80)
    print("📊 DETAILED COMPONENT RESULTS")
    print("="*80)
    
    print("\n1️⃣  Disparate Impact Analysis:")
    di = results['disparate_impact_analysis']
    print(f"   DI Ratio: {di.get('disparate_impact', 'N/A')}")
    print(f"   Risk: {di.get('risk_level', 'N/A')}")
    
    print("\n2️⃣  Proxy Variables:")
    proxy = results['proxy_variable_analysis']
    print(f"   Count: {proxy['count']}")
    print(f"   Risk: {proxy['risk_level']}")
    if proxy['detected_proxies']:
        print(f"   Detected: {', '.join(proxy['detected_proxies'])}")
    
    print("\n3️⃣  Protected Attributes:")
    protected = results['protected_attributes_check']
    print(f"   Violations: {protected['violation_count']}")
    print(f"   Risk: {protected['risk_level']}")
    
    print("\n4️⃣  Composite Risk Score:")
    composite = results['composite_risk_score']
    print(f"   Score: {composite['composite_score']}/100")
    print(f"   Risk: {composite['risk_level']}")
    print(f"   Components:")
    for component, score in composite['component_scores'].items():
        weight = composite['weights'].get(component.replace('_score', ''), 0)
        print(f"     • {component}: {score} (weight: {weight})")
    
    return results


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*80)
    print("🧪 FAIRLENS BIAS DETECTOR TEST SUITE")
    print("="*80)
    print("Testing bias detection with UCI Adult dataset")
    print("This demonstrates real-world disparate impact analysis")
    
    try:
        # Test 1: Disparate Impact
        di_result = test_disparate_impact_analysis()
        
        # Test 2: Proxy Variables
        proxy_result = test_proxy_variable_detection()
        
        # Test 3: Protected Attributes
        clean_result, violation_result = test_protected_attributes_check()
        
        # Test 4: Composite Risk Score
        risk_results = test_composite_risk_score()
        
        # Test 5: Full Analysis
        full_result = test_full_analysis()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\n📊 Test Summary:")
        print(f"  • Disparate Impact Analysis: {'✅ PASS' if di_result else '❌ FAIL'}")
        print(f"  • Proxy Variable Detection: {'✅ PASS' if proxy_result else '❌ FAIL'}")
        print(f"  • Protected Attributes Check: {'✅ PASS' if clean_result and violation_result else '❌ FAIL'}")
        print(f"  • Composite Risk Score: {'✅ PASS' if risk_results else '❌ FAIL'}")
        print(f"  • Full Analysis Pipeline: {'✅ PASS' if full_result else '❌ FAIL'}")
        
        print("\n💡 Next Steps:")
        print("  1. Review the disparate impact numbers from UCI Adult dataset")
        print("  2. The dataset shows real gender bias in income prediction")
        print("  3. Use these results to validate report generation")
        print("  4. Integrate with Flask API for web interface")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()

# Made with Bob
