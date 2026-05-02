import React, { useState, useMemo } from 'react';

const Dashboard = () => {
  const [periodType, setPeriodType] = useState('Monthly');
  const [selectedPeriod, setSelectedPeriod] = useState('Jan');
  const [featureType, setFeatureType] = useState('Gender');

  // Simulated monthly DI values for Gender
  const genderData = {
    Jan: 0.71, Feb: 0.68, Mar: 0.65,
    Apr: 0.70, May: 0.62, Jun: 0.58,
    Jul: 0.60, Aug: 0.63, Sep: 0.67,
    Oct: 0.69, Nov: 0.72, Dec: 0.75
  };

  // Simulated data for other features (similar pattern)
  const zipCodeData = {
    Jan: 0.82, Feb: 0.79, Mar: 0.76,
    Apr: 0.81, May: 0.73, Jun: 0.69,
    Jul: 0.71, Aug: 0.74, Sep: 0.78,
    Oct: 0.80, Nov: 0.83, Dec: 0.86
  };

  const ethnicGroupData = {
    Jan: 0.68, Feb: 0.65, Mar: 0.62,
    Apr: 0.67, May: 0.59, Jun: 0.55,
    Jul: 0.57, Aug: 0.60, Sep: 0.64,
    Oct: 0.66, Nov: 0.69, Dec: 0.72
  };

  // Get period options based on period type
  const getPeriodOptions = () => {
    switch (periodType) {
      case 'Monthly':
        return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      case 'Quarterly':
        return ['Q1', 'Q2', 'Q3', 'Q4'];
      case 'Fiscal Year':
        return ['2023', '2024', '2025', '2026'];
      default:
        return [];
    }
  };

  // Get data based on feature type
  const getFeatureData = () => {
    switch (featureType) {
      case 'Gender':
        return genderData;
      case 'Zip Code':
        return zipCodeData;
      case 'Ethnic Group':
        return ethnicGroupData;
      default:
        return genderData;
    }
  };

  // Get status based on DI value
  const getStatus = (di) => {
    if (di >= 0.8) return { icon: '🟢', label: 'COMPLIANT', class: 'status-compliant' };
    if (di >= 0.7) return { icon: '🟡', label: 'WARNING', class: 'status-warning' };
    return { icon: '🔴', label: 'VIOLATION', class: 'status-violation' };
  };

  // Calculate trend
  const calculateTrend = () => {
    const data = getFeatureData();
    const values = Object.values(data);
    const firstHalf = values.slice(0, 6).reduce((a, b) => a + b, 0) / 6;
    const secondHalf = values.slice(6).reduce((a, b) => a + b, 0) / 6;
    return secondHalf > firstHalf ? 'improving' : 'declining';
  };

  const currentData = getFeatureData();
  const trend = calculateTrend();

  // Distribution data for the selected feature
  const distributionData = useMemo(() => {
    const data = getFeatureData();
    return Object.entries(data).map(([month, di]) => ({
      month,
      di,
      status: getStatus(di)
    }));
  }, [featureType]);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📊 Dashboard</h1>
        <p>Bias metrics trends and analysis</p>
      </div>

      <div className="dashboard-controls">
        <div className="control-group">
          <label>Period Type</label>
          <select 
            value={periodType} 
            onChange={(e) => {
              setPeriodType(e.target.value);
              setSelectedPeriod(getPeriodOptions()[0]);
            }}
            className="dashboard-select"
          >
            <option>Monthly</option>
            <option>Quarterly</option>
            <option>Fiscal Year</option>
          </select>
        </div>

        <div className="control-group">
          <label>Period</label>
          <select 
            value={selectedPeriod} 
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="dashboard-select"
          >
            {getPeriodOptions().map(option => (
              <option key={option}>{option}</option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>Feature Type</label>
          <select 
            value={featureType} 
            onChange={(e) => setFeatureType(e.target.value)}
            className="dashboard-select"
          >
            <option>Gender</option>
            <option>Zip Code</option>
            <option>Ethnic Group</option>
          </select>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="trend-section">
          <h2>Trend Analysis - {featureType}</h2>
          <div className="trend-indicator">
            <span className={`trend-badge trend-${trend}`}>
              {trend === 'improving' ? '📈 Improving' : '📉 Declining'}
            </span>
          </div>
          <div className="trend-chart">
            {distributionData.map((item, index) => (
              <div key={index} className="trend-bar-container">
                <div className="trend-month">{item.month}</div>
                <div className="trend-bar-wrapper">
                  <div 
                    className={`trend-bar ${item.status.class}`}
                    style={{ height: `${item.di * 100}%` }}
                  >
                    <span className="trend-value">{item.di.toFixed(2)}</span>
                  </div>
                </div>
                <div className="trend-status">{item.status.icon}</div>
              </div>
            ))}
          </div>
          <div className="trend-legend">
            <div className="legend-item">
              <span className="legend-color status-compliant"></span>
              <span>≥ 0.8 Compliant</span>
            </div>
            <div className="legend-item">
              <span className="legend-color status-warning"></span>
              <span>0.7-0.79 Warning</span>
            </div>
            <div className="legend-item">
              <span className="legend-color status-violation"></span>
              <span>{'< 0.7 Violation'}</span>
            </div>
          </div>
        </div>

        <div className="distribution-section">
          <h2>Distribution Summary</h2>
          <div className="distribution-grid">
            {distributionData.map((item, index) => (
              <div key={index} className={`distribution-card ${item.status.class}`}>
                <div className="dist-month">{item.month}</div>
                <div className="dist-di">DI: {item.di.toFixed(2)}</div>
                <div className="dist-status">
                  {item.status.icon} {item.status.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="stats-section">
          <h2>Key Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Average DI</div>
              <div className="stat-value">
                {(Object.values(currentData).reduce((a, b) => a + b, 0) / 12).toFixed(2)}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Lowest DI</div>
              <div className="stat-value stat-danger">
                {Math.min(...Object.values(currentData)).toFixed(2)}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Highest DI</div>
              <div className="stat-value stat-success">
                {Math.max(...Object.values(currentData)).toFixed(2)}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Trend</div>
              <div className={`stat-value stat-${trend}`}>
                {trend === 'improving' ? '↗ Improving' : '↘ Declining'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

// Made with Bob