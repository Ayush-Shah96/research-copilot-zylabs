/**
 * Page for creating a new research session
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../hooks';
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
      <div className="page-header">
        <h1>Start New Research</h1>
        <p>Begin your company research journey</p>
      </div>

      <div className="form-container">
        <form onSubmit={handleSubmit} className="form">
          {error && <div className="form-error">{error}</div>}

          <div className="form-group">
            <label htmlFor="company_name">Company Name *</label>
            <input
              type="text"
              id="company_name"
              name="company_name"
              value={formData.company_name}
              onChange={handleChange}
              placeholder="e.g., Acme Corporation"
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
            <small>Optional - helps provide more context</small>
          </div>

          <div className="form-group">
            <label htmlFor="research_objective">Research Objective *</label>
            <textarea
              id="research_objective"
              name="research_objective"
              value={formData.research_objective}
              onChange={handleChange}
              placeholder="What do you want to learn about this company? E.g., 'Understand their product roadmap and market position for partnership discussion'"
              rows={5}
              disabled={loading}
              required
            />
            <small>Describe your research goals and what insights you need</small>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Start Research'}
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
      </div>
    </div>
  );
}

export default SessionCreatePage;
