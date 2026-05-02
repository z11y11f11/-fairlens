#!/usr/bin/env python3
"""
Test script to verify real Disparate Impact calculation from UCI Adult dataset
"""

import sys
import os
import pandas as pd

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audit.bias_detector import BiasDetector

def main():
    print("=" * 80)
    print("Testing Real Disparate Impact Calculation")
    print("=" * 80)
    print()
    
    # Load real data
    data_path = 'data/adult_train_processed.csv'
    print(f"Loading data from: {data_path}")
    
    try:
        df = pd.read_csv(data_path)
        print(f"✓ Loaded {len(df)} records")
        print()
        
        # Check columns
        print("Available columns:")
        print(f"  - sex: {df['sex'].dtype}")
        print(f"  - sex_binary: {df['sex_binary'].dtype if 'sex_binary' in df.columns else 'NOT FOUND'}")
        print(f"  - loan_approved: {df['loan_approved'].dtype}")
        print()
        
        # Check sex distribution
        print("Sex distribution:")
        print(df['sex'].value_counts())
        print()
        
        if 'sex_binary' in df.columns:
            print("Sex_binary distribution:")
            print(df['sex_binary'].value_counts())
            print()
        
        # Check loan approval distribution
        print("Loan approval distribution:")
        print(df['loan_approved'].value_counts())
        print()
        
        # Calculate approval rates by sex
        print("Approval rate by sex:")
        approval_by_sex = df.groupby('sex')['loan_approved'].agg(['mean', 'count'])
        print(approval_by_sex)
        print()
        
        if 'sex_binary' in df.columns:
            print("Approval rate by sex_binary:")
            approval_by_sex_binary = df.groupby('sex_binary')['loan_approved'].agg(['mean', 'count'])
            print(approval_by_sex_binary)
            print()
        
        # Run bias detection with sex_binary (numeric)
        print("=" * 80)
        print("Running BiasDetector with sex_binary (numeric)...")
        print("=" * 80)
        print()
        
        detector = BiasDetector()
        
        # Use sex_binary for proper numeric comparison
        result = detector.analyze_disparate_impact(
            data_path=data_path,
            protected_attribute='sex_binary',
            privileged_group=[1],  # Male = 1
            label_name='loan_approved',
            favorable_label=1
        )
        
        print("RESULTS:")
        print(f"  Disparate Impact Ratio: {result.get('disparate_impact', 'ERROR')}")
        print(f"  Risk Level: {result.get('risk_level', 'ERROR')}")
        print()
        
        if 'metrics_detail' in result:
            details = result['metrics_detail']
            print("DETAILED METRICS:")
            print(f"  Privileged group (Male): {details.get('privileged_group')}")
            print(f"  Unprivileged group (Female): {details.get('unprivileged_group')}")
            print(f"  Privileged selection rate: {details.get('privileged_selection_rate', 0):.3f}")
            print(f"  Unprivileged selection rate: {details.get('unprivileged_selection_rate', 0):.3f}")
            print(f"  Total samples: {details.get('total_samples')}")
            print(f"  Privileged samples: {details.get('privileged_samples')}")
            print(f"  Unprivileged samples: {details.get('unprivileged_samples')}")
            print()
        
        print("INTERPRETATION:")
        print(f"  {result.get('interpretation', 'No interpretation available')}")
        print()
        
        # Calculate expected DI manually for verification
        if 'sex_binary' in df.columns:
            male_approval = df[df['sex_binary'] == 1]['loan_approved'].mean()
            female_approval = df[df['sex_binary'] == 0]['loan_approved'].mean()
            manual_di = female_approval / male_approval if male_approval > 0 else 0
            
            print("=" * 80)
            print("MANUAL VERIFICATION:")
            print(f"  Male approval rate: {male_approval:.3f}")
            print(f"  Female approval rate: {female_approval:.3f}")
            print(f"  Manual DI calculation: {manual_di:.3f}")
            print(f"  BiasDetector DI: {result.get('disparate_impact', 'ERROR')}")
            print(f"  Match: {'✓ YES' if abs(manual_di - result.get('disparate_impact', 0)) < 0.001 else '✗ NO'}")
            print()
        
        # Check if DI is below threshold
        di_value = result.get('disparate_impact')
        if di_value is not None:
            if di_value < 0.8:
                print("⚠️  WARNING: Disparate Impact below 0.8 threshold - DISCRIMINATION DETECTED")
            elif di_value < 1.0:
                print("⚠️  CAUTION: Disparate Impact below 1.0 - Some disparity exists")
            else:
                print("✓ PASS: Disparate Impact >= 1.0 - No adverse impact")
        
        print()
        print("=" * 80)
        print("✓ Test completed successfully!")
        print("=" * 80)
        
        return True
        
    except FileNotFoundError:
        print(f"✗ ERROR: File not found: {data_path}")
        print("Please ensure the UCI Adult dataset has been downloaded.")
        return False
        
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Made with Bob
