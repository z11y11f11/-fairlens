"""
FairLens Flask API
REST API for AI bias auditing and report generation
"""

import os
import sys
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import traceback

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit.bias_detector import BiasDetector
from templates.loan_approval import LoanApprovalAuditTemplate
from audit.accountability import AccountabilityTracker
from audit.report_generator import AuditReportGenerator

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend (localhost:3000)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Create reports directory
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# Initialize components
bias_detector = BiasDetector()
audit_template = LoanApprovalAuditTemplate()
accountability_tracker = AccountabilityTracker()
report_generator = AuditReportGenerator()


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON with status and version
    """
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'service': 'FairLens AI Bias Audit API'
    })


@app.route('/api/audit', methods=['POST'])
def run_audit():
    """
    Run complete AI bias audit.
    
    Expected JSON payload:
    {
        "model_info": {
            "name": "Loan Approval Model",
            "version": "1.0.0",
            "description": "AI model for loan approval decisions"
        },
        "features": ["age", "income", "credit_score", ...],
        "data_info": {
            "data_path": "path/to/dataset.csv",
            "protected_attribute": "sex",
            "privileged_group": [1],
            "label_name": "income",
            "favorable_label": 1,
            "training_period": {
                "start_date": "2020-01-01",
                "end_date": "2023-12-31"
            },
            "data_source": "Internal customer database"
        },
        "raci_data": {
            "model_developer": "Alice Johnson",
            "approval_authority": "Bob Smith",
            "monitor_owner": "Carol White",
            "complaint_handler": "David Brown",
            "model_version": "1.0.0",
            "last_review_date": "2023-06-15"
        }
    }
    
    Returns:
        JSON with audit results and file paths
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400
        
        # Extract required fields
        model_info = data.get('model_info', {})
        features = data.get('features', [])
        data_info = data.get('data_info', {})
        raci_data = data.get('raci_data', {})
        
        # Validate required fields
        if not features:
            return jsonify({
                'error': 'Features list is required',
                'status': 'error'
            }), 400
        
        if not data_info.get('data_path'):
            return jsonify({
                'error': 'data_path is required in data_info',
                'status': 'error'
            }), 400
        
        print(f"[{datetime.now().isoformat()}] Starting audit for model: {model_info.get('name', 'Unknown')}")
        
        # Step 1: Run BiasDetector analysis
        print("Step 1: Running bias detection analysis...")
        audit_input = {
            'data_path': data_info.get('data_path'),
            'protected_attribute': data_info.get('protected_attribute', 'sex'),
            'privileged_group': data_info.get('privileged_group', [1]),
            'feature_list': features,
            'label_name': data_info.get('label_name', 'income'),
            'favorable_label': data_info.get('favorable_label', 1),
            'data_quality_score': data_info.get('data_quality_score', 0.8),
            'privacy_score': data_info.get('privacy_score', 0.9)
        }
        
        audit_results = bias_detector.run_full_analysis(audit_input)
        
        # Step 2: Run LoanApprovalAuditTemplate
        print("Step 2: Running regulatory compliance template...")
        
        # Extract DI results for template
        di_ratio = audit_results.get('disparate_impact_analysis', {}).get('disparate_impact')
        di_results = {
            data_info.get('protected_attribute', 'sex'): di_ratio if di_ratio is not None else 1.0
        }
        
        template_input = {
            'features': features,
            'training_period': data_info.get('training_period'),
            'raci_data': raci_data,
            'data_source': data_info.get('data_source')
        }
        
        template_findings = audit_template.run_full_template(template_input, di_results)
        
        # Step 3: Run AccountabilityTracker
        print("Step 3: Running accountability assessment...")
        
        # Add model version to RACI data if not present
        if 'model_version' not in raci_data:
            raci_data['model_version'] = model_info.get('version', '1.0.0')
        
        accountability_report = accountability_tracker.run_full_accountability(raci_data)
        
        # Step 4: Generate reports (Markdown + PDF)
        print("Step 4: Generating audit reports...")
        
        all_data = {
            'audit_results': audit_results,
            'template_findings': template_findings,
            'accountability_report': accountability_report
        }
        
        report_files = report_generator.generate_full_report(all_data, REPORTS_DIR)
        
        # Step 5: Prepare response
        print("Step 5: Preparing response...")
        
        audit_id = accountability_report['audit_trail']['audit_id']
        composite_score = audit_results.get('composite_risk_score', {})
        
        # Build risk summary
        risk_summary = {
            'overall_risk_level': composite_score.get('risk_level', 'UNKNOWN'),
            'composite_score': composite_score.get('composite_score', 0),
            'disparate_impact_ratio': audit_results.get('disparate_impact_analysis', {}).get('disparate_impact'),
            'proxy_variables_count': audit_results.get('proxy_variable_analysis', {}).get('count', 0),
            'direct_violations': audit_results.get('protected_attributes_check', {}).get('violation_count', 0),
            'high_risk_findings': template_findings.get('risk_summary', {}).get('high_risk_count', 0),
            'medium_risk_findings': template_findings.get('risk_summary', {}).get('medium_risk_count', 0),
            'governance_maturity': accountability_report.get('governance_maturity', {}).get('level_name', 'Unknown')
        }
        
        response = {
            'status': 'success',
            'audit_id': audit_id,
            'timestamp': datetime.now().isoformat(),
            'model_info': model_info,
            'risk_summary': risk_summary,
            'files': {
                'pdf_url': f'/api/download/{report_files["pdf_filename"]}',
                'markdown_url': f'/api/download/{report_files["markdown_filename"]}',
                'pdf_filename': report_files['pdf_filename'],
                'markdown_filename': report_files['markdown_filename']
            },
            'key_findings': audit_results.get('summary', {}).get('key_findings', []),
            'priority_actions': audit_results.get('summary', {}).get('priority_actions', [])
        }
        
        print(f"[{datetime.now().isoformat()}] Audit completed successfully: {audit_id}")
        
        return jsonify(response), 200
        
    except FileNotFoundError as e:
        error_msg = f"Data file not found: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'error': error_msg,
            'status': 'error',
            'type': 'file_not_found'
        }), 404
        
    except ValueError as e:
        error_msg = f"Invalid input data: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'error': error_msg,
            'status': 'error',
            'type': 'validation_error'
        }), 400
        
    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'error': error_msg,
            'status': 'error',
            'type': 'internal_error',
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/audit/manual', methods=['POST'])
def run_manual_audit():
    """
    Run audit with manual input data (no CSV file required).
    
    Expected JSON payload:
    {
        "gender": {
            "male_total": 100,
            "male_approved": 70,
            "female_total": 100,
            "female_approved": 50
        },
        "ethnic_groups": [
            {"name": "Group A", "total": 50, "approved": 30},
            {"name": "Group B", "total": 50, "approved": 25}
        ],
        "zip_codes": [
            {"name": "12345", "total": 60, "approved": 40},
            {"name": "67890", "total": 40, "approved": 20}
        ]
    }
    
    Returns:
        JSON with audit results and PDF download URL
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400
        
        # Extract manual input data
        gender_data = data.get('gender', {})
        ethnic_groups = data.get('ethnic_groups', [])
        zip_codes = data.get('zip_codes', [])
        
        # Validate gender data
        if not all(k in gender_data for k in ['male_total', 'male_approved', 'female_total', 'female_approved']):
            return jsonify({
                'error': 'Gender data must include male_total, male_approved, female_total, female_approved',
                'status': 'error'
            }), 400
        
        print(f"[{datetime.now().isoformat()}] Starting manual audit")
        
        # Calculate Disparate Impact for gender
        male_total = float(gender_data['male_total'])
        male_approved = float(gender_data['male_approved'])
        female_total = float(gender_data['female_total'])
        female_approved = float(gender_data['female_approved'])
        
        if male_total == 0 or female_total == 0:
            return jsonify({
                'error': 'Total counts cannot be zero',
                'status': 'error'
            }), 400
        
        male_rate = male_approved / male_total
        female_rate = female_approved / female_total
        
        # BUG FIX: Always calculate DI = lower_rate / higher_rate (must be 0-1.0)
        lower_rate = min(male_rate, female_rate)
        higher_rate = max(male_rate, female_rate)
        
        if higher_rate == 0:
            return jsonify({
                'error': 'Approval rates cannot be zero (division by zero)',
                'status': 'error'
            }), 400
        
        di_ratio = lower_rate / higher_rate
        
        # Determine risk level
        if di_ratio < 0.8:
            risk_level = "HIGH RISK 🔴"
            interpretation = (
                f"DISCRIMINATION DETECTED: Disparate Impact ratio of {di_ratio:.3f} "
                f"is below the 0.8 threshold (4/5 rule). Female approval rate: {female_rate:.1%}, "
                f"Male approval rate: {male_rate:.1%}"
            )
        elif di_ratio < 1.0:
            risk_level = "MEDIUM RISK 🟡"
            interpretation = (
                f"POTENTIAL BIAS: Disparate Impact ratio of {di_ratio:.3f} meets the 4/5 rule "
                f"but shows disparity. Monitor closely."
            )
        else:
            risk_level = "LOW RISK 🟢"
            interpretation = f"FAIR: Disparate Impact ratio of {di_ratio:.3f} indicates no adverse impact."
        
        # Build audit results structure
        audit_results = {
            'disparate_impact_analysis': {
                'disparate_impact': di_ratio,
                'statistical_parity_difference': female_rate - male_rate,
                'equal_opportunity_difference': female_rate - male_rate,
                'risk_level': risk_level,
                'interpretation': interpretation,
                'metrics_detail': {
                    'privileged_group': ['Male'],
                    'unprivileged_group': ['Female'],
                    'privileged_selection_rate': male_rate,
                    'unprivileged_selection_rate': female_rate,
                    'total_samples': int(male_total + female_total),
                    'privileged_samples': int(male_total),
                    'unprivileged_samples': int(female_total)
                }
            },
            'proxy_variable_analysis': {
                'detected_proxies': [],
                'count': 0,
                'risk_level': 'LOW RISK 🟢',
                'risk_explanation': 'Manual input - no proxy variables',
                'explanations': {},
                'recommendations': []
            },
            'protected_attributes_check': {
                'violations': [],
                'violation_count': 0,
                'risk_level': 'COMPLIANT ✅',
                'legal_implications': ['No direct use of protected attributes'],
                'required_actions': ['Continue monitoring']
            },
            'composite_risk_score': {
                'composite_score': 80 if di_ratio >= 0.8 else di_ratio * 100,
                'risk_level': risk_level,
                'component_scores': {
                    'disparate_impact_score': 80 if di_ratio >= 0.8 else di_ratio * 100,
                    'proxy_variable_score': 100,
                    'data_quality_score': 80,
                    'privacy_score': 90
                },
                'recommendations': []
            },
            'summary': {
                'overall_risk_level': risk_level,
                'composite_score': 80 if di_ratio >= 0.8 else di_ratio * 100,
                'disparate_impact_ratio': di_ratio,
                'key_findings': [interpretation],
                'priority_actions': []
            }
        }
        
        # Create minimal template findings
        template_findings = {
            'findings': {
                'data_bias': [],
                'discrimination': [],
                'accountability': [],
                'privacy': []
            },
            'recommendations': [],
            'risk_summary': {
                'high_risk_count': 1 if di_ratio < 0.8 else 0,
                'medium_risk_count': 1 if 0.8 <= di_ratio < 1.0 else 0
            },
            'next_review_date': (datetime.now().replace(month=datetime.now().month + 3) if datetime.now().month <= 9
                                else datetime.now().replace(year=datetime.now().year + 1, month=(datetime.now().month + 3) % 12)).strftime('%Y-%m-%d')
        }
        
        # Create accountability report
        audit_id = f"FL-{datetime.now().year}-{datetime.now().microsecond:04d}"
        accountability_report = {
            'audit_trail': {
                'audit_id': audit_id,
                'timestamp': datetime.now().isoformat(),
                'submitter': 'Manual Input User',
                'model_version': '1.0.0'
            },
            'governance_maturity': {
                'maturity_level': 2,
                'level_name': 'Defined',
                'score': 60,
                'risk': 'MEDIUM'
            },
            'raci_matrix': {
                'matrix': {}
            },
            'accountability_gaps': []
        }
        
        # Generate reports
        print("Generating audit reports...")
        all_data = {
            'audit_results': audit_results,
            'template_findings': template_findings,
            'accountability_report': accountability_report
        }
        
        report_files = report_generator.generate_full_report(all_data, REPORTS_DIR)
        
        # Prepare response
        response = {
            'status': 'success',
            'audit_id': audit_id,
            'timestamp': datetime.now().isoformat(),
            'risk_summary': {
                'overall_risk_level': risk_level,
                'composite_score': audit_results['composite_risk_score']['composite_score'],
                'disparate_impact_ratio': di_ratio,
                'gender_analysis': {
                    'male_rate': f"{male_rate:.1%}",
                    'female_rate': f"{female_rate:.1%}",
                    'di_ratio': f"{di_ratio:.3f}"
                }
            },
            'files': {
                'pdf_url': f'/api/download/{report_files["pdf_filename"]}',
                'markdown_url': f'/api/download/{report_files["markdown_filename"]}',
                'pdf_filename': report_files['pdf_filename'],
                'markdown_filename': report_files['markdown_filename']
            },
            'interpretation': interpretation
        }
        
        print(f"[{datetime.now().isoformat()}] Manual audit completed: {audit_id}")
        
        return jsonify(response), 200
        
    except ValueError as e:
        error_msg = f"Invalid input data: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'error': error_msg,
            'status': 'error',
            'type': 'validation_error'
        }), 400
        
    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'error': error_msg,
            'status': 'error',
            'type': 'internal_error',
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Download generated audit report files.
    
    Args:
        filename: Name of the file to download (PDF or Markdown)
    
    Returns:
        File download response
    """
    try:
        # Security: Only allow files from reports directory
        file_path = os.path.join(REPORTS_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({
                'error': f'File not found: {filename}',
                'status': 'error'
            }), 404
        
        # Security: Ensure file is within reports directory (prevent path traversal)
        if not os.path.abspath(file_path).startswith(os.path.abspath(REPORTS_DIR)):
            return jsonify({
                'error': 'Invalid file path',
                'status': 'error'
            }), 403
        
        # Determine mimetype
        if filename.endswith('.pdf'):
            mimetype = 'application/pdf'
        elif filename.endswith('.md'):
            mimetype = 'text/markdown'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"[ERROR] Download failed: {str(e)}")
        return jsonify({
            'error': f'Download failed: {str(e)}',
            'status': 'error'
        }), 500


@app.route('/api/reports', methods=['GET'])
def list_reports():
    """
    List all available audit reports.
    
    Returns:
        JSON with list of available reports
    """
    try:
        reports = []
        
        if os.path.exists(REPORTS_DIR):
            for filename in os.listdir(REPORTS_DIR):
                if filename.endswith(('.pdf', '.md')):
                    file_path = os.path.join(REPORTS_DIR, filename)
                    file_stat = os.stat(file_path)
                    
                    reports.append({
                        'filename': filename,
                        'size': file_stat.st_size,
                        'created': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        'download_url': f'/api/download/{filename}'
                    })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'count': len(reports),
            'reports': reports
        })
        
    except Exception as e:
        print(f"[ERROR] List reports failed: {str(e)}")
        return jsonify({
            'error': f'Failed to list reports: {str(e)}',
            'status': 'error'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500


if __name__ == '__main__':
    # Use port from environment or default to 5001 (5000 often used by AirPlay on macOS)
    port = int(os.environ.get('PORT', 5001))
    
    print("=" * 60)
    print("FairLens AI Bias Audit API")
    print("=" * 60)
    print(f"Reports directory: {REPORTS_DIR}")
    print(f"Starting server on http://localhost:{port}")
    print("Available endpoints:")
    print("  GET  /api/health          - Health check")
    print("  POST /api/audit           - Run bias audit")
    print("  GET  /api/download/<file> - Download report")
    print("  GET  /api/reports         - List all reports")
    print("=" * 60)
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )

# Made with Bob