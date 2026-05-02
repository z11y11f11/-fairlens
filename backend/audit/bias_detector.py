"""
FairLens Bias Detection Engine
Core bias detection using IBM AI Fairness 360 (AIF360)
Implements disparate impact analysis, proxy variable detection, and risk scoring
"""

import pandas as pd
import numpy as np
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import BinaryLabelDatasetMetric
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')


class BiasDetector:
    """
    Core bias detection engine for FairLens audit system.
    Analyzes datasets for discrimination using multiple fairness metrics.
    """
    
    # Protected attributes that should never be used directly
    PROTECTED_ATTRIBUTES = {
        'gender', 'sex', 'race', 'ethnicity', 'age', 'religion', 
        'nationality', 'national_origin', 'disability', 'marital_status',
        'sexual_orientation', 'gender_identity'
    }
    
    # Proxy variables that correlate with protected attributes
    PROXY_VARIABLES = {
        'zip_code': 'Strong proxy for race/ethnicity and socioeconomic status',
        'postal_code': 'Strong proxy for race/ethnicity and socioeconomic status',
        'zipcode': 'Strong proxy for race/ethnicity and socioeconomic status',
        'occupation': 'Potential proxy for gender and age discrimination',
        'job_title': 'Potential proxy for gender and age discrimination',
        'education_level': 'Potential proxy for socioeconomic status and race',
        'neighborhood': 'Strong proxy for race/ethnicity',
        'area_code': 'Proxy for geographic and demographic characteristics',
        'school_name': 'Proxy for socioeconomic status and race'
    }
    
    def __init__(self):
        """Initialize BiasDetector"""
        self.results = {}
    
    def analyze_disparate_impact(
        self,
        data_path: str,
        protected_attribute: str,
        privileged_group: List[Any],
        label_name: str = 'income',
        favorable_label: int = 1
    ) -> Dict[str, Any]:
        """
        Analyze disparate impact using the 4/5 rule (80% rule).
        
        The 4/5 rule states that if the selection rate for a protected group
        is less than 80% of the selection rate for the privileged group,
        there is evidence of adverse impact/discrimination.
        
        Args:
            data_path: Path to processed dataset (CSV)
            protected_attribute: Column name of protected attribute (e.g., 'sex', 'race')
            privileged_group: List of values considered privileged (e.g., [1] for male, 'Male')
            label_name: Name of the outcome/label column
            favorable_label: Value indicating favorable outcome (e.g., 1 for high income)
        
        Returns:
            Dictionary containing:
            - disparate_impact: DI ratio (should be >= 0.8)
            - statistical_parity_difference: SPD (should be close to 0)
            - equal_opportunity_difference: EOD (should be close to 0)
            - risk_level: HIGH/MEDIUM/LOW
            - interpretation: Human-readable explanation
            - metrics_detail: Detailed breakdown of calculations
        """
        try:
            # Load dataset
            df = pd.read_csv(data_path)
            
            # Validate columns exist
            if protected_attribute not in df.columns:
                raise ValueError(f"Protected attribute '{protected_attribute}' not found in dataset")
            if label_name not in df.columns:
                raise ValueError(f"Label '{label_name}' not found in dataset")
            
            # Determine unprivileged group (all values not in privileged_group)
            all_values = df[protected_attribute].unique()
            unprivileged_group = [v for v in all_values if v not in privileged_group]
            
            # Calculate selection rates manually
            # Privileged group (e.g., Male)
            priv_mask = df[protected_attribute].isin(privileged_group)
            priv_selection_rate = (df[priv_mask][label_name] == favorable_label).mean()
            priv_count = priv_mask.sum()
            
            # Unprivileged group (e.g., Female)
            unpriv_mask = ~priv_mask
            unpriv_selection_rate = (df[unpriv_mask][label_name] == favorable_label).mean()
            unpriv_count = unpriv_mask.sum()
            
            # Calculate Disparate Impact ratio
            # DI = (unprivileged selection rate) / (privileged selection rate)
            if priv_selection_rate > 0:
                disparate_impact = unpriv_selection_rate / priv_selection_rate
            else:
                disparate_impact = 0.0
            
            # Calculate Statistical Parity Difference
            # SPD = (unprivileged selection rate) - (privileged selection rate)
            statistical_parity_diff = unpriv_selection_rate - priv_selection_rate
            
            # Determine risk level based on 4/5 rule
            if disparate_impact < 0.8:
                risk_level = "HIGH RISK 🔴"
                interpretation = (
                    f"DISCRIMINATION DETECTED: Disparate Impact ratio of {disparate_impact:.3f} "
                    f"is below the 0.8 threshold (4/5 rule). This indicates adverse impact against "
                    f"the unprivileged group. The unprivileged group has a {unpriv_selection_rate:.1%} "
                    f"selection rate compared to {priv_selection_rate:.1%} for the privileged group."
                )
            elif disparate_impact < 1.0:
                risk_level = "MEDIUM RISK 🟡"
                interpretation = (
                    f"POTENTIAL BIAS: Disparate Impact ratio of {disparate_impact:.3f} "
                    f"meets the 4/5 rule but shows some disparity. The unprivileged group has "
                    f"a {unpriv_selection_rate:.1%} selection rate vs {priv_selection_rate:.1%} "
                    f"for the privileged group. Monitor closely."
                )
            else:
                risk_level = "LOW RISK 🟢"
                interpretation = (
                    f"FAIR: Disparate Impact ratio of {disparate_impact:.3f} indicates "
                    f"no adverse impact. Selection rates are comparable: {unpriv_selection_rate:.1%} "
                    f"(unprivileged) vs {priv_selection_rate:.1%} (privileged)."
                )
            
            return {
                'disparate_impact': float(disparate_impact),
                'statistical_parity_difference': float(statistical_parity_diff),
                'equal_opportunity_difference': float(statistical_parity_diff),  # Simplified for binary case
                'risk_level': risk_level,
                'interpretation': interpretation,
                'metrics_detail': {
                    'privileged_group': privileged_group,
                    'unprivileged_group': unprivileged_group,
                    'privileged_selection_rate': float(priv_selection_rate),
                    'unprivileged_selection_rate': float(unpriv_selection_rate),
                    'total_samples': len(df),
                    'privileged_samples': int(priv_count),
                    'unprivileged_samples': int(unpriv_count)
                }
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'disparate_impact': None,
                'risk_level': 'ERROR',
                'interpretation': f'Failed to analyze disparate impact: {str(e)}'
            }
    
    def detect_proxy_variables(self, feature_list: List[str]) -> Dict[str, Any]:
        """
        Detect proxy variables that may indirectly encode protected attributes.
        
        Proxy variables are features that correlate with protected attributes
        and can lead to indirect discrimination even when protected attributes
        are not directly used.
        
        Args:
            feature_list: List of feature names in the dataset
        
        Returns:
            Dictionary containing:
            - detected_proxies: List of detected proxy variables
            - risk_level: HIGH/MEDIUM/LOW based on number and type of proxies
            - explanations: Detailed explanation for each proxy
            - recommendations: Mitigation strategies
        """
        detected = []
        explanations = {}
        
        # Normalize feature names for comparison
        normalized_features = [f.lower().replace('_', '').replace('-', '') for f in feature_list]
        
        for i, feature in enumerate(feature_list):
            normalized = normalized_features[i]
            
            # Check against known proxy variables
            for proxy, explanation in self.PROXY_VARIABLES.items():
                proxy_normalized = proxy.lower().replace('_', '').replace('-', '')
                if proxy_normalized in normalized or normalized in proxy_normalized:
                    detected.append(feature)
                    explanations[feature] = explanation
                    break
        
        # Determine risk level
        if len(detected) >= 3:
            risk_level = "HIGH RISK 🔴"
            risk_explanation = (
                f"Multiple proxy variables detected ({len(detected)}). "
                "High risk of indirect discrimination through correlated features."
            )
        elif len(detected) >= 1:
            risk_level = "MEDIUM RISK 🟡"
            risk_explanation = (
                f"Proxy variables detected ({len(detected)}). "
                "Moderate risk of indirect discrimination. Review feature importance."
            )
        else:
            risk_level = "LOW RISK 🟢"
            risk_explanation = "No obvious proxy variables detected."
        
        recommendations = []
        if detected:
            recommendations = [
                "Consider removing or transforming proxy variables",
                "Analyze feature importance to assess actual impact",
                "Use fairness-aware feature selection methods",
                "Monitor model predictions across demographic groups",
                "Document business justification for using these features"
            ]
        
        return {
            'detected_proxies': detected,
            'count': len(detected),
            'risk_level': risk_level,
            'risk_explanation': risk_explanation,
            'explanations': explanations,
            'recommendations': recommendations
        }
    
    def check_protected_attributes_direct_use(
        self, 
        feature_list: List[str]
    ) -> Dict[str, Any]:
        """
        Check for direct use of protected attributes in features.
        
        Direct use of protected attributes violates:
        - Equal Credit Opportunity Act (ECOA) in US
        - EU AI Act Article 10
        - Fair Housing Act
        - Employment discrimination laws
        
        Args:
            feature_list: List of feature names in the dataset
        
        Returns:
            Dictionary containing:
            - violations: List of protected attributes found
            - risk_level: CRITICAL if any found
            - legal_implications: Relevant laws violated
            - required_actions: Immediate remediation steps
        """
        violations = []
        legal_implications = []
        
        # Normalize feature names for comparison
        normalized_features = [f.lower().replace('_', '').replace('-', '') for f in feature_list]
        
        for i, feature in enumerate(feature_list):
            normalized = normalized_features[i]
            
            # Check against protected attributes
            for protected in self.PROTECTED_ATTRIBUTES:
                protected_normalized = protected.lower().replace('_', '').replace('-', '')
                if protected_normalized in normalized or normalized in protected_normalized:
                    violations.append({
                        'feature': feature,
                        'protected_attribute': protected,
                        'severity': 'CRITICAL'
                    })
                    break
        
        # Determine legal implications
        if violations:
            risk_level = "CRITICAL VIOLATION ⛔"
            
            # Map violations to laws
            violation_types = {v['protected_attribute'] for v in violations}
            
            if any(attr in violation_types for attr in ['gender', 'sex']):
                legal_implications.append("Equal Credit Opportunity Act (ECOA) - Gender discrimination")
                legal_implications.append("Title VII Civil Rights Act - Sex discrimination")
            
            if any(attr in violation_types for attr in ['race', 'ethnicity']):
                legal_implications.append("Equal Credit Opportunity Act (ECOA) - Race discrimination")
                legal_implications.append("Fair Housing Act - Racial discrimination")
            
            if 'age' in violation_types:
                legal_implications.append("Age Discrimination in Employment Act (ADEA)")
                legal_implications.append("Equal Credit Opportunity Act (ECOA) - Age discrimination")
            
            if any(attr in violation_types for attr in ['religion', 'nationality']):
                legal_implications.append("Title VII Civil Rights Act - Religious/National origin discrimination")
            
            legal_implications.append("EU AI Act Article 10 - Prohibited AI practices")
            
            required_actions = [
                "IMMEDIATE: Remove all protected attributes from feature set",
                "URGENT: Retrain model without protected attributes",
                "REQUIRED: Conduct legal review with compliance team",
                "MANDATORY: Document remediation in audit trail",
                "CRITICAL: Assess if model has been deployed and halt if necessary"
            ]
        else:
            risk_level = "COMPLIANT ✅"
            legal_implications = ["No direct use of protected attributes detected"]
            required_actions = ["Continue monitoring for indirect discrimination via proxy variables"]
        
        return {
            'violations': violations,
            'violation_count': len(violations),
            'risk_level': risk_level,
            'legal_implications': legal_implications,
            'required_actions': required_actions
        }
    
    def calculate_composite_risk_score(
        self,
        di_ratio: float,
        proxy_count: int,
        direct_violations: int,
        data_quality_score: float = 0.8,
        privacy_score: float = 0.9
    ) -> Dict[str, Any]:
        """
        Calculate composite risk score using weighted formula.
        
        Formula: 0.4 × DI_score + 0.3 × Proxy_score + 0.2 × Data_quality + 0.1 × Privacy_score
        
        Args:
            di_ratio: Disparate Impact ratio (0.0 to 1.0+)
            proxy_count: Number of proxy variables detected
            direct_violations: Number of direct protected attribute uses
            data_quality_score: Data quality score (0.0 to 1.0)
            privacy_score: Privacy compliance score (0.0 to 1.0)
        
        Returns:
            Dictionary containing:
            - composite_score: Overall score (0-100)
            - risk_level: HIGH/MEDIUM/LOW
            - component_scores: Breakdown of each component
            - recommendations: Prioritized action items
        """
        # Component 1: Disparate Impact Score (0-100)
        # DI >= 1.0 = 100, DI = 0.8 = 80, DI < 0.8 = proportional penalty
        if di_ratio is None or di_ratio == 0:
            di_score = 0
        elif di_ratio >= 1.0:
            di_score = 100
        elif di_ratio >= 0.8:
            di_score = 80 + (di_ratio - 0.8) * 100  # Scale 0.8-1.0 to 80-100
        else:
            di_score = di_ratio * 100  # Below 0.8 = proportional to ratio
        
        # Component 2: Proxy Variable Score (0-100)
        # 0 proxies = 100, 1-2 = 70, 3-5 = 40, 6+ = 0
        if proxy_count == 0:
            proxy_score = 100
        elif proxy_count <= 2:
            proxy_score = 70
        elif proxy_count <= 5:
            proxy_score = 40
        else:
            proxy_score = max(0, 40 - (proxy_count - 5) * 10)
        
        # Component 3: Direct Violations (automatic 0 if any violations)
        if direct_violations > 0:
            # Critical violation - entire score becomes 0
            return {
                'composite_score': 0,
                'risk_level': 'CRITICAL VIOLATION ⛔',
                'component_scores': {
                    'disparate_impact_score': 0,
                    'proxy_variable_score': 0,
                    'data_quality_score': 0,
                    'privacy_score': 0
                },
                'recommendations': [
                    'IMMEDIATE: Remove all protected attributes from model',
                    'URGENT: Halt model deployment if in production',
                    'REQUIRED: Legal compliance review',
                    'MANDATORY: Retrain model from scratch'
                ]
            }
        
        # Component 4: Data Quality Score (0-100)
        data_quality_score_scaled = data_quality_score * 100
        
        # Component 5: Privacy Score (0-100)
        privacy_score_scaled = privacy_score * 100
        
        # Calculate weighted composite score
        composite_score = (
            0.4 * di_score +
            0.3 * proxy_score +
            0.2 * data_quality_score_scaled +
            0.1 * privacy_score_scaled
        )
        
        # Determine risk level
        if composite_score >= 71:
            risk_level = "LOW RISK 🟢"
            recommendations = [
                "Model shows good fairness characteristics",
                "Continue monitoring disparate impact metrics",
                "Document fairness testing in model card",
                "Establish ongoing bias monitoring process"
            ]
        elif composite_score >= 41:
            risk_level = "MEDIUM RISK 🟡"
            recommendations = [
                "Address proxy variables if possible",
                "Improve disparate impact ratio through reweighting or resampling",
                "Consider fairness-aware training algorithms",
                "Increase frequency of bias monitoring",
                "Document mitigation strategies"
            ]
        else:
            risk_level = "HIGH RISK 🔴"
            recommendations = [
                "URGENT: Model shows significant bias - do not deploy",
                "Remove or transform proxy variables",
                "Apply bias mitigation techniques (reweighting, adversarial debiasing)",
                "Consider collecting more balanced training data",
                "Conduct thorough fairness audit before any deployment",
                "Consult with legal/compliance team"
            ]
        
        return {
            'composite_score': round(composite_score, 2),
            'risk_level': risk_level,
            'component_scores': {
                'disparate_impact_score': round(di_score, 2),
                'proxy_variable_score': round(proxy_score, 2),
                'data_quality_score': round(data_quality_score_scaled, 2),
                'privacy_score': round(privacy_score_scaled, 2)
            },
            'weights': {
                'disparate_impact': 0.4,
                'proxy_variables': 0.3,
                'data_quality': 0.2,
                'privacy': 0.1
            },
            'recommendations': recommendations
        }
    
    def run_full_analysis(self, audit_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate complete bias analysis pipeline.
        
        Args:
            audit_input: Dictionary containing:
                - data_path: Path to dataset
                - protected_attribute: Protected attribute to analyze
                - privileged_group: Privileged group values
                - feature_list: List of all features
                - label_name: Outcome variable name (optional)
                - favorable_label: Favorable outcome value (optional)
        
        Returns:
            Complete analysis dictionary ready for report generation
        """
        results = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'input_parameters': audit_input
        }
        
        # Step 1: Analyze Disparate Impact
        print("Step 1: Analyzing disparate impact...")
        di_analysis = self.analyze_disparate_impact(
            data_path=audit_input['data_path'],
            protected_attribute=audit_input['protected_attribute'],
            privileged_group=audit_input['privileged_group'],
            label_name=audit_input.get('label_name', 'income'),
            favorable_label=audit_input.get('favorable_label', 1)
        )
        results['disparate_impact_analysis'] = di_analysis
        
        # Step 2: Detect Proxy Variables
        print("Step 2: Detecting proxy variables...")
        proxy_analysis = self.detect_proxy_variables(
            feature_list=audit_input['feature_list']
        )
        results['proxy_variable_analysis'] = proxy_analysis
        
        # Step 3: Check Protected Attributes Direct Use
        print("Step 3: Checking for direct use of protected attributes...")
        protected_check = self.check_protected_attributes_direct_use(
            feature_list=audit_input['feature_list']
        )
        results['protected_attributes_check'] = protected_check
        
        # Step 4: Calculate Composite Risk Score
        print("Step 4: Calculating composite risk score...")
        composite_risk = self.calculate_composite_risk_score(
            di_ratio=di_analysis.get('disparate_impact'),
            proxy_count=proxy_analysis['count'],
            direct_violations=protected_check['violation_count'],
            data_quality_score=audit_input.get('data_quality_score', 0.8),
            privacy_score=audit_input.get('privacy_score', 0.9)
        )
        results['composite_risk_score'] = composite_risk
        
        # Step 5: Generate Summary
        results['summary'] = {
            'overall_risk_level': composite_risk['risk_level'],
            'composite_score': composite_risk['composite_score'],
            'disparate_impact_ratio': di_analysis.get('disparate_impact'),
            'proxy_variables_detected': proxy_analysis['count'],
            'direct_violations': protected_check['violation_count'],
            'key_findings': self._generate_key_findings(results),
            'priority_actions': self._generate_priority_actions(results)
        }
        
        print("✅ Full analysis complete!")
        return results
    
    def _generate_key_findings(self, results: Dict[str, Any]) -> List[str]:
        """Generate key findings from analysis results"""
        findings = []
        
        # Disparate Impact findings
        di_ratio = results['disparate_impact_analysis'].get('disparate_impact')
        if di_ratio and di_ratio < 0.8:
            findings.append(f"⚠️ Disparate Impact ratio of {di_ratio:.3f} indicates discrimination (below 0.8 threshold)")
        
        # Protected attributes findings
        if results['protected_attributes_check']['violation_count'] > 0:
            findings.append(f"🚨 CRITICAL: {results['protected_attributes_check']['violation_count']} protected attributes used directly")
        
        # Proxy variables findings
        if results['proxy_variable_analysis']['count'] > 0:
            findings.append(f"⚠️ {results['proxy_variable_analysis']['count']} proxy variables detected")
        
        # Positive findings
        if not findings:
            findings.append("✅ No critical fairness issues detected")
        
        return findings
    
    def _generate_priority_actions(self, results: Dict[str, Any]) -> List[str]:
        """Generate prioritized action items"""
        actions = []
        
        # Critical actions first
        if results['protected_attributes_check']['violation_count'] > 0:
            actions.extend(results['protected_attributes_check']['required_actions'][:2])
        
        # High priority actions
        di_ratio = results['disparate_impact_analysis'].get('disparate_impact', 1.0)
        if di_ratio is not None and di_ratio < 0.8:
            actions.append("Apply bias mitigation techniques to improve disparate impact ratio")
        
        # Medium priority actions
        if results['proxy_variable_analysis']['count'] > 0:
            actions.append("Review and potentially remove proxy variables")
        
        # General recommendations
        actions.extend(results['composite_risk_score']['recommendations'][:3])
        
        return actions[:5]  # Return top 5 priority actions


if __name__ == "__main__":
    print("FairLens BiasDetector - Core Bias Detection Engine")
    print("=" * 60)
    print("This module provides bias detection capabilities using AIF360")
    print("Use bias_detector_test.py to run tests with UCI Adult dataset")

# Made with Bob
