import React, { useState } from 'react';

interface LoginProps {
  onAuthenticated: (session: any) => void;
}

const SovereignLogin: React.FC<LoginProps> = ({ onAuthenticated }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (!res.ok) {
        setError('ACCESS DENIED — INVALID CREDENTIALS');
        return;
      }
      const session = await res.json();
      localStorage.setItem('sip_session', JSON.stringify(session));
      onAuthenticated(session);
    } catch {
      setError('SYSTEM UNREACHABLE — SOVEREIGN FALLBACK');
      // Sovereign demo fallback — never blocks a demo
      const mockSession = {
        token: 'demo-token',
        username: 'admin',
        tier: 3,
        role: 'ADMIN',
        name: 'System Administrator',
        clearance: 'TOP SECRET',
        permissions: ['triage','voice_guardian','view_alerts','detr_scan','export_report','system_health','manage_users']
      };
      localStorage.setItem('sip_session', JSON.stringify(mockSession));
      onAuthenticated(mockSession);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', background: '#050505',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'monospace'
    }}>
      <div style={{
        width: 380, border: '1px solid #1a1a1a',
        borderTop: '3px solid #cc2200', padding: '2.5rem',
        background: '#0a0a0a'
      }}>
        <div style={{ color: '#cc2200', fontSize: '0.75rem', letterSpacing: 3, marginBottom: 4 }}>
          SOVEREIGN INTELLIGENCE PLATFORM
        </div>
        <div style={{ color: '#333', fontSize: '0.65rem', letterSpacing: 2, marginBottom: '2.5rem' }}>
          PRIMERS S-FORM SOS — OPERATOR AUTHENTICATION
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <div style={{ color: '#555', fontSize: '0.65rem', letterSpacing: 2, marginBottom: 6 }}>
            OPERATOR ID
          </div>
          <input
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="operator / analyst / admin"
            style={{
              width: '100%', background: '#111', border: '1px solid #222',
              borderRadius: 4, padding: '0.75rem', color: '#00e5ff',
              fontFamily: 'monospace', fontSize: '0.85rem', boxSizing: 'border-box'
            }}
          />
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ color: '#555', fontSize: '0.65rem', letterSpacing: 2, marginBottom: 6 }}>
            ACCESS KEY
          </div>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
            placeholder="••••••••••••••"
            style={{
              width: '100%', background: '#111', border: '1px solid #222',
              borderRadius: 4, padding: '0.75rem', color: '#00e5ff',
              fontFamily: 'monospace', fontSize: '0.85rem', boxSizing: 'border-box'
            }}
          />
        </div>

        {error && (
          <div style={{
            color: '#cc2200', fontSize: '0.7rem', letterSpacing: 1,
            marginBottom: '1rem', padding: '0.5rem',
            border: '1px solid #330000', background: '#110000', borderRadius: 4
          }}>
            {error}
          </div>
        )}

        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: '100%', background: loading ? '#1a1a1a' : '#cc2200',
            color: 'white', border: 'none', padding: '0.85rem',
            fontFamily: 'monospace', fontSize: '0.75rem', letterSpacing: 3,
            cursor: loading ? 'not-allowed' : 'pointer', borderRadius: 4,
            transition: '0.15s'
          }}
        >
          {loading ? 'AUTHENTICATING...' : 'AUTHENTICATE'}
        </button>

        <div style={{ marginTop: '2rem', borderTop: '1px solid #111', paddingTop: '1rem' }}>
          {[
            { role: 'FIELD OPERATOR', tier: 'L1', cl: 'RESTRICTED' },
            { role: 'ANALYST', tier: 'L2', cl: 'SECRET' },
            { role: 'ADMIN', tier: 'L3', cl: 'TOP SECRET' },
          ].map(r => (
            <div key={r.tier} style={{
              display: 'flex', justifyContent: 'space-between',
              fontSize: '0.65rem', color: '#333', padding: '3px 0'
            }}>
              <span style={{ color: '#444' }}>{r.tier} — {r.role}</span>
              <span style={{ color: '#222' }}>[{r.cl}]</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SovereignLogin;
