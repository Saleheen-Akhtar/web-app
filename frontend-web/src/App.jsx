import React, { useState } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = (username) => {
    // Optionally store token/user
    setIsLoggedIn(true);
  };

  return (
    <div className="App">
      <nav className="navbar navbar-dark bg-dark mb-4">
        <div className="container-fluid">
          <span className="navbar-brand mb-0 h1">Chemical Equipment Visualizer</span>
          {isLoggedIn && <button className="btn btn-outline-light" onClick={() => setIsLoggedIn(false)}>Logout</button>}
        </div>
      </nav>
      {isLoggedIn ? <Dashboard /> : <Login onLogin={handleLogin} />}
    </div>
  );
}

export default App;
