'use client';

/**
 * ResultPanel — Shows nesting statistics, unplaced pieces, and DXF download.
 */

export default function ResultPanel({ result, onDownloadDXF, isDownloading }) {
  if (!result) return null;

  const utilizationColor =
    result.utilization_rate >= 70 ? 'var(--success)' :
    result.utilization_rate >= 45 ? 'var(--warning)' :
    'var(--danger)';

  return (
    <div className="result-panel">
      <div className="result-stats">
        {/* Utilization gauge */}
        <div className="stat-card stat-main">
          <div className="gauge-container">
            <svg viewBox="0 0 120 120" className="gauge-svg">
              <circle
                cx="60" cy="60" r="50"
                fill="none"
                stroke="rgba(255,255,255,0.05)"
                strokeWidth="8"
              />
              <circle
                cx="60" cy="60" r="50"
                fill="none"
                stroke={utilizationColor}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${result.utilization_rate * 3.14} ${314 - result.utilization_rate * 3.14}`}
                transform="rotate(-90 60 60)"
                style={{ transition: 'stroke-dasharray 1s cubic-bezier(0.16, 1, 0.3, 1)' }}
              />
              <text x="60" y="55" textAnchor="middle" fill="white" fontSize="22" fontWeight="700" fontFamily="var(--font-body)">
                {result.utilization_rate.toFixed(1)}%
              </text>
              <text x="60" y="72" textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize="9" fontFamily="var(--font-body)">
                UTILIZATION
              </text>
            </svg>
          </div>
        </div>

        {/* Stats grid */}
        <div className="stat-card">
          <span className="stat-label">Placed pieces</span>
          <span className="stat-value">{result.total_placed}<span className="stat-total">/{result.total_requested}</span></span>
        </div>

        <div className="stat-card">
          <span className="stat-label">Cut type</span>
          <span className={`stat-value cut-type-value ${result.cut_type}`}>
            {result.cut_type === 'laser' ? '⚡ LASER' : '🔥 PLASMA'}
          </span>
        </div>

        <div className="stat-card">
          <span className="stat-label">Applied Kerf</span>
          <span className="stat-value">{result.kerf} mm</span>
        </div>
      </div>

      {/* Unplaced pieces warning */}
      {result.unplaced_pieces && result.unplaced_pieces.length > 0 && (
        <div className="unplaced-warning">
          <div className="warning-header">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M9 1L1 16h16L9 1z" stroke="var(--warning)" strokeWidth="1.5" fill="none" />
              <line x1="9" y1="6" x2="9" y2="10" stroke="var(--warning)" strokeWidth="1.5" strokeLinecap="round" />
              <circle cx="9" cy="13" r="0.8" fill="var(--warning)" />
            </svg>
            <span>{result.unplaced_pieces.length} unplaced piece{result.unplaced_pieces.length > 1 ? 's' : ''}</span>
          </div>
          <div className="unplaced-list">
            {result.unplaced_pieces.map((piece, i) => (
              <span key={i} className="unplaced-item">
                {piece.label} ({piece.width}×{piece.height})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Download button */}
      <button
        className="btn btn-download"
        onClick={onDownloadDXF}
        disabled={isDownloading}
      >
        {isDownloading ? (
          <>
            <span className="spinner"></span>
            Generating...
          </>
        ) : (
          <>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 3v10M10 13l-4-4M10 13l4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M3 15v2h14v-2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Download DXF file
          </>
        )}
      </button>
    </div>
  );
}
