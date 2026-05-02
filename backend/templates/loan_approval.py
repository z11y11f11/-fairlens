"""
Loan Approval Audit Template
Maps bias detection results to regulatory requirements for loan approval systems.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class LoanApprovalAuditTemplate:
    """
    Audit template for loan approval systems that assesses bias risks,
    discrimination, accountability, and privacy compliance.
    """
    
    # Regulatory thresholds
    DISPARATE_IMPACT_THRESHOLD_HIGH = 0.8  # 4/5 rule
    DISPARATE_IMPACT_THRESHOLD_MEDIUM = 0.9
    ACCOUNTABILITY_REVIEW_MONTHS = 12
    
    # Protected attributes under ECOA and EU AI Act
    ECOA_PROTECTED_ATTRIBUTES = ['gender', 'race', 'age', 'marital_status', 'national_origin']
    
    # Proxy variables that may indicate bias
    PROXY_VARIABLES = ['zip_code', 'zipcode', 'postal_code', 'occupation', 'neighborhood']
    
    # PII that should be minimized
    PII_FEATURES = ['name', 'ssn', 'social_security', 'address', 'phone', 'email']
    
    def __init__(self):
        """Initialize the loan approval audit template."""
        self.findings = []
        
    def assess_data_bias_risk(
        self, 
        features: List[str], 
        training_period: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Assess data bias risks in training data.
        
        Args:
            features: List of feature names used in the model
            training_period: Dict with 'start_date' and 'end_date' (YYYY-MM-DD format)
            
        Returns:
            List of risk items with level (HIGH/MEDIUM/LOW) and explanation
        """
        risk_items = []
        
        # Check for historical bias risk (data before 2020)
        if training_period:
            try:
                start_date = datetime.strptime(training_period.get('start_date', ''), '%Y-%m-%d')
                if start_date.year < 2020:
                    risk_items.append({
                        'risk_level': 'HIGH',
                        'category': 'Historical Bias',
                        'finding': 'Training data includes records from before 2020',
                        'explanation': (
                            f'Training data starts from {start_date.year}, which may contain '
                            'historical biases from discriminatory lending practices. '
                            'Pre-2020 data may not reflect current fair lending standards.'
                        ),
                        'regulation': 'ECOA Section 1002.6 - Prohibited Basis'
                    })
            except (ValueError, KeyError):
                risk_items.append({
                    'risk_level': 'MEDIUM',
                    'category': 'Data Quality',
                    'finding': 'Training period not properly specified',
                    'explanation': 'Unable to assess historical bias risk due to missing or invalid training period dates.',
                    'regulation': 'Model Risk Management SR 11-7'
                })
        
        # Check for proxy variables
        proxy_vars_found = [f for f in features if any(proxy in f.lower() for proxy in self.PROXY_VARIABLES)]
        if proxy_vars_found:
            risk_items.append({
                'risk_level': 'HIGH',
                'category': 'Proxy Variables',
                'finding': f'Proxy variables detected: {", ".join(proxy_vars_found)}',
                'explanation': (
                    'These variables may serve as proxies for protected characteristics '
                    '(e.g., zip code correlates with race/ethnicity). Using proxy variables '
                    'can result in indirect discrimination.'
                ),
                'regulation': 'ECOA Regulation B - Indirect Discrimination'
            })
        
        # Check for direct use of protected attributes
        protected_attrs_found = [f for f in features if any(attr in f.lower() for attr in self.ECOA_PROTECTED_ATTRIBUTES)]
        if protected_attrs_found:
            risk_items.append({
                'risk_level': 'HIGH',
                'category': 'Protected Attributes',
                'finding': f'Protected attributes used directly: {", ".join(protected_attrs_found)}',
                'explanation': (
                    'Direct use of protected characteristics in lending decisions '
                    'is prohibited under ECOA and may violate fair lending laws.'
                ),
                'regulation': 'ECOA 15 USC 1691(a) - Prohibited Basis'
            })
        
        # If no major risks found, add a low-risk item
        if not risk_items:
            risk_items.append({
                'risk_level': 'LOW',
                'category': 'Data Bias',
                'finding': 'No obvious proxy variables or protected attributes detected',
                'explanation': 'Initial feature review shows no direct use of prohibited characteristics.',
                'regulation': 'ECOA Compliance'
            })
        
        return risk_items
    
    def assess_discrimination_risk(
        self, 
        di_results: Dict[str, float], 
        feature_list: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Assess discrimination risk using disparate impact analysis.
        
        Args:
            di_results: Dict mapping protected groups to disparate impact ratios
            feature_list: List of features used in the model
            
        Returns:
            List of discrimination findings with risk levels
        """
        findings = []
        
        # Apply 4/5 rule to disparate impact results
        for group, di_ratio in di_results.items():
            if di_ratio < self.DISPARATE_IMPACT_THRESHOLD_HIGH:
                findings.append({
                    'risk_level': 'HIGH',
                    'category': 'Disparate Impact',
                    'finding': f'Disparate impact detected for {group}: {di_ratio:.3f}',
                    'explanation': (
                        f'The disparate impact ratio of {di_ratio:.3f} is below the 0.80 threshold '
                        '(4/5 rule), indicating potential adverse impact on this protected group. '
                        'This may constitute unlawful discrimination under ECOA.'
                    ),
                    'regulation': 'ECOA 4/5 Rule (Uniform Guidelines on Employee Selection Procedures)',
                    'metric_value': di_ratio,
                    'threshold': self.DISPARATE_IMPACT_THRESHOLD_HIGH
                })
            elif di_ratio < self.DISPARATE_IMPACT_THRESHOLD_MEDIUM:
                findings.append({
                    'risk_level': 'MEDIUM',
                    'category': 'Disparate Impact',
                    'finding': f'Borderline disparate impact for {group}: {di_ratio:.3f}',
                    'explanation': (
                        f'The disparate impact ratio of {di_ratio:.3f} is between 0.80 and 0.90, '
                        'indicating potential concern. While not automatically discriminatory, '
                        'this warrants further investigation and monitoring.'
                    ),
                    'regulation': 'ECOA Fair Lending Guidelines',
                    'metric_value': di_ratio,
                    'threshold': self.DISPARATE_IMPACT_THRESHOLD_MEDIUM
                })
            else:
                findings.append({
                    'risk_level': 'LOW',
                    'category': 'Disparate Impact',
                    'finding': f'Acceptable disparate impact for {group}: {di_ratio:.3f}',
                    'explanation': (
                        f'The disparate impact ratio of {di_ratio:.3f} is above 0.90, '
                        'indicating no significant adverse impact on this protected group.'
                    ),
                    'regulation': 'ECOA Compliance',
                    'metric_value': di_ratio,
                    'threshold': self.DISPARATE_IMPACT_THRESHOLD_MEDIUM
                })
        
        # Check ECOA violations (direct use of protected characteristics)
        ecoa_violations = [f for f in feature_list if any(attr in f.lower() for attr in self.ECOA_PROTECTED_ATTRIBUTES)]
        if ecoa_violations:
            findings.append({
                'risk_level': 'HIGH',
                'category': 'ECOA Violation',
                'finding': f'Direct use of protected characteristics: {", ".join(ecoa_violations)}',
                'explanation': (
                    'The model directly uses protected characteristics prohibited under ECOA. '
                    'This constitutes a clear violation of fair lending laws and must be remediated immediately.'
                ),
                'regulation': 'ECOA 15 USC 1691(a)(1) - Discrimination Prohibited'
            })
        
        # Check EU AI Act Article 9 compliance (high-risk AI system)
        findings.append({
            'risk_level': 'MEDIUM',
            'category': 'EU AI Act Compliance',
            'finding': 'Loan approval system classified as high-risk under EU AI Act',
            'explanation': (
                'Credit scoring and loan approval systems are classified as high-risk AI systems '
                'under EU AI Act Article 9. This requires: (1) risk management system, '
                '(2) data governance, (3) technical documentation, (4) transparency, '
                '(5) human oversight, (6) accuracy and robustness measures.'
            ),
            'regulation': 'EU AI Act Article 9 - High-Risk AI Systems'
        })
        
        return findings
    
    def assess_accountability_gaps(
        self, 
        raci_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Assess accountability and governance gaps.
        
        Args:
            raci_data: Dict containing RACI matrix and governance information
                Expected keys: 'responsible', 'accountable', 'consulted', 'informed',
                'last_review_date', 'complaint_handler'
                
        Returns:
            List of accountability findings
        """
        findings = []
        
        # Required RACI roles
        required_roles = ['responsible', 'accountable', 'consulted', 'informed']
        
        # Check if all RACI roles are filled
        missing_roles = [role for role in required_roles if not raci_data.get(role)]
        if missing_roles:
            findings.append({
                'risk_level': 'MEDIUM',
                'category': 'Governance Gap',
                'finding': f'Missing RACI roles: {", ".join(missing_roles)}',
                'explanation': (
                    'Incomplete RACI matrix indicates unclear accountability for model decisions. '
                    'All roles (Responsible, Accountable, Consulted, Informed) must be clearly '
                    'defined to ensure proper governance and oversight.'
                ),
                'regulation': 'Model Risk Management SR 11-7 - Governance'
            })
        
        # Check if last review date is within 12 months
        last_review = raci_data.get('last_review_date')
        if last_review:
            try:
                review_date = datetime.strptime(last_review, '%Y-%m-%d')
                months_since_review = (datetime.now() - review_date).days / 30.44
                
                if months_since_review > self.ACCOUNTABILITY_REVIEW_MONTHS:
                    findings.append({
                        'risk_level': 'MEDIUM',
                        'category': 'Model Review',
                        'finding': f'Model not reviewed in {int(months_since_review)} months',
                        'explanation': (
                            f'Last model review was on {last_review}, which exceeds the 12-month '
                            'requirement. Regular model validation is required to ensure continued '
                            'accuracy and fairness.'
                        ),
                        'regulation': 'Model Risk Management SR 11-7 - Ongoing Monitoring'
                    })
                else:
                    findings.append({
                        'risk_level': 'LOW',
                        'category': 'Model Review',
                        'finding': f'Model reviewed {int(months_since_review)} months ago',
                        'explanation': 'Model review is current and within the 12-month requirement.',
                        'regulation': 'Model Risk Management SR 11-7 - Compliance'
                    })
            except (ValueError, TypeError):
                findings.append({
                    'risk_level': 'MEDIUM',
                    'category': 'Model Review',
                    'finding': 'Invalid or missing last review date',
                    'explanation': 'Unable to verify model review currency due to invalid date format.',
                    'regulation': 'Model Risk Management SR 11-7'
                })
        else:
            findings.append({
                'risk_level': 'MEDIUM',
                'category': 'Model Review',
                'finding': 'No model review date recorded',
                'explanation': 'Missing review date prevents verification of ongoing model validation.',
                'regulation': 'Model Risk Management SR 11-7'
            })
        
        # Check if complaint handler exists
        if not raci_data.get('complaint_handler'):
            findings.append({
                'risk_level': 'MEDIUM',
                'category': 'Consumer Protection',
                'finding': 'No complaint handler designated',
                'explanation': (
                    'A designated complaint handler is required to address consumer disputes '
                    'and adverse action inquiries. This is essential for ECOA compliance and '
                    'consumer protection.'
                ),
                'regulation': 'ECOA Section 1002.9 - Notifications'
            })
        else:
            findings.append({
                'risk_level': 'LOW',
                'category': 'Consumer Protection',
                'finding': f'Complaint handler designated: {raci_data.get("complaint_handler")}',
                'explanation': 'Proper complaint handling mechanism is in place.',
                'regulation': 'ECOA Compliance'
            })
        
        return findings
    
    def assess_privacy_compliance(
        self, 
        feature_list: List[str], 
        data_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Assess privacy and data protection compliance.
        
        Args:
            feature_list: List of features used in the model
            data_source: Description of data source (optional)
            
        Returns:
            List of privacy compliance findings
        """
        findings = []
        
        # Check for PII in features
        pii_found = [f for f in feature_list if any(pii in f.lower() for pii in self.PII_FEATURES)]
        if pii_found:
            findings.append({
                'risk_level': 'HIGH',
                'category': 'PII Exposure',
                'finding': f'PII detected in features: {", ".join(pii_found)}',
                'explanation': (
                    'Direct use of personally identifiable information (PII) in model features '
                    'violates data minimization principles and increases privacy risks. '
                    'PII should be anonymized or removed unless strictly necessary.'
                ),
                'regulation': 'GDPR Article 5(1)(c) - Data Minimization'
            })
        
        # Check if data source is authorized
        if data_source:
            if 'unauthorized' in data_source.lower() or 'unknown' in data_source.lower():
                findings.append({
                    'risk_level': 'HIGH',
                    'category': 'Data Source',
                    'finding': 'Unauthorized or unknown data source',
                    'explanation': (
                        'Data source authorization cannot be verified. All data used for '
                        'credit decisions must come from authorized sources with proper '
                        'consumer consent.'
                    ),
                    'regulation': 'FCRA Section 604 - Permissible Purposes'
                })
            else:
                findings.append({
                    'risk_level': 'LOW',
                    'category': 'Data Source',
                    'finding': f'Data source documented: {data_source}',
                    'explanation': 'Data source is documented and appears authorized.',
                    'regulation': 'FCRA Compliance'
                })
        else:
            findings.append({
                'risk_level': 'MEDIUM',
                'category': 'Data Source',
                'finding': 'Data source not specified',
                'explanation': 'Data source should be documented for audit trail and compliance verification.',
                'regulation': 'FCRA Section 607 - Compliance Procedures'
            })
        
        # Check GDPR data minimization principle
        if len(feature_list) > 50:
            findings.append({
                'risk_level': 'MEDIUM',
                'category': 'Data Minimization',
                'finding': f'Large number of features: {len(feature_list)}',
                'explanation': (
                    f'The model uses {len(feature_list)} features, which may violate data '
                    'minimization principles. Consider feature selection to use only data '
                    'adequate, relevant, and limited to what is necessary.'
                ),
                'regulation': 'GDPR Article 5(1)(c) - Data Minimization'
            })
        else:
            findings.append({
                'risk_level': 'LOW',
                'category': 'Data Minimization',
                'finding': f'Reasonable feature count: {len(feature_list)}',
                'explanation': 'Feature count appears reasonable and aligned with data minimization principles.',
                'regulation': 'GDPR Compliance'
            })
        
        return findings
    
    def generate_remediation_recommendations(
        self, 
        all_findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate prioritized remediation recommendations based on findings.
        
        Args:
            all_findings: Combined list of all findings from assessments
            
        Returns:
            Prioritized list of remediation recommendations
        """
        recommendations = []
        
        # Separate findings by risk level
        high_risks = [f for f in all_findings if f.get('risk_level') == 'HIGH']
        medium_risks = [f for f in all_findings if f.get('risk_level') == 'MEDIUM']
        low_risks = [f for f in all_findings if f.get('risk_level') == 'LOW']
        
        # HIGH risk findings → urgent action required
        for finding in high_risks:
            recommendations.append({
                'priority': 'URGENT',
                'timeline': 'Immediate action required',
                'finding_category': finding.get('category'),
                'finding': finding.get('finding'),
                'recommendation': self._get_remediation_action(finding),
                'regulation': finding.get('regulation'),
                'risk_level': 'HIGH'
            })
        
        # MEDIUM risk findings → recommended within 90 days
        for finding in medium_risks:
            recommendations.append({
                'priority': 'HIGH',
                'timeline': 'Remediate within 90 days',
                'finding_category': finding.get('category'),
                'finding': finding.get('finding'),
                'recommendation': self._get_remediation_action(finding),
                'regulation': finding.get('regulation'),
                'risk_level': 'MEDIUM'
            })
        
        # LOW risk findings → monitor quarterly
        for finding in low_risks:
            recommendations.append({
                'priority': 'LOW',
                'timeline': 'Monitor quarterly',
                'finding_category': finding.get('category'),
                'finding': finding.get('finding'),
                'recommendation': 'Continue monitoring and maintain current controls',
                'regulation': finding.get('regulation'),
                'risk_level': 'LOW'
            })
        
        return recommendations
    
    def _get_remediation_action(self, finding: Dict[str, Any]) -> str:
        """
        Get specific remediation action based on finding category.
        
        Args:
            finding: Finding dictionary
            
        Returns:
            Specific remediation recommendation
        """
        category = finding.get('category', '').lower()
        
        remediation_map = {
            'disparate impact': (
                'Investigate root cause of disparate impact. Consider: '
                '(1) Retraining model with balanced data, '
                '(2) Adjusting decision thresholds, '
                '(3) Implementing fairness constraints, '
                '(4) Removing or transforming biased features.'
            ),
            'ecoa violation': (
                'Immediately remove protected characteristics from model features. '
                'Retrain model without prohibited variables and validate compliance.'
            ),
            'proxy variables': (
                'Remove or transform proxy variables that correlate with protected characteristics. '
                'Consider using fairness-aware feature engineering techniques.'
            ),
            'protected attributes': (
                'Remove protected attributes from model inputs immediately. '
                'Conduct impact analysis and retrain model.'
            ),
            'historical bias': (
                'Update training data to include recent records (post-2020). '
                'Consider temporal reweighting or using only recent data for training.'
            ),
            'pii exposure': (
                'Remove PII from model features. Implement data anonymization or '
                'pseudonymization techniques. Use derived features instead of raw PII.'
            ),
            'governance gap': (
                'Complete RACI matrix with designated individuals for all roles. '
                'Document responsibilities and establish clear escalation procedures.'
            ),
            'model review': (
                'Conduct comprehensive model validation including: '
                '(1) Performance metrics, (2) Fairness assessment, '
                '(3) Feature importance analysis, (4) Documentation update.'
            ),
            'consumer protection': (
                'Designate a complaint handler and establish procedures for: '
                '(1) Receiving complaints, (2) Investigating disputes, '
                '(3) Providing adverse action notices, (4) Maintaining records.'
            ),
            'data source': (
                'Document data sources and verify authorization. '
                'Ensure proper consumer consent and FCRA compliance.'
            ),
            'data minimization': (
                'Conduct feature selection analysis to reduce feature count. '
                'Remove redundant or unnecessary features while maintaining model performance.'
            )
        }
        
        for key, action in remediation_map.items():
            if key in category:
                return action
        
        return 'Conduct detailed investigation and implement appropriate controls.'
    
    def run_full_template(
        self, 
        audit_input: Dict[str, Any], 
        di_results: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Orchestrate all assessments and return complete findings.
        
        Args:
            audit_input: Dict containing:
                - features: List of feature names
                - training_period: Dict with start_date and end_date
                - raci_data: RACI matrix and governance info
                - data_source: Data source description
            di_results: Disparate impact results from bias detector
            
        Returns:
            Complete structured findings dictionary
        """
        # Extract inputs
        features = audit_input.get('features', [])
        training_period = audit_input.get('training_period')
        raci_data = audit_input.get('raci_data', {})
        data_source = audit_input.get('data_source')
        
        # Run all assessments
        data_bias_findings = self.assess_data_bias_risk(features, training_period)
        discrimination_findings = self.assess_discrimination_risk(di_results, features)
        accountability_findings = self.assess_accountability_gaps(raci_data)
        privacy_findings = self.assess_privacy_compliance(features, data_source)
        
        # Combine all findings
        all_findings = (
            data_bias_findings + 
            discrimination_findings + 
            accountability_findings + 
            privacy_findings
        )
        
        # Generate recommendations
        recommendations = self.generate_remediation_recommendations(all_findings)
        
        # Calculate summary statistics
        risk_summary = {
            'high_risk_count': len([f for f in all_findings if f.get('risk_level') == 'HIGH']),
            'medium_risk_count': len([f for f in all_findings if f.get('risk_level') == 'MEDIUM']),
            'low_risk_count': len([f for f in all_findings if f.get('risk_level') == 'LOW']),
            'total_findings': len(all_findings)
        }
        
        # Determine overall risk level
        if risk_summary['high_risk_count'] > 0:
            overall_risk = 'HIGH'
        elif risk_summary['medium_risk_count'] > 2:
            overall_risk = 'MEDIUM'
        else:
            overall_risk = 'LOW'
        
        # Return structured findings
        return {
            'audit_timestamp': datetime.now().isoformat(),
            'overall_risk_level': overall_risk,
            'risk_summary': risk_summary,
            'findings': {
                'data_bias': data_bias_findings,
                'discrimination': discrimination_findings,
                'accountability': accountability_findings,
                'privacy': privacy_findings
            },
            'recommendations': recommendations,
            'regulatory_references': self._get_regulatory_references(),
            'next_review_date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        }
    
    def _get_regulatory_references(self) -> Dict[str, str]:
        """
        Get relevant regulatory references.
        
        Returns:
            Dict of regulation names and descriptions
        """
        return {
            'ECOA': 'Equal Credit Opportunity Act (15 USC 1691) - Prohibits discrimination in credit decisions',
            'FCRA': 'Fair Credit Reporting Act (15 USC 1681) - Regulates consumer credit information',
            'GDPR': 'General Data Protection Regulation (EU 2016/679) - Data protection and privacy',
            'EU_AI_Act': 'EU Artificial Intelligence Act - Regulation of high-risk AI systems',
            'SR_11-7': 'Federal Reserve SR 11-7 - Guidance on Model Risk Management',
            'Regulation_B': 'ECOA Regulation B (12 CFR 1002) - Equal Credit Opportunity',
            '4/5_Rule': 'Uniform Guidelines on Employee Selection Procedures - Disparate impact threshold'
        }

# Made with Bob
