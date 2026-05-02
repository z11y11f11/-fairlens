import React, { useState } from 'react';

const AuditForm = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    // Section 1: Model Information
    modelName: '',
    modelType: '',
    useCase: 'Loan/Credit Approval',
    deploymentDate: '',
    riskClassification: 'HIGH RISK - EU AI Act Article 6',
    
    // Section 2: Features & Protected Attributes
    features: {
      age: { selected: false, protected: true, proxy: false, proxyFor: '' },
      gender: { selected: false, protected: true, proxy: false, proxyFor: '' },
      income: { selected: false, protected: false, proxy: false, proxyFor: '' },
      zip_code: { selected: false, protected: false, proxy: true, proxyFor: 'race' },
      occupation: { selected: false, protected: false, proxy: true, proxyFor: 'possible' },
      credit_history: { selected: false, protected: false, proxy: false, proxyFor: '' }
    },
    customFeatures: [],
    
    // Section 3: Accountability (RACI)
    modelDeveloperName: '',
    modelDeveloperEmail: '',
    approvalAuthorityName: '',
    approvalAuthorityRole: '',
    monitorOwnerName: '',
    monitorOwnerDepartment: '',
    complaintHandlerName: '',
    complaintHandlerContact: '',
    lastReviewDate: '',
    
    // Section 4: Data Information
    trainingDataStartYear: '',
    trainingDataEndYear: '',
    dataSource: '',
    recordCount: '',
    dataGapsLimitations: ''
  });

  const [customFeatureName, setCustomFeatureName] = useState('');
  const [customFeatureProtected, setCustomFeatureProtected] = useState(false);
  const [customFeatureProxy, setCustomFeatureProxy] = useState(false);
  const [customFeatureProxyFor, setCustomFeatureProxyFor] = useState('');
  const [submitStatus, setSubmitStatus] = useState({ type: '', message: '' });

  const tabs = [
    'Model Information',
    'Features & Protected Attributes',
    'Accountability (RACI)',
    'Data Information'
  ];

  const modelTypes = [
    'XGBoost',
    'Random Forest',
    'Neural Network',
    'Logistic Regression',
    'Rule-based'
  ];

  const dataSources = [
    'Internal historical',
    'External bureau',
    'Mixed'
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFeatureToggle = (featureName) => {
    setFormData(prev => ({
      ...prev,
      features: {
        ...prev.features,
        [featureName]: {
          ...prev.features[featureName],
          selected: !prev.features[featureName].selected
        }
      }
    }));
  };

  const handleAddCustomFeature = () => {
    if (customFeatureName.trim()) {
      const newFeature = {
        name: customFeatureName.trim(),
        selected: true,
        protected: customFeatureProtected,
        proxy: customFeatureProxy,
        proxyFor: customFeatureProxyFor.trim()
      };
      
      setFormData(prev => ({
        ...prev,
        customFeatures: [...prev.customFeatures, newFeature]
      }));
      
      // Reset custom feature inputs
      setCustomFeatureName('');
      setCustomFeatureProtected(false);
      setCustomFeatureProxy(false);
      setCustomFeatureProxyFor('');
    }
  };

  const handleRemoveCustomFeature = (index) => {
    setFormData(prev => ({
      ...prev,
      customFeatures: prev.customFeatures.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitStatus({ type: 'loading', message: 'Generating audit report...' });

    try {
      // Prepare selected features
      const selectedFeatures = [];
      Object.entries(formData.features).forEach(([name, data]) => {
        if (data.selected) {
          selectedFeatures.push({
            name,
            protected: data.protected,
            proxy: data.proxy,
            proxyFor: data.proxyFor
          });
        }
      });

      // Add custom features
      formData.customFeatures.forEach(feature => {
        if (feature.selected) {
          selectedFeatures.push({
            name: feature.name,
            protected: feature.protected,
            proxy: feature.proxy,
            proxyFor: feature.proxyFor
          });
        }
      });

      const auditData = {
        modelInfo: {
          name: formData.modelName,
          type: formData.modelType,
          useCase: formData.useCase,
          deploymentDate: formData.deploymentDate,
          riskClassification: formData.riskClassification
        },
        features: selectedFeatures,
        accountability: {
          modelDeveloper: {
            name: formData.modelDeveloperName,
            email: formData.modelDeveloperEmail
          },
          approvalAuthority: {
            name: formData.approvalAuthorityName,
            role: formData.approvalAuthorityRole
          },
          monitorOwner: {
            name: formData.monitorOwnerName,
            department: formData.monitorOwnerDepartment
          },
          complaintHandler: {
            name: formData.complaintHandlerName,
            contact: formData.complaintHandlerContact
          },
          lastReviewDate: formData.lastReviewDate
        },
        dataInfo: {
          trainingPeriod: {
            start: formData.trainingDataStartYear,
            end: formData.trainingDataEndYear
          },
          dataSource: formData.dataSource,
          recordCount: formData.recordCount,
          dataGapsLimitations: formData.dataGapsLimitations
        }
      };

      const response = await fetch('/api/audit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(auditData)
      });

      if (response.ok) {
        const result = await response.json();
        setSubmitStatus({ 
          type: 'success', 
          message: 'Audit report generated successfully! Check the backend for results.' 
        });
      } else {
        const error = await response.json();
        setSubmitStatus({ 
          type: 'error', 
          message: `Error: ${error.error || 'Failed to generate audit report'}` 
        });
      }
    } catch (error) {
      setSubmitStatus({ 
        type: 'error', 
        message: `Network error: ${error.message}` 
      });
    }
  };

  const renderSection1 = () => (
    <div className="form-section">
      <h2>Model Information</h2>
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="modelName">Model Name *</label>
          <input
            type="text"
            id="modelName"
            value={formData.modelName}
            onChange={(e) => handleInputChange('modelName', e.target.value)}
            placeholder="e.g., CreditScore_XGB_v2.1"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="modelType">Model Type *</label>
          <select
            id="modelType"
            value={formData.modelType}
            onChange={(e) => handleInputChange('modelType', e.target.value)}
            required
          >
            <option value="">Select model type</option>
            {modelTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="useCase">Use Case</label>
          <input
            type="text"
            id="useCase"
            value={formData.useCase}
            readOnly
            className="readonly-field"
          />
        </div>

        <div className="form-group">
          <label htmlFor="deploymentDate">Deployment Date *</label>
          <input
            type="date"
            id="deploymentDate"
            value={formData.deploymentDate}
            onChange={(e) => handleInputChange('deploymentDate', e.target.value)}
            required
          />
        </div>

        <div className="form-group full-width">
          <label htmlFor="riskClassification">Risk Classification</label>
          <input
            type="text"
            id="riskClassification"
            value={formData.riskClassification}
            readOnly
            className="readonly-field risk-high"
          />
          <p className="field-note">
            This system is classified as HIGH RISK under EU AI Act Article 6 due to its use in creditworthiness assessment.
          </p>
        </div>
      </div>
    </div>
  );

  const renderSection2 = () => (
    <div className="form-section">
      <h2>Features & Protected Attributes</h2>
      <p className="section-description">
        Select the features used by your model. Protected attributes and proxy variables are automatically flagged.
      </p>
      
      <div className="features-list">
        <div className="features-header">
          <span className="col-feature">Feature Name</span>
          <span className="col-protected">Protected</span>
          <span className="col-proxy">Proxy</span>
          <span className="col-select">Use in Model</span>
        </div>
        
        {Object.entries(formData.features).map(([name, data]) => (
          <div key={name} className="feature-row">
            <span className="col-feature">{name}</span>
            <span className="col-protected">
              {data.protected ? (
                <span className="badge badge-protected">YES</span>
              ) : (
                <span className="badge badge-normal">NO</span>
              )}
            </span>
            <span className="col-proxy">
              {data.proxy ? (
                <span className="badge badge-warning">YES → {data.proxyFor}</span>
              ) : (
                <span className="badge badge-normal">NO</span>
              )}
            </span>
            <span className="col-select">
              <input
                type="checkbox"
                checked={data.selected}
                onChange={() => handleFeatureToggle(name)}
              />
            </span>
          </div>
        ))}

        {formData.customFeatures.map((feature, index) => (
          <div key={`custom-${index}`} className="feature-row custom-feature">
            <span className="col-feature">{feature.name}</span>
            <span className="col-protected">
              {feature.protected ? (
                <span className="badge badge-protected">YES</span>
              ) : (
                <span className="badge badge-normal">NO</span>
              )}
            </span>
            <span className="col-proxy">
              {feature.proxy ? (
                <span className="badge badge-warning">YES → {feature.proxyFor}</span>
              ) : (
                <span className="badge badge-normal">NO</span>
              )}
            </span>
            <span className="col-select">
              <button
                type="button"
                className="btn-remove"
                onClick={() => handleRemoveCustomFeature(index)}
              >
                Remove
              </button>
            </span>
          </div>
        ))}
      </div>

      <div className="add-custom-feature">
        <h3>Add Custom Feature</h3>
        <div className="custom-feature-form">
          <input
            type="text"
            placeholder="Feature name"
            value={customFeatureName}
            onChange={(e) => setCustomFeatureName(e.target.value)}
          />
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={customFeatureProtected}
              onChange={(e) => setCustomFeatureProtected(e.target.checked)}
            />
            Protected attribute
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={customFeatureProxy}
              onChange={(e) => setCustomFeatureProxy(e.target.checked)}
            />
            Proxy variable
          </label>
          {customFeatureProxy && (
            <input
              type="text"
              placeholder="Proxy for (e.g., race, gender)"
              value={customFeatureProxyFor}
              onChange={(e) => setCustomFeatureProxyFor(e.target.value)}
            />
          )}
          <button
            type="button"
            className="btn-add"
            onClick={handleAddCustomFeature}
          >
            Add Feature
          </button>
        </div>
      </div>
    </div>
  );

  const renderSection3 = () => (
    <div className="form-section">
      <h2>Accountability (RACI Matrix)</h2>
      <p className="section-description">
        Define the responsible parties for model governance and compliance.
      </p>
      
      <div className="form-grid">
        <div className="form-group-header full-width">
          <h3>Model Developer (Responsible)</h3>
        </div>
        <div className="form-group">
          <label htmlFor="modelDeveloperName">Full Name *</label>
          <input
            type="text"
            id="modelDeveloperName"
            value={formData.modelDeveloperName}
            onChange={(e) => handleInputChange('modelDeveloperName', e.target.value)}
            placeholder="John Doe"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="modelDeveloperEmail">Email *</label>
          <input
            type="email"
            id="modelDeveloperEmail"
            value={formData.modelDeveloperEmail}
            onChange={(e) => handleInputChange('modelDeveloperEmail', e.target.value)}
            placeholder="john.doe@company.com"
            required
          />
        </div>

        <div className="form-group-header full-width">
          <h3>Approval Authority (Accountable)</h3>
        </div>
        <div className="form-group">
          <label htmlFor="approvalAuthorityName">Full Name *</label>
          <input
            type="text"
            id="approvalAuthorityName"
            value={formData.approvalAuthorityName}
            onChange={(e) => handleInputChange('approvalAuthorityName', e.target.value)}
            placeholder="Jane Smith"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="approvalAuthorityRole">Role/Title *</label>
          <input
            type="text"
            id="approvalAuthorityRole"
            value={formData.approvalAuthorityRole}
            onChange={(e) => handleInputChange('approvalAuthorityRole', e.target.value)}
            placeholder="Chief Risk Officer"
            required
          />
        </div>

        <div className="form-group-header full-width">
          <h3>Monitor/Owner (Consulted)</h3>
        </div>
        <div className="form-group">
          <label htmlFor="monitorOwnerName">Full Name *</label>
          <input
            type="text"
            id="monitorOwnerName"
            value={formData.monitorOwnerName}
            onChange={(e) => handleInputChange('monitorOwnerName', e.target.value)}
            placeholder="Alice Johnson"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="monitorOwnerDepartment">Department *</label>
          <input
            type="text"
            id="monitorOwnerDepartment"
            value={formData.monitorOwnerDepartment}
            onChange={(e) => handleInputChange('monitorOwnerDepartment', e.target.value)}
            placeholder="Model Risk Management"
            required
          />
        </div>

        <div className="form-group-header full-width">
          <h3>Complaint Handler (Informed)</h3>
        </div>
        <div className="form-group">
          <label htmlFor="complaintHandlerName">Full Name *</label>
          <input
            type="text"
            id="complaintHandlerName"
            value={formData.complaintHandlerName}
            onChange={(e) => handleInputChange('complaintHandlerName', e.target.value)}
            placeholder="Bob Williams"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="complaintHandlerContact">Contact (Email/Phone) *</label>
          <input
            type="text"
            id="complaintHandlerContact"
            value={formData.complaintHandlerContact}
            onChange={(e) => handleInputChange('complaintHandlerContact', e.target.value)}
            placeholder="complaints@company.com"
            required
          />
        </div>

        <div className="form-group full-width">
          <label htmlFor="lastReviewDate">Last Review Date *</label>
          <input
            type="date"
            id="lastReviewDate"
            value={formData.lastReviewDate}
            onChange={(e) => handleInputChange('lastReviewDate', e.target.value)}
            required
          />
        </div>
      </div>
    </div>
  );

  const renderSection4 = () => (
    <div className="form-section">
      <h2>Data Information</h2>
      <p className="section-description">
        Provide details about the training data used for model development.
      </p>
      
      <div className="form-grid">
        <div className="form-group-header full-width">
          <h3>Training Data Period</h3>
        </div>
        <div className="form-group">
          <label htmlFor="trainingDataStartYear">Start Year *</label>
          <input
            type="number"
            id="trainingDataStartYear"
            value={formData.trainingDataStartYear}
            onChange={(e) => handleInputChange('trainingDataStartYear', e.target.value)}
            placeholder="2018"
            min="1900"
            max="2100"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="trainingDataEndYear">End Year *</label>
          <input
            type="number"
            id="trainingDataEndYear"
            value={formData.trainingDataEndYear}
            onChange={(e) => handleInputChange('trainingDataEndYear', e.target.value)}
            placeholder="2023"
            min="1900"
            max="2100"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="dataSource">Data Source *</label>
          <select
            id="dataSource"
            value={formData.dataSource}
            onChange={(e) => handleInputChange('dataSource', e.target.value)}
            required
          >
            <option value="">Select data source</option>
            {dataSources.map(source => (
              <option key={source} value={source}>{source}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="recordCount">Approximate Record Count *</label>
          <input
            type="number"
            id="recordCount"
            value={formData.recordCount}
            onChange={(e) => handleInputChange('recordCount', e.target.value)}
            placeholder="50000"
            min="0"
            required
          />
        </div>

        <div className="form-group full-width">
          <label htmlFor="dataGapsLimitations">Known Data Gaps or Limitations *</label>
          <textarea
            id="dataGapsLimitations"
            value={formData.dataGapsLimitations}
            onChange={(e) => handleInputChange('dataGapsLimitations', e.target.value)}
            placeholder="Describe any known issues with the training data, such as missing values, underrepresented groups, temporal gaps, or data quality concerns..."
            rows="6"
            required
          />
          <p className="field-note">
            Be thorough in documenting data limitations. This is critical for EU AI Act compliance.
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="audit-form-container">
      <div className="form-intro">
        <h2>AI System Audit Questionnaire</h2>
        <p>Complete all sections to generate a comprehensive audit report for EU AI Act compliance.</p>
      </div>

      <div className="tabs">
        {tabs.map((tab, index) => (
          <button
            key={index}
            className={`tab ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
            type="button"
          >
            <span className="tab-number">{index + 1}</span>
            <span className="tab-label">{tab}</span>
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="tab-content">
          {activeTab === 0 && renderSection1()}
          {activeTab === 1 && renderSection2()}
          {activeTab === 2 && renderSection3()}
          {activeTab === 3 && renderSection4()}
        </div>

        <div className="form-navigation">
          {activeTab > 0 && (
            <button
              type="button"
              className="btn-secondary"
              onClick={() => setActiveTab(activeTab - 1)}
            >
              Previous
            </button>
          )}
          
          {activeTab < tabs.length - 1 ? (
            <button
              type="button"
              className="btn-primary"
              onClick={() => setActiveTab(activeTab + 1)}
            >
              Next
            </button>
          ) : (
            <button type="submit" className="btn-submit">
              Generate Audit Report
            </button>
          )}
        </div>

        {submitStatus.message && (
          <div className={`submit-status ${submitStatus.type}`}>
            {submitStatus.message}
          </div>
        )}
      </form>
    </div>
  );
};

export default AuditForm;

// Made with Bob
