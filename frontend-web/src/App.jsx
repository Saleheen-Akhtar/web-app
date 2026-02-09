import React, { useState } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import { Beaker, LogOut, User } from 'lucide-react';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');

  const handleLogin = (user) => {
    setUsername(user);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUsername('');
  };

  return (
    <div className="app">
      {isLoggedIn && (
        <header className="topbar">
          <div className="topbar-brand">
            <Beaker size={24} strokeWidth={1.5} />
            <span>ChemViz</span>
          </div>
          <div className="topbar-actions">
            <div className="topbar-user">
              <div className="topbar-avatar">
                <User size={16} />
              </div>
              <span>{username}</span>
            </div>
            <button className="topbar-logout" onClick={handleLogout}>
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        </header>
      )}
      {isLoggedIn ? (
        <Dashboard onLogout={handleLogout} username={username} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;
