import React from 'react';

const Regulations = () => {
  const regulations = [
    {
      name: 'EU AI Act Article 6',
      link: 'https://artificialintelligenceact.eu/article/6/',
      description: 'Classification rules for high-risk AI systems',
      ourStatus: 'non-compliant',
      violation: 'Gender feature shows DI=0.362, below 0.8 threshold',
      recommendation: 'Retrain model without gender feature or implement bias mitigation techniques to achieve DI ≥ 0.8'
    },
    {
      name: 'ECOA',
      fullName: 'Equal Credit Opportunity Act',
      link: 'https://www.consumerfinance.gov/rules-policy/regulations/1002/',
      description: 'Prohibits discrimination in any aspect of a credit transaction',
      ourStatus: 'non-compliant',
      violation: 'Disparate impact detected in credit approval rates by gender',
      recommendation: 'Review and adjust decision thresholds to ensure equal treatment across protected groups'
    },
    {
      name: 'GDPR Article 5',
      fullName: 'Principles relating to processing of personal data',
      link: 'https://gdpr-info.eu/art-5-gdpr/',
      description: 'Data minimization - personal data must be adequate, relevant and limited to what is necessary',
      ourStatus: 'non-compliant',
      violation: 'Zip code detected as proxy variable for race/ethnicity',
      recommendation: 'Remove zip code feature or demonstrate legitimate business necessity with documented justification'
    },
    {
      name: 'EU AI Act Article 9',
      fullName: 'Risk management system',
      link: 'https://artificialintelligenceact.eu/article/9/',
      description: 'Requirements for risk management systems for high-risk AI',
      ourStatus: 'compliant',
      violation: null,
      recommendation: null
    }
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>⚖️ Regulations</h1>
        <p>Compliance status and regulatory requirements</p>
      </div>

      <div className="regulations-content">
        {regulations.map((reg, index) => (
          <div key={index} className={`regulation-card regulation-${reg.ourStatus}`}>
            <div className="regulation-header">
              <div className="regulation-title">
                <h2>{reg.name}</h2>
                {reg.fullName && <div className="regulation-fullname">{reg.fullName}</div>}
              </div>
              <div className={`regulation-status status-${reg.ourStatus}`}>
                {reg.ourStatus === 'compliant' && '🟢 Compliant'}
                {reg.ourStatus === 'non-compliant' && '🔴 Non-Compliant'}
                {reg.ourStatus === 'warning' && '🟡 Needs Review'}
              </div>
            </div>

            <div className="regulation-description">
              {reg.description}
            </div>

            <div className="regulation-link">
              <a href={reg.link} target="_blank" rel="noopener noreferrer">
                🔗 View Full Regulation
              </a>
            </div>

            {reg.ourStatus === 'non-compliant' && (
              <div className="regulation-details">
                <div className="violation-section">
                  <h4>⚠️ Violation Details:</h4>
                  <p>{reg.violation}</p>
                </div>
                <div className="recommendation-section">
                  <h4>💡 Recommended Fix:</h4>
                  <p>{reg.recommendation}</p>
                </div>
              </div>
            )}

            {reg.ourStatus === 'compliant' && (
              <div className="compliant-message">
                ✓ System meets all requirements for this regulation
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="regulations-footer">
        <div className="footer-note">
          <strong>Note:</strong> This compliance assessment is based on current audit data. 
          Regular monitoring and updates are required to maintain compliance.
        </div>
      </div>
    </div>
  );
};

export default Regulations;

// Made with Bob