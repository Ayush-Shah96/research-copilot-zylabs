/**
 * Layout component with header and main content area
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, X } from 'lucide-react';
import '../styles/layout.css';

function Layout({ children, error, setError }) {
  return (
    <div className="layout">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <Link to="/" className="logo">
            <span className="logo-icon">🔍</span>
            <span className="logo-text">Research Copilot</span>
          </Link>
          
          <nav className="nav">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/create" className="nav-link primary">
              + New Research
            </Link>
          </nav>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <div className="error-content">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
          <button
            className="error-close"
            onClick={() => setError(null)}
          >
            <X size={20} />
          </button>
        </div>
      )}

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>
          AI Research Copilot • Built with React & FastAPI •{' '}
          <a href="#" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}

export default Layout;
