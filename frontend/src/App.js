import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    // Check system health
    axios
      .get(`${API}/health`)
      .then((res) => setSystemStatus(res.data))
      .catch((err) => console.error('Health check failed:', err));
  }, []);

  return (
    <div className="App min-h-screen bg-gray-900 text-white">
      <BrowserRouter>
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h1 className="text-2xl font-bold text-blue-400">🤖 Jarvis AI</h1>
                {systemStatus && (
                  <span
                    className={`px-3 py-1 text-xs rounded-full ${
                      systemStatus.status === 'healthy'
                        ? 'bg-green-900 text-green-300'
                        : 'bg-red-900 text-red-300'
                    }`}
                  >
                    {systemStatus.status === 'healthy' ? '● Online' : '● Offline'}
                  </span>
                )}
              </div>
              <nav className="flex space-x-6">
                <Link
                  to="/"
                  className="hover:text-blue-400 transition-colors"
                  data-testid="nav-dashboard"
                >
                  Dashboard
                </Link>
                <Link
                  to="/chat"
                  className="hover:text-blue-400 transition-colors"
                  data-testid="nav-chat"
                >
                  Chat
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
