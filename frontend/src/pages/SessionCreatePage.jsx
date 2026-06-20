/**
 * Page for creating a new research session
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../hooks';
import { ArrowLeft, Sparkles } from 'lucide-react';
import '../styles/pages.css';

function SessionCreatePage() {
  const navigate = useNavigate();
  const { createSession, loading } = useSession();
  const [formData, setFormData] = useState({
    company_name: '',
    company_website: '',
    research_objective: '',
  });
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!formData.company_name.trim()) {
      setError('Company name is required');
      return;
    }

    if (!formData.research_objective.trim()) {
      setError('Research objective is required');
      return;
    }

    try {
      const session = await createSession(formData);
      navigate(`/session/${session.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create session');
    }
  };

  return (
    <div className="page">
      <button className="btn-back" onClick={() => navigate('/')} style={{ marginBottom: 'var(--spacing-xl)' }}>
        <ArrowLeft size={20} />
      </button>

      <div className="page-header">
        <div>
          <h1>Start New Research</h1>
          <p>Let AI help you prepare for your next important meeting</p>
        </div>
      </div>

      <div className="form-container">
        <form onSubmit={handleSubmit} className="form">
          {error && <div className="form-error">{error}</div>}

          <div className="form-group">
            <label htmlFor="company_name">
              <Sparkles size={18} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Company Name <span style={{ color: 'var(--danger)' }}>*</span>
            </label>
            <input
              type="text"
              id="company_name"
              name="company_name"
              value={formData.company_name}
              onChange={handleChange}
              placeholder="e.g., Acme Corporation, TechStartup Inc."
              disabled={loading}
              required
            />
            <small>The company you want to research</small>
          </div>

          <div className="form-group">
            <label htmlFor="company_website">Company Website</label>
            <input
              type="url"
              id="company_website"
              name="company_website"
              value={formData.company_website}
              onChange={handleChange}
              placeholder="https://example.com"
              disabled={loading}
            />
            <small>Optional - helps provide more context and sources</small>
          </div>

          <div className="form-group">
            <label htmlFor="research_objective">
              Research Objective <span style={{ color: 'var(--danger)' }}>*</span>
            </label>
            <textarea
              id="research_objective"
              name="research_objective"
              value={formData.research_objective}
              onChange={handleChange}
              placeholder="What do you want to learn about this company? E.g., 'Understand their product roadmap and market position for a partnership discussion' or 'Identify their pain points in customer success management'"
              rows={5}
              disabled={loading}
              required
            />
            <small>Describe your research goals and what insights you need for your meeting</small>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></span>
                  Creating...
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  Start Research
                </>
              )}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/')}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>

        {/* Info Box */}
        <div
          style={{
            marginTop: 'var(--spacing-2xl)',
            padding: 'var(--spacing-lg)',
            background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.05), rgba(6, 182, 212, 0.05))',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border)',
            color: 'var(--text-secondary)',
            fontSize: '0.9rem',
          }}
        >
          <p style={{ margin: 0, marginBottom: 'var(--spacing-sm)' }}>
            <strong>💡 Tip:</strong> The more specific your research objective, the better the insights.
          </p>
          <p style={{ margin: 0 }}>
            <strong>⏱️ Duration:</strong> Research typically takes 2-5 minutes depending on available data.
          </p>
        </div>
      </div>
    </div>
  );
}

export default SessionCreatePage;
