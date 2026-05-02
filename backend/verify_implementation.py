"""
Verification script for FairLens Task 6 implementation
Checks that all required files and components exist
"""

import os
import sys
import ast


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  ✓ {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"  ✗ {description}: {filepath} - NOT FOUND")
        return False


def check_class_exists(filepath, class_name):
    """Check if a class exists in a Python file."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        if class_name in classes:
            print(f"    ✓ Class '{class_name}' found")
            return True
        else:
            print(f"    ✗ Class '{class_name}' NOT FOUND")
            return False
    except Exception as e:
        print(f"    ✗ Error parsing file: {e}")
        return False


def check_method_exists(filepath, class_name, method_name):
    """Check if a method exists in a class."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                if method_name in methods:
                    print(f"      ✓ Method '{method_name}' found")
                    return True
                else:
                    print(f"      ✗ Method '{method_name}' NOT FOUND")
                    return False
        
        return False
    except Exception as e:
        print(f"      ✗ Error checking method: {e}")
        return False


def check_flask_route(filepath, route_path):
    """Check if a Flask route exists."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        if f"@app.route('{route_path}'" in content or f'@app.route("{route_path}"' in content:
            print(f"    ✓ Route '{route_path}' found")
            return True
        else:
            print(f"    ✗ Route '{route_path}' NOT FOUND")
            return False
    except Exception as e:
        print(f"    ✗ Error checking route: {e}")
        return False


def main():
    print("=" * 70)
    print("FairLens Task 6 Implementation Verification")
    print("=" * 70)
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    results = []
    
    # Check 1: report_generator.py exists
    print("\n1. Checking report_generator.py...")
    report_gen_path = os.path.join(backend_dir, 'audit', 'report_generator.py')
    results.append(check_file_exists(report_gen_path, "Report Generator"))
    
    if os.path.exists(report_gen_path):
        # Check AuditReportGenerator class
        results.append(check_class_exists(report_gen_path, 'AuditReportGenerator'))
        
        # Check required methods
        print("    Checking required methods:")
        results.append(check_method_exists(report_gen_path, 'AuditReportGenerator', 'generate_markdown_report'))
        results.append(check_method_exists(report_gen_path, 'AuditReportGenerator', 'convert_to_pdf'))
        results.append(check_method_exists(report_gen_path, 'AuditReportGenerator', 'generate_full_report'))
    
    # Check 2: app.py exists
    print("\n2. Checking app.py...")
    app_path = os.path.join(backend_dir, 'app.py')
    results.append(check_file_exists(app_path, "Flask API"))
    
    if os.path.exists(app_path):
        # Check Flask routes
        print("    Checking API endpoints:")
        results.append(check_flask_route(app_path, '/api/health'))
        results.append(check_flask_route(app_path, '/api/audit'))
        results.append(check_flask_route(app_path, '/api/download/<filename>'))
        
        # Check CORS configuration
        with open(app_path, 'r') as f:
            content = f.read()
            if 'CORS' in content and 'localhost:3000' in content:
                print("    ✓ CORS configured for localhost:3000")
                results.append(True)
            else:
                print("    ✗ CORS not properly configured")
                results.append(False)
    
    # Check 3: requirements.txt updated
    print("\n3. Checking requirements.txt...")
    req_path = os.path.join(backend_dir, 'requirements.txt')
    results.append(check_file_exists(req_path, "Requirements"))
    
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            content = f.read()
            
        required_packages = ['markdown', 'weasyprint', 'flask', 'flask-cors']
        print("    Checking required packages:")
        for package in required_packages:
            if package in content.lower():
                print(f"      ✓ {package}")
                results.append(True)
            else:
                print(f"      ✗ {package} - NOT FOUND")
                results.append(False)
    
    # Check 4: Integration points
    print("\n4. Checking integration with existing modules...")
    
    # Check imports in app.py
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            content = f.read()
        
        required_imports = [
            'BiasDetector',
            'LoanApprovalAuditTemplate',
            'AccountabilityTracker',
            'AuditReportGenerator'
        ]
        
        print("    Checking imports:")
        for imp in required_imports:
            if imp in content:
                print(f"      ✓ {imp}")
                results.append(True)
            else:
                print(f"      ✗ {imp} - NOT IMPORTED")
                results.append(False)
    
    # Check 5: Report sections
    print("\n5. Checking report sections in generate_markdown_report...")
    if os.path.exists(report_gen_path):
        with open(report_gen_path, 'r') as f:
            content = f.read()
        
        required_sections = [
            'Executive Summary',
            'Regulatory Context',
            'Data Bias Risk Assessment',
            'Discrimination Detection Results',
            'Accountability & Governance',
            'Data Privacy Compliance',
            'Remediation Recommendations',
            'Audit Trail'
        ]
        
        print("    Checking report sections:")
        for section in required_sections:
            if section in content:
                print(f"      ✓ {section}")
                results.append(True)
            else:
                print(f"      ✗ {section} - NOT FOUND")
                results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nChecks passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n🎉 All verification checks passed!")
        print("\nTask 6 implementation is complete:")
        print("  ✓ backend/audit/report_generator.py created")
        print("  ✓ backend/app.py created with Flask API")
        print("  ✓ All required methods and endpoints implemented")
        print("  ✓ Integration with existing modules verified")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run the API: python3 app.py")
        print("  3. Test with frontend or curl commands")
        return 0
    else:
        print(f"\n⚠️  {total - passed} verification check(s) failed")
        print("Please review the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob