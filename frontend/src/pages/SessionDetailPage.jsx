/**
 * Session detail page showing research progress and report
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSession, useWorkflow, useChat } from '../hooks';
import { Play, RotateCcw, ArrowLeft } from 'lucide-react';
import '../styles/pages.css';

function SessionDetailPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { currentSession, fetchSessionDetail } = useSession();
  const { progress, startWorkflow, retryWorkflow } = useWorkflow();
  const { messages, sendMessage: sendChatMessage } = useChat(sessionId);
  const [loading, setLoading] = useState(true);
  const [chatInput, setChatInput] = useState('');

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
      return () => clearInterval(interval);
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
            Back to Home
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
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1>{currentSession.company_name}</h1>
          <p>{currentSession.research_objective}</p>
        </div>
        <span className={`status status-${currentSession.status}`}>
          {currentSession.status}
        </span>
      </div>

      {/* Main Content Grid */}
      <div className="session-grid">
        {/* Research Section */}
        <section className="section research-section">
          <h2>Research Progress</h2>

          {currentSession.status === 'pending' && (
            <div className="research-ready">
              <p>Ready to start research</p>
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
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: progress?.progress_percentage || 0 + '%' }}
                ></div>
              </div>
              <p>{progress?.message || 'Processing...'}</p>
              <small>
                Step {progress?.steps_completed || 0} of {progress?.total_steps || 5}
              </small>
            </div>
          )}

          {currentSession.status === 'completed' && (
            <div className="research-complete">
              <p>✓ Research completed successfully</p>
            </div>
          )}

          {currentSession.status === 'failed' && (
            <div className="research-failed">
              <p>✗ Research failed: {currentSession.error_message}</p>
              <button
                className="btn btn-secondary"
                onClick={handleRetry}
              >
                <RotateCcw size={18} />
                Retry
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

              {currentSession.report.discovery_questions && (
                <div className="report-item">
                  <h3>Discovery Questions</h3>
                  <ul>
                    {currentSession.report.discovery_questions.map((q, i) => (
                      <li key={i}>{q.question}</li>
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
            <h2>Ask Questions</h2>

            <div className="chat-messages">
              {messages.length === 0 ? (
                <p className="chat-empty">
                  Ask questions about the research findings
                </p>
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
                placeholder="Ask a question about the research..."
                disabled={loading}
              />
              <button type="submit" className="btn btn-primary" disabled={loading}>
                Send
              </button>
            </form>
          </section>
        )}
      </div>
    </div>
  );
}

export default SessionDetailPage;
