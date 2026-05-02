import React from 'react';

const AlertCenter = () => {
  const alerts = [
    {
      feature: 'Gender',
      status: 'violation',
      metric: 'DI=0.362',
      icon: '🔴',
      message: 'VIOLATION - Disparate Impact below 0.8 threshold'
    },
    {
      feature: 'Zip Code',
      status: 'warning',
      metric: 'Proxy variable detected',
      icon: '🟡',
      message: 'WARNING - Potential proxy for protected attribute (race/ethnicity)'
    },
    {
      feature: 'Age',
      status: 'compliant',
      metric: 'DI=0.85',
      icon: '🟢',
      message: 'COMPLIANT - Within acceptable range'
    }
  ];

  const regulations = [
    {
      name: 'EU AI Act Article 6',
      classification: 'HIGH RISK',
      description: 'System classified as high-risk due to creditworthiness assessment',
      status: 'violation'
    },
    {
      name: 'ECOA',
      fullName: 'Equal Credit Opportunity Act',
      description: 'Prohibits discrimination in credit decisions',
      status: 'violation'
    },
    {
      name: 'GDPR Article 5',
      fullName: 'Data Minimization',
      description: 'Personal data must be adequate, relevant and limited',
      status: 'warning'
    }
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>🚨 Alert Center</h1>
        <p>Current bias alerts and compliance status</p>
      </div>

      <div className="alert-section">
        <h2>Current Bias Alerts</h2>
        <div className="alerts-grid">
          {alerts.map((alert, index) => (
            <div key={index} className={`alert-card alert-${alert.status}`}>
              <div className="alert-header">
                <span className="alert-icon">{alert.icon}</span>
                <h3>{alert.feature}</h3>
              </div>
              <div className="alert-metric">{alert.metric}</div>
              <div className="alert-message">{alert.message}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="compliance-section">
        <h2>Compliance Rules Summary</h2>
        <div className="compliance-list">
          {regulations.map((reg, index) => (
            <div key={index} className={`compliance-card compliance-${reg.status}`}>
              <div className="compliance-header">
                <h3>{reg.name}</h3>
                {reg.classification && (
                  <span className="classification-badge">{reg.classification}</span>
                )}
              </div>
              {reg.fullName && <div className="compliance-fullname">{reg.fullName}</div>}
              <div className="compliance-description">{reg.description}</div>
              <div className="compliance-status">
                {reg.status === 'violation' && '🔴 Non-Compliant'}
                {reg.status === 'warning' && '🟡 Needs Review'}
                {reg.status === 'compliant' && '🟢 Compliant'}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="action-section">
        <button className="btn-generate-report">
          📄 Generate Monthly Report
        </button>
      </div>
    </div>
  );
};

export default AlertCenter;

// Made with Bob