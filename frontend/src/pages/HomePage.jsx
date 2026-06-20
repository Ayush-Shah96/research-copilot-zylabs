/**
 * Home page showing list of research sessions and dashboard
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useSession } from '../hooks';
import { Calendar, Briefcase, ChevronRight, Clock } from 'lucide-react';
import '../styles/pages.css';

function HomePage() {
  const { sessions, loading, fetchSessions } = useSession();
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    running: 0,
    failed: 0,
  });

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  useEffect(() => {
    if (sessions.length > 0) {
      const newStats = {
        total: sessions.length,
        completed: sessions.filter(s => s.status === 'completed').length,
        running: sessions.filter(s => s.status === 'running').length,
        failed: sessions.filter(s => s.status === 'failed').length,
      };
      setStats(newStats);
    }
  }, [sessions]);

  const completedPercentage = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
  const recentSessions = sessions.slice(0, 6);

  if (loading && sessions.length === 0) {
    return (
      <div className="page">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading research sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      {/* Welcome Header */}
      <div className="page-header">
        <div>
          <h1>Research Dashboard</h1>
          <p>Automated company research for smarter sales</p>
        </div>
      </div>

      {/* Quick Action */}
      <div className="page-actions">
        <Link to="/create" className="btn btn-primary">
          <span>✨</span> Start New Research
        </Link>
      </div>

      {/* Stats Grid */}
      {sessions.length > 0 && (
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-label">Total Sessions</div>
            <div className="metric-value">{stats.total}</div>
            <div className="metric-change">All research projects</div>
          </div>

          <div className="metric-card">
            <div className="metric-label">Completed</div>
            <div className="metric-value" style={{ color: 'var(--success)' }}>
              {completedPercentage}%
            </div>
            <div className="metric-change">{stats.completed} of {stats.total}</div>
          </div>

          <div className="metric-card">
            <div className="metric-label">In Progress</div>
            <div className="metric-value" style={{ color: 'var(--primary-light)' }}>
              {stats.running}
            </div>
            <div className="metric-change">Currently running</div>
          </div>

          <div className="metric-card">
            <div className="metric-label">Failed</div>
            <div className="metric-value" style={{ color: 'var(--danger)' }}>
              {stats.failed}
            </div>
            <div className="metric-change">Need attention</div>
          </div>
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h2>No research sessions yet</h2>
          <p>Start your first company research to get insights for your sales meetings</p>
          <Link to="/create" className="btn btn-primary">
            Launch Your First Research
          </Link>
        </div>
      ) : (
        <>
          {/* Recent Sessions */}
          <div style={{ marginTop: 'var(--spacing-2xl)' }}>
            <h2 style={{ marginBottom: 'var(--spacing-lg)', color: 'var(--text)' }}>
              Recent Research
            </h2>
            <div className="sessions-grid">
              {recentSessions.map((session) => (
                <Link
                  key={session.id}
                  to={`/session/${session.id}`}
                  className="session-card"
                >
                  <div className="session-header">
                    <h3>{session.company_name}</h3>
                    <span className={`status status-${session.status}`}>
                      {session.status === 'completed' && '✓'}
                      {session.status === 'running' && '⟳'}
                      {session.status === 'pending' && '○'}
                      {session.status === 'failed' && '✕'}
                      {' '}
                      {session.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="session-content">
                    <p className="objective">{session.research_objective}</p>
                  </div>

                  <div className="session-meta">
                    <div className="meta-item">
                      <Calendar size={16} />
                      <span>
                        {new Date(session.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </span>
                    </div>
                    {session.company_website && (
                      <div className="meta-item">
                        <Briefcase size={16} />
                        <span className="website">{session.company_website}</span>
                      </div>
                    )}
                    <div className="meta-item">
                      <Clock size={16} />
                      <span>
                        {new Date(session.created_at).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                  </div>

                  <div className="session-action">
                    <ChevronRight size={20} />
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* View All Link */}
          {sessions.length > 6 && (
            <div style={{ textAlign: 'center', marginTop: 'var(--spacing-2xl)' }}>
              <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--spacing-lg)' }}>
                Showing {recentSessions.length} of {sessions.length} research sessions
              </p>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  const grid = document.querySelector('.sessions-grid');
                  if (grid) grid.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                View All Sessions
              </button>
            </div>
          )}
        </>
      )}

      {/* Features Info */}
      <div
        style={{
          marginTop: 'var(--spacing-2xl)',
          padding: 'var(--spacing-2xl)',
          background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.05), rgba(6, 182, 212, 0.05))',
          borderRadius: 'var(--radius-xl)',
          border: '1px solid var(--border)',
        }}
      >
        <h2 style={{ marginBottom: 'var(--spacing-lg)', color: 'var(--text)' }}>
          How It Works
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: 'var(--spacing-lg)',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-md)' }}>
              <div style={{ fontSize: '1.5rem' }}>🔍</div>
              <h3 style={{ margin: 0, color: 'var(--text)' }}>1. Create Session</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
              Enter company name and research objectives
            </p>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-md)' }}>
              <div style={{ fontSize: '1.5rem' }}>⚙️</div>
              <h3 style={{ margin: 0, color: 'var(--text)' }}>2. Run Workflow</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
              AI-powered research workflow executes automatically
            </p>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-md)' }}>
              <div style={{ fontSize: '1.5rem' }}>📊</div>
              <h3 style={{ margin: 0, color: 'var(--text)' }}>3. Get Insights</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
              Receive structured research report with actionable insights
            </p>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-md)' }}>
              <div style={{ fontSize: '1.5rem' }}>💬</div>
              <h3 style={{ margin: 0, color: 'var(--text)' }}>4. Ask Questions</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
              Follow-up chat with context-aware responses
            </p>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-md)' }}>
              <div style={{ fontSize: '1.5rem' }}>🎯</div>
              <h3 style={{ margin: 0, color: 'var(--text)' }}>5. Prepare</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
              Use insights to prepare for your meeting
            </p>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-md)' }}>
              <div style={{ fontSize: '1.5rem' }}>📈</div>
              <h3 style={{ margin: 0, color: 'var(--text)' }}>6. Win More Deals</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
              Close deals with better informed conversations
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;