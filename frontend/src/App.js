import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const API_REGION1 = process.env.REACT_APP_API_REGION1 || 'http://localhost:8000';
const API_REGION2 = process.env.REACT_APP_API_REGION2 || 'http://localhost:8100';

// Credentials: admin / admin123
const VALID_CREDENTIALS = { username: 'admin', password: 'admin123' };

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [activeRegion, setActiveRegion] = useState('region1');
  const [apiBase, setApiBase] = useState(API_REGION1);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const [modalData, setModalData] = useState(null);
  const [modalTitle, setModalTitle] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    setApiBase(activeRegion === 'region1' ? API_REGION1 : API_REGION2);
  }, [activeRegion]);

  useEffect(() => {
    if (isLoggedIn) {
      fetchStatus();
      const interval = setInterval(fetchStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [apiBase, isLoggedIn]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === VALID_CREDENTIALS.username && password === VALID_CREDENTIALS.password) {
      setIsLoggedIn(true);
      setLoginError('');
    } else {
      setLoginError('Invalid credentials. Use admin / admin123');
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUsername('');
    setPassword('');
  };

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${apiBase}/api/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const showModal = (title, data) => {
    setModalTitle(title);
    setModalData(data);
  };

  const closeModal = () => {
    setModalData(null);
    setModalTitle('');
  };

  const fetchActiveUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiBase}/api/users/active`);
      showModal('Active Users', response.data);
    } catch (error) {
      showModal('Active Users', { error: 'Failed to fetch users' });
    }
    setLoading(false);
  };

  const fetchActiveDevices = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiBase}/api/devices/active`);
      showModal('Active Devices', response.data);
    } catch (error) {
      showModal('Active Devices', { error: 'Failed to fetch devices' });
    }
    setLoading(false);
  };

  const fetchVersion = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiBase}/fastapi/${activeRegion}/getappversion`);
      showModal('Deployment Version', response.data);
    } catch (error) {
      showModal('Deployment Version', { error: 'Failed to fetch version' });
    }
    setLoading(false);
  };

  const fetchLogStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiBase}/api/diagnostics/logs/stats`);
      showModal('Log Diagnostics', response.data);
    } catch (error) {
      showModal('Log Diagnostics', { error: 'Failed to fetch log stats' });
    }
    setLoading(false);
  };

  const simulateHighTraffic = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${apiBase}/api/simulate/high-traffic`);
      showModal('High Traffic Simulation', response.data);
    } catch (error) {
      showModal('High Traffic Simulation', { error: 'Failed to simulate traffic' });
    }
    setLoading(false);
  };

  const simulateFailover = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${apiBase}/api/failover/simulate`);
      showModal('Failover Simulation', response.data);
      const targetRegion = response.data.target_region;
      setActiveRegion(targetRegion);
    } catch (error) {
      showModal('Failover Simulation', { error: 'Failed to simulate failover' });
    }
    setLoading(false);
  };

  const searchImages = async () => {
    if (!searchQuery.trim()) {
      showModal('Image Search', { error: 'Please enter a search query' });
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${apiBase}/api/images/search`, {
        query: searchQuery,
        top_k: 5
      });
      showModal('Image Search Results', response.data);
    } catch (error) {
      showModal('Image Search Results', { error: 'Failed to search images' });
    }
    setLoading(false);
  };

  const queryLLM = async (question) => {
    setLoading(true);
    try {
      const response = await axios.post(`${apiBase}/api/diagnostics/query`, {
        question: question
      });
      showModal('AI Query Response', response.data);
    } catch (error) {
      showModal('AI Query Response', { error: 'Failed to query LLM' });
    }
    setLoading(false);
  };

  // Login Page
  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-box">
          <h1>Enterprise SRE Dashboard</h1>
          <p>99.99999% Availability System</p>
          {loginError && <div className="login-error">{loginError}</div>}
          <form className="login-form" onSubmit={handleLogin}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="admin"
                autoComplete="username"
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="admin123"
                autoComplete="current-password"
              />
            </div>
            <button type="submit" className="login-btn">Login</button>
          </form>
        </div>
      </div>
    );
  }

  // Dashboard
  return (
    <div className="App">
      <header className="App-header">
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
        <h1>Enterprise SRE AI Dashboard</h1>
        <p className="subtitle">99.99999% Availability • Tier-0 Reliability System</p>

        <div className="region-selector">
          <button
            className={activeRegion === 'region1' ? 'active' : ''}
            onClick={() => setActiveRegion('region1')}
          >
            Region 1
          </button>
          <button
            className={activeRegion === 'region2' ? 'active' : ''}
            onClick={() => setActiveRegion('region2')}
          >
            Region 2
          </button>
        </div>
      </header>

      <main className="dashboard">
        <section className="status-section">
          <h2>Live System Status</h2>
          {status && (
            <div className="status-card">
              <div className="status-item">
                <span className="label">Region</span>
                <span className="value">{status.region}</span>
              </div>
              <div className="status-item">
                <span className="label">Status</span>
                <span className="value">{status.status}</span>
              </div>
              <div className="status-item">
                <span className="label">Version</span>
                <span className="value">{status.version}</span>
              </div>
              <div className="status-item">
                <span className="label">Active Devices</span>
                <span className="value">{status.active_devices || 0}</span>
              </div>
              <div className="status-item">
                <span className="label">Active Users</span>
                <span className="value">{status.active_users || 0}</span>
              </div>
            </div>
          )}
        </section>

        <section className="actions-section">
          <h2>Dashboard Controls</h2>
          <div className="button-grid">
            <button className="action-btn" onClick={fetchActiveUsers} disabled={loading}>
              Active Users
            </button>
            <button className="action-btn" onClick={fetchActiveDevices} disabled={loading}>
              Active Devices
            </button>
            <button className="action-btn" onClick={fetchVersion} disabled={loading}>
              Deployment Version
            </button>
            <button className="action-btn" onClick={fetchStatus} disabled={loading}>
              Refresh Status
            </button>
            <button className="action-btn" onClick={fetchLogStats} disabled={loading}>
              Log Diagnostics
            </button>
            <button className="action-btn" onClick={simulateHighTraffic} disabled={loading}>
              Simulate High Traffic
            </button>
            <button className="action-btn" onClick={simulateFailover} disabled={loading}>
              Simulate Failover
            </button>
          </div>
        </section>

        <section className="search-section">
          <h2>AI-Powered Search & Queries</h2>
          <div className="search-box">
            <input
              type="text"
              placeholder="Search images or ask questions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchImages()}
            />
            <button onClick={searchImages} disabled={loading}>Search Images</button>
          </div>

          <div className="quick-queries">
            <h3>Quick Queries:</h3>
            <button onClick={() => queryLLM("How many safety incidences occurred in BP operations in 2024?")} disabled={loading}>
              Safety Incidents 2024
            </button>
            <button onClick={() => queryLLM("Describe BP oil drill operations and hard hat requirements")} disabled={loading}>
              Hard Hat Requirements
            </button>
            <button onClick={() => queryLLM("Give me the most frequent IP devices generating error 400")} disabled={loading}>
              Top IPs - Error 400
            </button>
            <button onClick={() => queryLLM("List economic and social sustainability statements")} disabled={loading}>
              Sustainability
            </button>
          </div>
        </section>
      </main>

      <footer className="App-footer">
        <p>Enterprise Distributed Systems COE • CMPE 273 • San José State University</p>
        <p>Powered by FastAPI, React, Redis Stack, MQTT, RabbitMQ, Cohere AI</p>
      </footer>

      {/* Modal */}
      {modalData && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>Close</button>
            <h3>{modalTitle}</h3>
            {modalData.answer ? (
              <div>
                <p><strong>Question:</strong> {modalData.question}</p>
                <p style={{marginTop: '1rem', whiteSpace: 'pre-wrap'}}>{modalData.answer}</p>
              </div>
            ) : (
              <pre>{JSON.stringify(modalData, null, 2)}</pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
