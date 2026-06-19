/**
 * Home page showing list of research sessions
 */

import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useSession } from '../hooks';
import { Calendar, Briefcase, ChevronRight } from 'lucide-react';
import '../styles/pages.css';

function HomePage() {
  const { sessions, loading, fetchSessions } = useSession();

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  if (loading) {
    return (
      <div className="page">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Research Sessions</h1>
        <p>Track and manage your company research projects</p>
      </div>

      <div className="page-actions">
        <Link to="/create" className="btn btn-primary">
          + Start New Research
        </Link>
      </div>

      {sessions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h2>No research sessions yet</h2>
          <p>Create your first research session to get started</p>
          <Link to="/create" className="btn btn-primary">
            Start Your First Research
          </Link>
        </div>
      ) : (
        <div className="sessions-grid">
          {sessions.map((session) => (
            <Link
              key={session.id}
              to={`/session/${session.id}`}
              className="session-card"
            >
              <div className="session-header">
                <h3>{session.company_name}</h3>
                <span className={`status status-${session.status}`}>
                  {session.status}
                </span>
              </div>

              <div className="session-content">
                <p className="objective">{session.research_objective}</p>
              </div>

              <div className="session-meta">
                <div className="meta-item">
                  <Calendar size={16} />
                  <span>{new Date(session.created_at).toLocaleDateString()}</span>
                </div>
                {session.company_website && (
                  <div className="meta-item">
                    <Briefcase size={16} />
                    <span className="website">{session.company_website}</span>
                  </div>
                )}
              </div>

              <div className="session-action">
                <ChevronRight size={20} />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default HomePage;
