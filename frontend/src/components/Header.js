'use client';

/**
 * Header — SNETH industrial branding bar with connection status indicator.
 */

import { useState, useEffect } from 'react';
import { checkHealth } from '@/lib/api';

export default function Header() {
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    const check = async () => {
      const ok = await checkHealth();
      setBackendOnline(ok);
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-brand">
          <div className="header-logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect x="2" y="2" width="28" height="28" rx="6" stroke="currentColor" strokeWidth="1.5" fill="none" />
              <path d="M8 16h16M16 8v16M10 10l12 12M22 10l-12 12" stroke="var(--accent)" strokeWidth="1.2" strokeLinecap="round" opacity="0.7" />
              <circle cx="16" cy="16" r="3" fill="var(--accent)" opacity="0.9" />
            </svg>
          </div>
          <div>
            <h1 className="header-title">SNETH</h1>
            <p className="header-subtitle">Nesting Module — Cutting Optimization</p>
          </div>
        </div>

        <div className="header-right">
          <div className="header-badge">
            <span className="label-text">WORKSHOP 4.0</span>
          </div>
          <div className={`status-indicator ${backendOnline ? 'online' : 'offline'}`}>
            <span className="status-dot"></span>
            <span className="status-text">{backendOnline ? 'API Connected' : 'API Offline'}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
