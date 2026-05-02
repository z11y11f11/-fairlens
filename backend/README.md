# FairLens Backend API

Flask-based REST API for AI bias auditing and compliance reporting.

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the API Server

```bash
python3 app.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /api/health
```
Returns API status and version.

### Run Audit
```
POST /api/audit
Content-Type: application/json

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
```

Returns audit results with PDF and Markdown report URLs.

### Download Report
```
GET /api/download/<filename>
```
Download generated PDF or Markdown report.

### List Reports
```
GET /api/reports
```
List all available audit reports.

## Project Structure

```
backend/
├── app.py                      # Flask API server
├── requirements.txt            # Python dependencies
├── audit/
│   ├── bias_detector.py       # Core bias detection engine
│   ├── accountability.py      # RACI matrix and governance
│   └── report_generator.py    # Markdown/PDF report generation
├── templates/
│   └── loan_approval.py       # Loan approval audit template
└── reports/                   # Generated audit reports (created automatically)
```

## Testing

Run the test suite:
```bash
python3 test_api.py
```

## Components

### BiasDetector
- Analyzes disparate impact using 4/5 rule
- Detects proxy variables
- Checks for protected attribute usage
- Calculates composite risk scores

### LoanApprovalAuditTemplate
- Maps findings to regulatory requirements (ECOA, EU AI Act, GDPR)
- Assesses data bias, discrimination, accountability, and privacy
- Generates prioritized remediation recommendations

### AccountabilityTracker
- Builds RACI matrices for AI lifecycle activities
- Identifies accountability gaps
- Assesses governance maturity

### AuditReportGenerator
- Generates comprehensive Markdown reports
- Converts to professionally styled PDFs
- Includes all regulatory context and findings

## Regulatory Compliance

This system helps assess compliance with:
- **ECOA** (Equal Credit Opportunity Act)
- **EU AI Act** Article 9 (High-Risk AI Systems)
- **FCRA** (Fair Credit Reporting Act)
- **GDPR** Article 5 (Data Minimization)
- **Federal Reserve SR 11-7** (Model Risk Management)

## Made with Bob