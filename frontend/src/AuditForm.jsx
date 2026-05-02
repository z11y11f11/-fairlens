import React, { useState } from 'react';

/* global XLSX */

const AuditForm = () => {
  // CSV upload state
  const [csvFile, setCsvFile] = useState(null);
  const [csvColumns, setCsvColumns] = useState([]);
  const [csvData, setCsvData] = useState(null);
  const [resultColumn, setResultColumn] = useState('');
  const [selectedProtectedAttrs, setSelectedProtectedAttrs] = useState([]);
  const [csvPreview, setCsvPreview] = useState([]);
  
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

  // Validation errors state
  const [validationErrors, setValidationErrors] = useState({
    male: false,
    female: false,
    ethnicGroups: [],
    zipCodes: []
  });

  // Validation helper
  const validateInput = (approved, total) => {
    const approvedNum = parseFloat(approved);
    const totalNum = parseFloat(total);
    if (approved && total && approvedNum > totalNum) {
      return true; // Error: approved > total
    }
    return false;
  };

  // Calculate rate and DI
  const calculateRate = (approved, total) => {
    if (!approved || !total || total === 0) return 0;
    return (parseFloat(approved) / parseFloat(total) * 100).toFixed(1);
  };

  const calculateDI = () => {
    const maleRate = parseFloat(genderData.male.approved) / parseFloat(genderData.male.total);
    const femaleRate = parseFloat(genderData.female.approved) / parseFloat(genderData.female.total);
    
    if (!maleRate || !femaleRate) return null;
    
    // BUG FIX: Always calculate DI = lower_rate / higher_rate (must be 0-1.0)
    const lowerRate = Math.min(maleRate, femaleRate);
    const higherRate = Math.max(maleRate, femaleRate);
    
    if (higherRate === 0) return null;
    
    const di = lowerRate / higherRate;
    return di.toFixed(2);
  };

  // Check if there are any validation errors
  const hasValidationErrors = () => {
    return validationErrors.male ||
           validationErrors.female ||
           validationErrors.ethnicGroups.some(e => e) ||
           validationErrors.zipCodes.some(e => e);
  };

  const getDIStatus = (di) => {
    if (!di) return null;
    if (di >= 0.8) return { icon: '🟢', label: 'COMPLIANT', class: 'status-compliant' };
    if (di >= 0.7) return { icon: '🟡', label: 'WARNING', class: 'status-warning' };
    return { icon: '🔴', label: 'VIOLATION', class: 'status-violation' };
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setCsvFile(file);
    
    // Detect file type
    const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls');
    
    const reader = new FileReader();
    
    if (isExcel) {
      // Parse Excel file using SheetJS
      reader.onload = async (event) => {
        try {
          const data = new Uint8Array(event.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          
          // Get first sheet
          const firstSheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheetName];
          
          // Convert to JSON (array of arrays)
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
          
          if (jsonData.length < 2) {
            alert('Excel file must have at least a header row and one data row');
            return;
          }
          
          // First row is headers
          const headers = jsonData[0].map(h => String(h).trim());
          
          // Parse first 5 data rows for preview
          const previewRows = [];
          for (let i = 1; i < Math.min(6, jsonData.length); i++) {
            const row = {};
            headers.forEach((header, idx) => {
              row[header] = jsonData[i][idx] !== undefined ? String(jsonData[i][idx]) : '';
            });
            previewRows.push(row);
          }
          
          setCsvPreview(previewRows);
          
          // Detect column types (same logic as CSV)
          const detectedColumns = headers.map(colName => {
            const lowerName = colName.toLowerCase();
            
            // Check if it's a result column (0/1 values)
            const isResult = previewRows.every(row => {
              const val = row[colName];
              return val === '0' || val === '1' || val === 0 || val === 1 || val === '';
            });
            
            // Detect protected attributes
            if (lowerName.includes('gender') || lowerName.includes('sex')) {
              return { name: colName, type: 'protected', icon: '🔴', label: 'Protected Attribute' };
            } else if (lowerName.includes('race') || lowerName.includes('ethnicity') || lowerName.includes('ethnic')) {
              return { name: colName, type: 'protected', icon: '🔴', label: 'Protected Attribute' };
            } else if (lowerName.includes('age')) {
              return { name: colName, type: 'protected', icon: '🔴', label: 'Protected Attribute' };
            } else if (lowerName.includes('zip') || lowerName.includes('postal') || lowerName.includes('zipcode')) {
              return { name: colName, type: 'proxy', icon: '🟡', label: 'Proxy Variable' };
            } else if (isResult && (lowerName.includes('approved') || lowerName.includes('outcome') || lowerName.includes('result'))) {
              return { name: colName, type: 'result', icon: '🎯', label: 'Result Column' };
            } else {
              return { name: colName, type: 'normal', icon: '✅', label: 'Normal Feature' };
            }
          });
          
          setCsvColumns(detectedColumns);
          
          // Auto-select result column
          const resultCols = detectedColumns.filter(col => col.type === 'result');
          if (resultCols.length > 0) {
            setResultColumn(resultCols[0].name);
          } else {
            // If no result column detected, select first column with 0/1 values
            const binaryCol = detectedColumns.find(col => {
              return previewRows.every(row => {
                const val = row[col.name];
                return val === '0' || val === '1' || val === 0 || val === 1 || val === '';
              });
            });
            if (binaryCol) {
              setResultColumn(binaryCol.name);
            }
          }
          
          // Auto-select protected attributes
          const protectedCols = detectedColumns
            .filter(col => col.type === 'protected')
            .map(col => col.name);
          setSelectedProtectedAttrs(protectedCols);
          
        } catch (error) {
          console.error('Error parsing Excel file:', error);
          alert('Error parsing Excel file. Please ensure it is a valid .xlsx or .xls file.');
        }
      };
      
      reader.readAsArrayBuffer(file);
      
    } else {
      // Parse CSV file (original logic)
      reader.onload = async (event) => {
        const text = event.target.result;
        const lines = text.split('\n').filter(line => line.trim());
        
        if (lines.length < 2) {
          alert('CSV file must have at least a header row and one data row');
          return;
        }
        
        // Parse header
        const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
        
        // Parse first 5 data rows for preview
        const previewRows = [];
        for (let i = 1; i < Math.min(6, lines.length); i++) {
          const values = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''));
          const row = {};
          headers.forEach((header, idx) => {
            row[header] = values[idx] || '';
          });
          previewRows.push(row);
        }
        
        setCsvPreview(previewRows);
      
      // Detect column types
      const detectedColumns = headers.map(colName => {
        const lowerName = colName.toLowerCase();
        
        // Check if it's a result column (0/1 values)
        const isResult = previewRows.every(row => {
          const val = row[colName];
          return val === '0' || val === '1' || val === 0 || val === 1 || val === '';
        });
        
        // Detect protected attributes
        if (lowerName.includes('gender') || lowerName.includes('sex')) {
          return { name: colName, type: 'protected', icon: '🔴', label: 'Protected Attribute' };
        } else if (lowerName.includes('race') || lowerName.includes('ethnicity') || lowerName.includes('ethnic')) {
          return { name: colName, type: 'protected', icon: '🔴', label: 'Protected Attribute' };
        } else if (lowerName.includes('age')) {
          return { name: colName, type: 'protected', icon: '🔴', label: 'Protected Attribute' };
        } else if (lowerName.includes('zip') || lowerName.includes('postal') || lowerName.includes('zipcode')) {
          return { name: colName, type: 'proxy', icon: '🟡', label: 'Proxy Variable' };
        } else if (isResult && (lowerName.includes('approved') || lowerName.includes('outcome') || lowerName.includes('result'))) {
          return { name: colName, type: 'result', icon: '🎯', label: 'Result Column' };
        } else {
          return { name: colName, type: 'normal', icon: '✅', label: 'Normal Feature' };
        }
      });
      
      setCsvColumns(detectedColumns);
      
      // Auto-select result column
      const resultCols = detectedColumns.filter(col => col.type === 'result');
      if (resultCols.length > 0) {
        setResultColumn(resultCols[0].name);
      } else {
        // If no result column detected, select first column with 0/1 values
        const binaryCol = detectedColumns.find(col => {
          return previewRows.every(row => {
            const val = row[col.name];
            return val === '0' || val === '1' || val === 0 || val === 1 || val === '';
          });
        });
        if (binaryCol) {
          setResultColumn(binaryCol.name);
        }
      }
      
      // Auto-select protected attributes
      const protectedCols = detectedColumns
        .filter(col => col.type === 'protected')
        .map(col => col.name);
      setSelectedProtectedAttrs(protectedCols);
      };
      
      reader.readAsText(file);
    }
  };

  const toggleProtectedAttr = (attrName) => {
    if (selectedProtectedAttrs.includes(attrName)) {
      setSelectedProtectedAttrs(selectedProtectedAttrs.filter(a => a !== attrName));
    } else {
      setSelectedProtectedAttrs([...selectedProtectedAttrs, attrName]);
    }
  };

  const handleCsvGenerateReport = async () => {
    if (!csvFile) {
      alert('Please upload a CSV file first');
      return;
    }
    
    if (!resultColumn) {
      alert('Please select a result column');
      return;
    }
    
    if (selectedProtectedAttrs.length === 0) {
      alert('Please select at least one protected attribute to analyze');
      return;
    }
    
    try {
      // Show loading state
      const button = document.querySelector('.btn-csv-generate');
      const originalText = button.textContent;
      button.textContent = '⏳ Analyzing CSV data...';
      button.disabled = true;
      
      // Prepare form data
      const formData = new FormData();
      formData.append('file', csvFile);
      formData.append('result_column', resultColumn);
      formData.append('protected_attributes', JSON.stringify(selectedProtectedAttrs));
      
      // Send POST request to backend
      const response = await fetch('http://localhost:5001/api/audit/csv', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (response.ok && result.status === 'success') {
        // Success - trigger PDF download
        const pdfUrl = `http://localhost:5001${result.files.pdf_url}`;
        
        // Create temporary link and trigger download
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = result.files.pdf_filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Build results summary
        let resultsSummary = `✅ CSV Audit Report Generated!\n\n`;
        resultsSummary += `Audit ID: ${result.audit_id}\n`;
        resultsSummary += `File: ${result.file_info.filename} (${result.file_info.rows} rows)\n`;
        resultsSummary += `Overall Risk: ${result.risk_summary.overall_risk_level}\n`;
        resultsSummary += `DI Ratio: ${result.risk_summary.disparate_impact_ratio.toFixed(3)}\n\n`;
        resultsSummary += `Protected Attributes Analyzed:\n`;
        
        for (const [attr, data] of Object.entries(result.risk_summary.results)) {
          resultsSummary += `\n${attr}: ${data.risk_level}\n`;
          resultsSummary += `  DI = ${data.di_ratio.toFixed(3)}\n`;
          resultsSummary += `  ${data.interpretation}\n`;
        }
        
        resultsSummary += `\nPDF downloaded: ${result.files.pdf_filename}`;
        
        alert(resultsSummary);
      } else {
        // Error from backend
        alert(`❌ Error: ${result.error || 'Failed to generate report'}`);
      }
      
      // Restore button
      button.textContent = originalText;
      button.disabled = false;
      
    } catch (error) {
      console.error('Error generating CSV report:', error);
      alert(`❌ Network Error: ${error.message}\n\nMake sure the backend is running on http://localhost:5001`);
      
      // Restore button
      const button = document.querySelector('.btn-csv-generate');
      if (button) {
        button.textContent = '📄 Generate Audit Report (PDF)';
        button.disabled = false;
      }
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
    
    // Validate if updating total or approved
    if (field === 'total' || field === 'approved') {
      const approved = field === 'approved' ? value : updated[index].approved;
      const total = field === 'total' ? value : updated[index].total;
      const errors = [...validationErrors.ethnicGroups];
      errors[index] = validateInput(approved, total);
      setValidationErrors({
        ...validationErrors,
        ethnicGroups: errors
      });
    }
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
    
    // Validate if updating total or approved
    if (field === 'total' || field === 'approved') {
      const approved = field === 'approved' ? value : updated[index].approved;
      const total = field === 'total' ? value : updated[index].total;
      const errors = [...validationErrors.zipCodes];
      errors[index] = validateInput(approved, total);
      setValidationErrors({
        ...validationErrors,
        zipCodes: errors
      });
    }
  };

  const handleGenerateReport = async () => {
    // Validate gender data
    if (!genderData.male.total || !genderData.male.approved ||
        !genderData.female.total || !genderData.female.approved) {
      alert('Please fill in all gender data fields (Male and Female totals and approved counts)');
      return;
    }

    // Prepare payload
    const payload = {
      gender: {
        male_total: parseFloat(genderData.male.total),
        male_approved: parseFloat(genderData.male.approved),
        female_total: parseFloat(genderData.female.total),
        female_approved: parseFloat(genderData.female.approved)
      },
      ethnic_groups: ethnicGroups
        .filter(g => g.name && g.total && g.approved)
        .map(g => ({
          name: g.name,
          total: parseFloat(g.total),
          approved: parseFloat(g.approved)
        })),
      zip_codes: zipCodes
        .filter(z => z.name && z.total && z.approved)
        .map(z => ({
          name: z.name,
          total: parseFloat(z.total),
          approved: parseFloat(z.approved)
        }))
    };

    try {
      // Show loading state
      const button = document.querySelector('.btn-generate-report');
      const originalText = button.textContent;
      button.textContent = '⏳ Generating report...';
      button.disabled = true;

      // Send POST request to backend
      const response = await fetch('http://localhost:5001/api/audit/manual', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
        // Success - trigger PDF download
        const pdfUrl = `http://localhost:5001${result.files.pdf_url}`;
        
        // Create temporary link and trigger download
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = result.files.pdf_filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Show success message
        alert(
          `✅ Audit Report Generated!\n\n` +
          `Audit ID: ${result.audit_id}\n` +
          `DI Ratio: ${result.risk_summary.disparate_impact_ratio.toFixed(3)}\n` +
          `Risk Level: ${result.risk_summary.overall_risk_level}\n\n` +
          `PDF downloaded: ${result.files.pdf_filename}`
        );
      } else {
        // Error from backend
        alert(`❌ Error: ${result.error || 'Failed to generate report'}`);
      }

      // Restore button
      button.textContent = originalText;
      button.disabled = false;

    } catch (error) {
      console.error('Error generating report:', error);
      alert(`❌ Network Error: ${error.message}\n\nMake sure the backend is running on http://localhost:5001`);
      
      // Restore button
      const button = document.querySelector('.btn-generate-report');
      button.textContent = '📄 Generate Audit Report (PDF)';
      button.disabled = false;
    }
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
        {/* Section A: Upload CSV/Excel - Complete Standalone Workflow */}
        <div className="form-section">
          <h2>Section A: Upload Data File</h2>
          
          {/* STEP 1: Upload & Column Detection */}
          <div className="csv-step">
            <h3>Step 1: Upload & Column Detection</h3>
            <div className="upload-instructions">
              <p><strong>Upload your loan data file. Required columns:</strong></p>
              <ul>
                <li>A result column (e.g. loan_approved): values must be 0 or 1</li>
                <li>At least one protected attribute column:
                  <ul>
                    <li>gender (Male/Female), ethnicity, zip_code, race, age</li>
                  </ul>
                </li>
                <li>Optional: applicant_name, income, loan_amount</li>
              </ul>
            </div>
            
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
              {csvFile && <div className="file-name">✓ Selected: {csvFile.name}</div>}
            </div>

            {csvColumns.length > 0 && (
              <div className="csv-analysis">
                <h4>Detected Columns:</h4>
                <div className="columns-list">
                  {csvColumns.map((col, index) => (
                    <div key={index} className={`column-item column-${col.type}`}>
                      <span className="column-icon">{col.icon}</span>
                      <span className="column-name">{col.name}</span>
                      <span className="column-type">{col.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* STEP 2: Select Columns for Analysis */}
          {csvColumns.length > 0 && (
            <div className="csv-step">
              <h3>Step 2: Select Columns for Analysis</h3>
              
              <div className="column-selection">
                <div className="selection-group">
                  <label><strong>Select Result Column:</strong></label>
                  <select
                    value={resultColumn}
                    onChange={(e) => setResultColumn(e.target.value)}
                    className="result-select"
                  >
                    <option value="">-- Select Result Column --</option>
                    {csvColumns.map((col, index) => (
                      <option key={index} value={col.name}>
                        {col.icon} {col.name}
                      </option>
                    ))}
                  </select>
                  <small>Only columns with 0/1 values should be selected</small>
                </div>

                <div className="selection-group">
                  <label><strong>Select Protected Attributes to Analyze:</strong></label>
                  <div className="checkbox-group">
                    {csvColumns
                      .filter(col => col.type === 'protected' || col.type === 'proxy')
                      .map((col, index) => (
                        <label key={index} className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={selectedProtectedAttrs.includes(col.name)}
                            onChange={() => toggleProtectedAttr(col.name)}
                          />
                          <span>{col.icon} {col.name}</span>
                        </label>
                      ))}
                  </div>
                  {selectedProtectedAttrs.length === 0 && (
                    <small style={{color: 'orange'}}>⚠️ Please select at least one protected attribute</small>
                  )}
                </div>
              </div>

              {/* Data Preview */}
              {csvPreview.length > 0 && (
                <div className="data-preview">
                  <h4>Data Preview (first 5 rows):</h4>
                  <div className="preview-table-container">
                    <table className="preview-table">
                      <thead>
                        <tr>
                          {Object.keys(csvPreview[0]).map((header, idx) => (
                            <th key={idx}>{header}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {csvPreview.map((row, rowIdx) => (
                          <tr key={rowIdx}>
                            {Object.values(row).map((value, colIdx) => (
                              <td key={colIdx}>{value}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* STEP 3: Generate Report */}
          {csvColumns.length > 0 && (
            <div className="csv-step">
              <h3>Step 3: Generate Report</h3>
              <button
                onClick={handleCsvGenerateReport}
                className="btn-csv-generate btn-generate-report"
                disabled={!resultColumn || selectedProtectedAttrs.length === 0}
                style={{
                  opacity: (!resultColumn || selectedProtectedAttrs.length === 0) ? 0.5 : 1,
                  cursor: (!resultColumn || selectedProtectedAttrs.length === 0) ? 'not-allowed' : 'pointer'
                }}
              >
                📄 Generate Audit Report (PDF)
              </button>
              {(!resultColumn || selectedProtectedAttrs.length === 0) && (
                <p style={{color: 'orange', marginTop: '10px'}}>
                  ⚠️ Please complete Step 2 before generating report
                </p>
              )}
            </div>
          )}
        </div>

        {/* Visual Divider */}
        <div className="section-divider">
          <span>── OR ──</span>
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
                  onChange={(e) => {
                    const newTotal = e.target.value;
                    setGenderData({
                      ...genderData,
                      male: { ...genderData.male, total: newTotal }
                    });
                    setValidationErrors({
                      ...validationErrors,
                      male: validateInput(genderData.male.approved, newTotal)
                    });
                  }}
                  className="input-field"
                />
                <input
                  type="number"
                  placeholder="Approved"
                  value={genderData.male.approved}
                  onChange={(e) => {
                    const newApproved = e.target.value;
                    setGenderData({
                      ...genderData,
                      male: { ...genderData.male, approved: newApproved }
                    });
                    setValidationErrors({
                      ...validationErrors,
                      male: validateInput(newApproved, genderData.male.total)
                    });
                  }}
                  className="input-field"
                />
                <span className="rate-display">
                  → {calculateRate(genderData.male.approved, genderData.male.total)}%
                </span>
              </div>
              {validationErrors.male && (
                <div style={{ color: 'red', fontSize: '14px', marginLeft: '80px', marginTop: '5px' }}>
                  Error: Approved count cannot exceed total applicants
                </div>
              )}

              <div className="input-row">
                <span className="row-label">Female:</span>
                <input
                  type="number"
                  placeholder="Total applicants"
                  value={genderData.female.total}
                  onChange={(e) => {
                    const newTotal = e.target.value;
                    setGenderData({
                      ...genderData,
                      female: { ...genderData.female, total: newTotal }
                    });
                    setValidationErrors({
                      ...validationErrors,
                      female: validateInput(genderData.female.approved, newTotal)
                    });
                  }}
                  className="input-field"
                />
                <input
                  type="number"
                  placeholder="Approved"
                  value={genderData.female.approved}
                  onChange={(e) => {
                    const newApproved = e.target.value;
                    setGenderData({
                      ...genderData,
                      female: { ...genderData.female, approved: newApproved }
                    });
                    setValidationErrors({
                      ...validationErrors,
                      female: validateInput(newApproved, genderData.female.total)
                    });
                  }}
                  className="input-field"
                />
                <span className="rate-display">
                  → {calculateRate(genderData.female.approved, genderData.female.total)}%
                </span>
              </div>
              {validationErrors.female && (
                <div style={{ color: 'red', fontSize: '14px', marginLeft: '80px', marginTop: '5px' }}>
                  Error: Approved count cannot exceed total applicants
                </div>
              )}

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
              <div key={index}>
                <div className="input-row">
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
                {validationErrors.ethnicGroups[index] && (
                  <div style={{ color: 'red', fontSize: '14px', marginLeft: '150px', marginTop: '5px', marginBottom: '10px' }}>
                    Error: Approved count cannot exceed total applicants
                  </div>
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
              <div key={index}>
                <div className="input-row">
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
                {validationErrors.zipCodes[index] && (
                  <div style={{ color: 'red', fontSize: '14px', marginLeft: '150px', marginTop: '5px', marginBottom: '10px' }}>
                    Error: Approved count cannot exceed total applicants
                  </div>
                )}
              </div>
            ))}
            <button onClick={addZipCode} className="btn-add-row">
              + Add Area
            </button>
          </div>
        </div>

        <div className="form-actions">
          <button
            onClick={handleGenerateReport}
            className="btn-generate-report"
            disabled={hasValidationErrors()}
            style={{
              opacity: hasValidationErrors() ? 0.5 : 1,
              cursor: hasValidationErrors() ? 'not-allowed' : 'pointer'
            }}
          >
            📄 Generate Audit Report (PDF)
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuditForm;

// Made with Bob
