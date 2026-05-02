import React, { useState } from 'react';

const AuditForm = () => {
  const [uploadMethod, setUploadMethod] = useState('csv'); // 'csv' or 'manual'
  const [csvFile, setCsvFile] = useState(null);
  const [csvColumns, setCsvColumns] = useState([]);
  const [resultColumn, setResultColumn] = useState('');
  
  // Manual input state
  const [genderData, setGenderData] = useState({
    male: { total: '', approved: '' },
    female: { total: '', approved: '' }
  });
  
  const [ethnicGroups, setEthnicGroups] = useState([
    { name: '', total: '', approved: '' }
  ]);
  
  const [zipCodes, setZipCodes] = useState([
    { name: '', total: '', approved: '' }
  ]);

  // Calculate rate and DI
  const calculateRate = (approved, total) => {
    if (!approved || !total || total === 0) return 0;
    return (parseFloat(approved) / parseFloat(total) * 100).toFixed(1);
  };

  const calculateDI = () => {
    const maleRate = parseFloat(genderData.male.approved) / parseFloat(genderData.male.total);
    const femaleRate = parseFloat(genderData.female.approved) / parseFloat(genderData.female.total);
    
    if (!maleRate || !femaleRate) return null;
    
    const di = femaleRate / maleRate;
    return di.toFixed(2);
  };

  const getDIStatus = (di) => {
    if (!di) return null;
    if (di >= 0.8) return { icon: '🟢', label: 'COMPLIANT', class: 'status-compliant' };
    if (di >= 0.7) return { icon: '🟡', label: 'WARNING', class: 'status-warning' };
    return { icon: '🔴', label: 'VIOLATION', class: 'status-violation' };
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCsvFile(file);
      // Simulate column detection
      const mockColumns = [
        { name: 'age', type: 'normal', icon: '✅' },
        { name: 'gender', type: 'protected', icon: '🔴' },
        { name: 'income', type: 'normal', icon: '✅' },
        { name: 'zip_code', type: 'proxy', icon: '🟡' },
        { name: 'loan_approved', type: 'result', icon: '🎯' }
      ];
      setCsvColumns(mockColumns);
      setResultColumn('loan_approved');
    }
  };

  const addEthnicGroup = () => {
    setEthnicGroups([...ethnicGroups, { name: '', total: '', approved: '' }]);
  };

  const removeEthnicGroup = (index) => {
    setEthnicGroups(ethnicGroups.filter((_, i) => i !== index));
  };

  const updateEthnicGroup = (index, field, value) => {
    const updated = [...ethnicGroups];
    updated[index][field] = value;
    setEthnicGroups(updated);
  };

  const addZipCode = () => {
    setZipCodes([...zipCodes, { name: '', total: '', approved: '' }]);
  };

  const removeZipCode = (index) => {
    setZipCodes(zipCodes.filter((_, i) => i !== index));
  };

  const updateZipCode = (index, field, value) => {
    const updated = [...zipCodes];
    updated[index][field] = value;
    setZipCodes(updated);
  };

  const handleGenerateReport = () => {
    alert('Generating audit report with current data...');
  };

  const di = calculateDI();
  const diStatus = getDIStatus(di);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📋 Audit Form</h1>
        <p>Upload data or manually input metrics for bias analysis</p>
      </div>

      <div className="audit-form-content">
        {/* Section A: Upload CSV/Excel */}
        <div className="form-section">
          <h2>Section A: Upload Data File</h2>
          <div className="upload-area">
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileUpload}
              className="file-input"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="file-upload-label">
              📁 Choose CSV or Excel File
            </label>
            {csvFile && <div className="file-name">Selected: {csvFile.name}</div>}
          </div>

          {csvColumns.length > 0 && (
            <div className="csv-analysis">
              <h3>Auto-Detected Columns</h3>
              <div className="columns-list">
                {csvColumns.map((col, index) => (
                  <div key={index} className={`column-item column-${col.type}`}>
                    <span className="column-icon">{col.icon}</span>
                    <span className="column-name">{col.name}</span>
                    <span className="column-type">
                      {col.type === 'protected' && 'Protected Attribute'}
                      {col.type === 'proxy' && 'Proxy Variable'}
                      {col.type === 'normal' && 'Normal Feature'}
                      {col.type === 'result' && 'Result Column'}
                    </span>
                  </div>
                ))}
              </div>

              <div className="result-selection">
                <label>Select Result Column:</label>
                <select 
                  value={resultColumn} 
                  onChange={(e) => setResultColumn(e.target.value)}
                  className="result-select"
                >
                  {csvColumns.map((col, index) => (
                    <option key={index} value={col.name}>{col.name}</option>
                  ))}
                </select>
              </div>

              <div className="auto-calculate">
                <button className="btn-calculate">
                  🔍 Auto-Calculate DI for All Protected Attributes
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="section-divider">
          <span>OR</span>
        </div>

        {/* Section B: Manual Input */}
        <div className="form-section">
          <h2>Section B: Manual Input</h2>

          {/* Gender (Fixed) */}
          <div className="manual-subsection">
            <h3>Gender</h3>
            <div className="gender-inputs">
              <div className="input-row">
                <span className="row-label">Male:</span>
                <input
                  type="number"
                  placeholder="Total applicants"
                  value={genderData.male.total}
                  onChange={(e) => setGenderData({
                    ...genderData,
                    male: { ...genderData.male, total: e.target.value }
                  })}
                  className="input-field"
                />
                <input
                  type="number"
                  placeholder="Approved"
                  value={genderData.male.approved}
                  onChange={(e) => setGenderData({
                    ...genderData,
                    male: { ...genderData.male, approved: e.target.value }
                  })}
                  className="input-field"
                />
                <span className="rate-display">
                  → {calculateRate(genderData.male.approved, genderData.male.total)}%
                </span>
              </div>

              <div className="input-row">
                <span className="row-label">Female:</span>
                <input
                  type="number"
                  placeholder="Total applicants"
                  value={genderData.female.total}
                  onChange={(e) => setGenderData({
                    ...genderData,
                    female: { ...genderData.female, total: e.target.value }
                  })}
                  className="input-field"
                />
                <input
                  type="number"
                  placeholder="Approved"
                  value={genderData.female.approved}
                  onChange={(e) => setGenderData({
                    ...genderData,
                    female: { ...genderData.female, approved: e.target.value }
                  })}
                  className="input-field"
                />
                <span className="rate-display">
                  → {calculateRate(genderData.female.approved, genderData.female.total)}%
                </span>
              </div>

              {di && (
                <div className={`di-result ${diStatus.class}`}>
                  <strong>DI = {di}</strong>
                  <span className="di-status">{diStatus.icon} {diStatus.label}</span>
                </div>
              )}
            </div>
          </div>

          {/* Ethnic Group (Flexible) */}
          <div className="manual-subsection">
            <h3>Ethnic Group</h3>
            {ethnicGroups.map((group, index) => (
              <div key={index} className="input-row">
                <input
                  type="text"
                  placeholder="Group name"
                  value={group.name}
                  onChange={(e) => updateEthnicGroup(index, 'name', e.target.value)}
                  className="input-field input-name"
                />
                <input
                  type="number"
                  placeholder="Total"
                  value={group.total}
                  onChange={(e) => updateEthnicGroup(index, 'total', e.target.value)}
                  className="input-field"
                />
                <input
                  type="number"
                  placeholder="Approved"
                  value={group.approved}
                  onChange={(e) => updateEthnicGroup(index, 'approved', e.target.value)}
                  className="input-field"
                />
                <span className="rate-display">
                  → {calculateRate(group.approved, group.total)}%
                </span>
                {ethnicGroups.length > 1 && (
                  <button
                    onClick={() => removeEthnicGroup(index)}
                    className="btn-delete"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button onClick={addEthnicGroup} className="btn-add-row">
              + Add Group
            </button>
          </div>

          {/* Zip Code (Flexible) */}
          <div className="manual-subsection">
            <h3>Zip Code</h3>
            {zipCodes.map((zip, index) => (
              <div key={index} className="input-row">
                <input
                  type="text"
                  placeholder="Zip code or area"
                  value={zip.name}
                  onChange={(e) => updateZipCode(index, 'name', e.target.value)}
                  className="input-field input-name"
                />
                <input
                  type="number"
                  placeholder="Total"
                  value={zip.total}
                  onChange={(e) => updateZipCode(index, 'total', e.target.value)}
                  className="input-field"
                />
                <input
                  type="number"
                  placeholder="Approved"
                  value={zip.approved}
                  onChange={(e) => updateZipCode(index, 'approved', e.target.value)}
                  className="input-field"
                />
                <span className="rate-display">
                  → {calculateRate(zip.approved, zip.total)}%
                </span>
                {zipCodes.length > 1 && (
                  <button
                    onClick={() => removeZipCode(index)}
                    className="btn-delete"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button onClick={addZipCode} className="btn-add-row">
              + Add Area
            </button>
          </div>
        </div>

        <div className="form-actions">
          <button onClick={handleGenerateReport} className="btn-generate-report">
            📄 Generate Audit Report (PDF)
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuditForm;

// Made with Bob
