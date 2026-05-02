#!/usr/bin/env python3
"""
Demo Run Script for FairLens
Simulates a complete audit using the demo scenario with UCI Adult dataset
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_demo_audit():
    """
    Run a complete audit using the demo scenario:
    - Model: XGBoost Credit Scoring
    - Features: age, gender, income, zip_code, occupation, credit_history
    - Training data: 2015-2020 historical loan decisions
    - Institution: City Commercial Bank
    """
    
    print("=" * 80)
    print("FairLens Demo Run - End-to-End Audit Test")
    print("=" * 80)
    print()
    
    # Demo scenario data - matching API expected format
    audit_request = {
        "model_info": {
            "name": "XGBoost Credit Scoring",
            "type": "classification",
            "version": "1.0.0",
            "use_case": "loan_approval"
        },
        "features": [
            "age",
            "workclass",
            "education",
            "marital-status",
            "occupation",
            "relationship",
            "race",
            "sex",
            "capital-gain",
            "capital-loss",
            "hours-per-week",
            "native-country"
        ],
        "data_info": {
            "data_path": "data/adult_train_processed.csv",
            "protected_attribute": "sex_binary",
            "privileged_group": [1],  # Male = 1
            "label_name": "loan_approved",
            "favorable_label": 1,  # Approved = 1
            "training_period": {
                "start_date": "2015-01-01",
                "end_date": "2020-12-31"
            },
            "data_source": "UCI Adult Dataset",
            "data_quality_score": 0.85,
            "privacy_score": 0.90
        },
        "raci_data": {
            "responsible": "Data Science Team",
            "accountable": "Chief AI Officer",
            "consulted": "Legal & Compliance",
            "informed": "Executive Board",
            "institution": "City Commercial Bank",
            "model_version": "1.0.0"
        }
    }
    
    print("Demo Scenario:")
    print(f"  Model: {audit_request['model_info']['name']}")
    print(f"  Features: {len(audit_request['features'])} features from UCI Adult dataset")
    print(f"  Protected Attribute: {audit_request['data_info']['protected_attribute']}")
    training_period = audit_request['data_info']['training_period']
    print(f"  Training Period: {training_period['start_date']} to {training_period['end_date']}")
    print(f"  Institution: {audit_request['raci_data']['institution']}")
    print()
    
    # Check if Flask backend is running
    backend_url = "http://localhost:5001"
    
    try:
        print("Checking if Flask backend is running...")
        response = requests.get(f"{backend_url}/api/health", timeout=2)
        print(f"✓ Backend is running (status: {response.status_code})")
        print()
    except requests.exceptions.RequestException as e:
        print("✗ Backend is not running!")
        print("Please start the Flask backend first:")
        print("  cd /Users/Qulei/Desktop/fairlens")
        print("  source venv/bin/activate")
        print("  python backend/app.py")
        print()
        return False
    
    # Send audit request
    print("Sending audit request to backend...")
    try:
        response = requests.post(
            f"{backend_url}/api/audit",
            json=audit_request,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✓ Audit completed successfully!")
            print()
            
            # Parse response
            audit_results = response.json()
            
            # Display results
            print("=" * 80)
            print("AUDIT RESULTS")
            print("=" * 80)
            print()
            
            # Risk Summary
            if "risk_summary" in audit_results:
                risk = audit_results["risk_summary"]
                print("RISK SUMMARY:")
                print(f"  Overall Risk Level: {risk.get('overall_risk', 'N/A')}")
                print(f"  Risk Score: {risk.get('risk_score', 'N/A')}")
                print()
            
            # Bias Metrics
            if "bias_metrics" in audit_results:
                metrics = audit_results["bias_metrics"]
                print("BIAS METRICS:")
                
                if "disparate_impact" in metrics:
                    di = metrics["disparate_impact"]
                    print(f"\n  Disparate Impact (Gender):")
                    print(f"    Male approval rate: {di.get('male_rate', 'N/A'):.2%}")
                    print(f"    Female approval rate: {di.get('female_rate', 'N/A'):.2%}")
                    print(f"    DI Ratio: {di.get('ratio', 'N/A'):.3f}")
                    print(f"    Status: {'✓ PASS' if di.get('ratio', 0) >= 0.8 else '✗ FAIL'} (threshold: 0.8)")
                
                if "statistical_parity" in metrics:
                    sp = metrics["statistical_parity"]
                    print(f"\n  Statistical Parity Difference:")
                    print(f"    Difference: {sp.get('difference', 'N/A'):.3f}")
                    print(f"    Status: {'✓ PASS' if abs(sp.get('difference', 1)) <= 0.1 else '✗ FAIL'} (threshold: ±0.1)")
                
                if "equal_opportunity" in metrics:
                    eo = metrics["equal_opportunity"]
                    print(f"\n  Equal Opportunity Difference:")
                    print(f"    Difference: {eo.get('difference', 'N/A'):.3f}")
                    print(f"    Status: {'✓ PASS' if abs(eo.get('difference', 1)) <= 0.1 else '✗ FAIL'} (threshold: ±0.1)")
                
                print()
            
            # Recommendations
            if "recommendations" in audit_results:
                recs = audit_results["recommendations"]
                print("RECOMMENDATIONS:")
                for i, rec in enumerate(recs, 1):
                    print(f"  {i}. {rec}")
                print()
            
            # Save report
            if "report" in audit_results:
                report_path = "data/demo_audit_report.md"
                with open(report_path, 'w') as f:
                    f.write(audit_results["report"])
                print(f"✓ Full report saved to: {report_path}")
                print()
            
            # Save JSON results
            json_path = "data/demo_audit_results.json"
            with open(json_path, 'w') as f:
                json.dump(audit_results, f, indent=2)
            print(f"✓ JSON results saved to: {json_path}")
            print()
            
            print("=" * 80)
            print("✓ Demo audit completed successfully!")
            print("=" * 80)
            
            return True
            
        else:
            print(f"✗ Audit failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error sending audit request: {e}")
        return False

if __name__ == "__main__":
    success = run_demo_audit()
    sys.exit(0 if success else 1)

# Made with Bob
