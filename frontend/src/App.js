import React from 'react';
import AuditForm from './AuditForm';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>FairLens AI Audit System</h1>
          <p className="header-subtitle">EU AI Act Compliance Tool for High-Risk AI Systems</p>
        </div>
      </header>
      <main className="app-main">
        <AuditForm />
      </main>
      <footer className="app-footer">
        <p>&copy; 2026 FairLens AI Audit System | EU AI Act Article 6 Compliance</p>
      </footer>
    </div>
  );
}

export default App;

// Made with Bob
