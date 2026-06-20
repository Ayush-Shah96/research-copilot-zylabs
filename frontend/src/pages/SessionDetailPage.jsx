/**
 * Session detail page showing research progress and report
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSession, useWorkflow, useChat } from '../hooks';
import { Play, RotateCcw, ArrowLeft, Send, Zap } from 'lucide-react';
import '../styles/pages.css';

function SessionDetailPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { currentSession, fetchSessionDetail } = useSession();
  const { progress, startWorkflow, retryWorkflow } = useWorkflow();
  const { messages, sendMessage: sendChatMessage } = useChat(sessionId);
  const [loading, setLoading] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [progressInterval, setProgressInterval] = useState(null);

  useEffect(() => {
    const loadSession = async () => {
      try {
        await fetchSessionDetail(sessionId);
      } finally {
        setLoading(false);
      }
    };
    loadSession();
  }, [sessionId, fetchSessionDetail]);

  const handleStartWorkflow = async () => {
    try {
      await startWorkflow(sessionId);
      // Refresh session and progress periodically
      const interval = setInterval(() => {
        fetchSessionDetail(sessionId);
      }, 2000);
      setProgressInterval(interval);
    } catch (err) {
      alert('Failed to start workflow: ' + err.message);
    }
  };

  const handleRetry = async () => {
    try {
      await retryWorkflow(sessionId);
    } catch (err) {
      alert('Failed to retry: ' + err.message);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    try {
      await sendChatMessage(chatInput);
      setChatInput('');
    } catch (err) {
      alert('Failed to send message: ' + err.message);
    }
  };

  useEffect(() => {
    return () => {
      if (progressInterval) clearInterval(progressInterval);
    };
  }, [progressInterval]);

  if (loading) {
    return (
      <div className="page">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading session...</p>
        </div>
      </div>
    );
  }

  if (!currentSession) {
    return (
      <div className="page">
        <div className="error-state">
          <p>Session not found</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page session-detail">
      {/* Header */}
      <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/')}>
          <ArrowLeft size={24} />
        </button>
        <div style={{ flex: 1 }}>
          <h1>{currentSession.company_name}</h1>
          <p>{currentSession.research_objective}</p>
        </div>
        <span className={`status status-${currentSession.status}`}>
          {currentSession.status === 'completed' && '✓ Completed'}
          {currentSession.status === 'running' && '⟳ Running'}
          {currentSession.status === 'pending' && '○ Pending'}
          {currentSession.status === 'failed' && '✕ Failed'}
        </span>
      </div>

      {/* Main Content Grid */}
      <div className="session-grid">
        {/* Research Section */}
        <section className="section research-section">
          <h2>Research Workflow</h2>

          {currentSession.status === 'pending' && (
            <div className="research-ready">
              <Zap size={40} style={{ color: 'var(--primary)' }} />
              <p>Ready to launch research</p>
              <button
                className="btn btn-primary"
                onClick={handleStartWorkflow}
              >
                <Play size={18} />
                Start Research
              </button>
            </div>
          )}

          {currentSession.status === 'running' && (
            <div className="research-progress">
              <p style={{ textAlign: 'center', marginBottom: 'var(--spacing-md)' }}>
                {progress?.message || 'Processing research...'}
              </p>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: (progress?.progress_percentage || 0) + '%' }}
                ></div>
              </div>
              <div style={{ marginTop: 'var(--spacing-lg)', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                  Step {progress?.steps_completed || 0} of {progress?.total_steps || 5}
                </p>
              </div>
            </div>
          )}

          {currentSession.status === 'completed' && (
            <div className="research-complete">
              <span style={{ fontSize: '2rem' }}>✓</span>
              <p>Research completed successfully!</p>
            </div>
          )}

          {currentSession.status === 'failed' && (
            <div className="research-failed">
              <span style={{ fontSize: '2rem' }}>✕</span>
              <p>{currentSession.error_message}</p>
              <button
                className="btn btn-secondary"
                onClick={handleRetry}
              >
                <RotateCcw size={18} />
                Retry Research
              </button>
            </div>
          )}
        </section>

        {/* Report Section */}
        {currentSession.report && (
          <section className="section report-section">
            <h2>Research Report</h2>

            <div className="report-content">
              {currentSession.report.company_overview && (
                <div className="report-item">
                  <h3>Company Overview</h3>
                  <p>{currentSession.report.company_overview}</p>
                </div>
              )}

              {currentSession.report.products_services && (
                <div className="report-item">
                  <h3>Products & Services</h3>
                  <p>{currentSession.report.products_services}</p>
                </div>
              )}

              {currentSession.report.target_customers && (
                <div className="report-item">
                  <h3>Target Customers</h3>
                  <p>{currentSession.report.target_customers}</p>
                </div>
              )}

              {currentSession.report.business_signals && (
                <div className="report-item">
                  <h3>Business Signals</h3>
                  <p>{currentSession.report.business_signals}</p>
                </div>
              )}

              {currentSession.report.discovery_questions && currentSession.report.discovery_questions.length > 0 && (
                <div className="report-item">
                  <h3>Key Discovery Questions</h3>
                  <ul>
                    {currentSession.report.discovery_questions.slice(0, 3).map((q, i) => (
                      <li key={i}>
                        <strong>{q.question}</strong>
                        <small style={{ color: 'var(--text-secondary)', display: 'block', marginTop: '0.25rem' }}>
                          {q.priority && `Priority: ${q.priority}`}
                        </small>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Chat Section */}
        {currentSession.status === 'completed' && (
          <section className="section chat-section">
            <h2>Follow-Up Chat</h2>

            <div className="chat-messages">
              {messages.length === 0 ? (
                <p className="chat-empty">Ask questions about the research...</p>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id} className={`message message-${msg.role}`}>
                    <div className="message-role">{msg.role}</div>
                    <div className="message-content">{msg.content}</div>
                  </div>
                ))
              )}
            </div>

            <form onSubmit={handleSendMessage} className="chat-form">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask a question about the research findings..."
                disabled={loading}
              />
              <button type="submit" className="btn btn-primary" disabled={loading}>
                <Send size={18} />
              </button>
            </form>
          </section>
        )}
      </div>
    </div>
  );
}

export default SessionDetailPage;
