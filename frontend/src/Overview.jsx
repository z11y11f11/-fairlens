import React from 'react';

function Overview({ onNavigate }) {
  return (
    <div className="overview-container">
      {/* SECTION 1 - Hero Header */}
      <section className="hero-header">
        <h1 className="hero-title">FairLens AI Audit System</h1>
        <h2 className="hero-subtitle">AI Bias Accountability Platform for Financial Institutions</h2>
        <p className="hero-tagline">Powered by IBM AI Fairness 360 | EU AI Act Compliant | August 2026</p>
      </section>

      {/* SECTION 2 - What is FairLens? */}
      <section className="what-is-fairlens">
        <h2>What is FairLens?</h2>
        <p>
          FairLens helps financial institutions systematically detect discrimination risks in AI-powered credit decision models. 
          Generate standardized audit reports that demonstrate compliance with EU AI Act before its mandatory enforcement in August 2026.
        </p>
      </section>

      {/* SECTION 3 - Who is it for? */}
      <section className="who-is-it-for">
        <h2>Who is it for?</h2>
        <div className="cards-container">
          <div className="card">
            <div className="card-icon">👔</div>
            <h3>Chief Compliance Officer</h3>
            <p>Monitor real-time bias alerts and generate regulatory reports</p>
          </div>
          <div className="card">
            <div className="card-icon">🔬</div>
            <h3>AI & Model Risk Team</h3>
            <p>Analyze fairness metrics and track bias trends over time</p>
          </div>
          <div className="card">
            <div className="card-icon">🏛️</div>
            <h3>Regulators & Auditors</h3>
            <p>Review compliance status against EU AI Act, ECOA and GDPR</p>
          </div>
        </div>
      </section>

      {/* SECTION 4 - How to Use */}
      <section className="how-to-use">
        <h2>How to Use</h2>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-icon">🚨</div>
            <h3>Alert Center</h3>
            <p>
              View real-time bias alerts from your institution's AI systems.
              Monitor which features triggered violations.
            </p>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-icon">📊</div>
            <h3>Dashboard</h3>
            <p>
              Analyze historical bias trends by period and feature type.
              Track Gender, Zip Code and Ethnic Group disparities over time.
            </p>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-icon">📋</div>
            <h3>Audit</h3>
            <p>
              Upload CSV/Excel data or manually input group statistics.
              System calculates Disparate Impact and generates PDF report.
              Supported formats: .csv .xlsx
            </p>
          </div>
          <div className="step">
            <div className="step-number">4</div>
            <div className="step-icon">⚖️</div>
            <h3>Regulations</h3>
            <p>
              Compare audit results against EU AI Act, ECOA and GDPR.
              View specific violations and recommended fixes.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 5 - Key Stats */}
      <section className="key-stats">
        <h2>Key Statistics</h2>
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-value">4/5 Rule</div>
            <div className="stat-label">Legal DI Threshold</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">Aug 2026</div>
            <div className="stat-label">EU AI Act Deadline</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">70+</div>
            <div className="stat-label">Fairness Metrics</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">HIGH RISK</div>
            <div className="stat-label">Credit AI Classification</div>
          </div>
        </div>
      </section>

      {/* SECTION 6 - Regulatory Badges */}
      <section className="regulatory-badges">
        <div className="badges-container">
          <span className="badge">EU AI Act</span>
          <span className="badge-separator">|</span>
          <span className="badge">ECOA</span>
          <span className="badge-separator">|</span>
          <span className="badge">GDPR</span>
          <span className="badge-separator">|</span>
          <span className="badge">FCRA</span>
          <span className="badge-separator">|</span>
          <span className="badge">IBM AIF360</span>
        </div>
      </section>

      {/* SECTION 7 - CTA Buttons */}
      <section className="cta-section">
        <button className="cta-button cta-primary" onClick={() => onNavigate(3)}>
          Start Audit →
        </button>
        <button className="cta-button cta-secondary" onClick={() => onNavigate(1)}>
          View Alerts →
        </button>
      </section>
    </div>
  );
}

export default Overview;

// Made with Bob
