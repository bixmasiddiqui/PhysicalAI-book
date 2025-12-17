import React, { useState, useEffect } from 'react';
import './AuthMenu.css';

const API_URL = 'http://localhost:8000';

export default function AuthMenu() {
  const [user, setUser] = useState(null);
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('auth_token');
    const userData = localStorage.getItem('user_data');
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        setUser(data.user);
        setShowLogin(false);
        setEmail('');
        setPassword('');
      } else {
        const error = await response.json();
        setError(error.detail || 'Login failed');
      }
    } catch (err) {
      setError('Connection error. Make sure backend is running on port 8000.');
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch(`${API_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          onboarding: {
            role: 'Student',
            programming_experience: 'Beginner',
            preferred_language: 'English'
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        setUser(data.user);
        setShowSignup(false);
        setEmail('');
        setPassword('');
      } else {
        const error = await response.json();
        setError(error.detail || 'Signup failed');
      }
    } catch (err) {
      setError('Connection error. Make sure backend is running on port 8000.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    setUser(null);
  };

  if (user) {
    return (
      <div className="auth-menu">
        <span className="user-email">{user.email}</span>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>
    );
  }

  return (
    <div className="auth-menu">
      <button onClick={() => setShowLogin(true)} className="auth-btn">Login</button>
      <button onClick={() => setShowSignup(true)} className="auth-btn signup">Sign Up</button>

      {showLogin && (
        <div className="modal-overlay" onClick={() => setShowLogin(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
              {error && <div className="error">{error}</div>}
              <button type="submit">Login</button>
              <button type="button" onClick={() => setShowLogin(false)}>Cancel</button>
            </form>
          </div>
        </div>
      )}

      {showSignup && (
        <div className="modal-overlay" onClick={() => setShowSignup(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h2>Sign Up</h2>
            <form onSubmit={handleSignup}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
              <input
                type="password"
                placeholder="Password (min 8 characters)"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                minLength={8}
              />
              {error && <div className="error">{error}</div>}
              <button type="submit">Sign Up</button>
              <button type="button" onClick={() => setShowSignup(false)}>Cancel</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
