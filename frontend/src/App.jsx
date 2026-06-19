/**
 * Main App component with routing and layout
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useSession } from './hooks';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import SessionCreatePage from './pages/SessionCreatePage';
import SessionDetailPage from './pages/SessionDetailPage';
import './styles/App.css';

function App() {
  const [error, setError] = useState(null);
  const { fetchSessions } = useSession();

  useEffect(() => {
    // Load sessions on app startup
    fetchSessions().catch((err) => {
      console.error('Failed to load sessions:', err);
      setError('Failed to load sessions');
    });
  }, [fetchSessions]);

  return (
    <Router>
      <Layout error={error} setError={setError}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/create" element={<SessionCreatePage />} />
          <Route path="/session/:sessionId" element={<SessionDetailPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
