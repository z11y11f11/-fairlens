import React, { useState } from 'react';
import AlertCenter from './AlertCenter';
import Dashboard from './Dashboard';
import AuditForm from './AuditForm';
import Regulations from './Regulations';

function App() {
  const [currentPage, setCurrentPage] = useState('alert');

  const renderPage = () => {
    switch (currentPage) {
      case 'alert':
        return <AlertCenter />;
      case 'dashboard':
        return <Dashboard />;
      case 'audit':
        return <AuditForm />;
      case 'regulations':
        return <Regulations />;
      default:
        return <AlertCenter />;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>FairLens AI Audit System</h1>
          <p className="header-subtitle">EU AI Act Compliance Tool for High-Risk AI Systems</p>
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-tab ${currentPage === 'alert' ? 'active' : ''}`}
          onClick={() => setCurrentPage('alert')}
        >
          <span className="nav-icon">🚨</span>
          <span className="nav-label">Alert Center</span>
        </button>
        <button
          className={`nav-tab ${currentPage === 'dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentPage('dashboard')}
        >
          <span className="nav-icon">📊</span>
          <span className="nav-label">Dashboard</span>
        </button>
        <button
          className={`nav-tab ${currentPage === 'audit' ? 'active' : ''}`}
          onClick={() => setCurrentPage('audit')}
        >
          <span className="nav-icon">📋</span>
          <span className="nav-label">Audit</span>
        </button>
        <button
          className={`nav-tab ${currentPage === 'regulations' ? 'active' : ''}`}
          onClick={() => setCurrentPage('regulations')}
        >
          <span className="nav-icon">⚖️</span>
          <span className="nav-label">Regulations</span>
        </button>
      </nav>

      <main className="app-main">
        {renderPage()}
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 FairLens AI Audit System | EU AI Act Article 6 Compliance</p>
      </footer>
    </div>
  );
}

export default App;

// Made with Bob
