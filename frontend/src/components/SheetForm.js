'use client';

/**
 * SheetForm — Input form for sheet metal dimensions and cutting parameters.
 */

export default function SheetForm({ sheetData, onUpdate }) {
  const handleChange = (field, value) => {
    const numVal = parseFloat(value);
    if (!isNaN(numVal) && numVal >= 0) {
      onUpdate({ ...sheetData, [field]: numVal });
    }
  };

  // Auto-suggest kerf based on thickness
  const suggestedKerf = sheetData.thickness < 15 ? 3 : 6;
  const cutType = sheetData.thickness < 15 ? 'LASER' : 'PLASMA';

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <rect x="2" y="2" width="16" height="16" rx="2" stroke="var(--accent)" strokeWidth="1.5" />
            <line x1="6" y1="2" x2="6" y2="18" stroke="var(--accent)" strokeWidth="0.5" opacity="0.4" />
            <line x1="2" y1="6" x2="18" y2="6" stroke="var(--accent)" strokeWidth="0.5" opacity="0.4" />
          </svg>
        </div>
        <h2 className="card-title">Tôle Principale</h2>
        <span className={`cut-badge ${cutType.toLowerCase()}`}>{cutType}</span>
      </div>

      <div className="form-grid">
        <div className="form-group">
          <label className="form-label">Largeur (mm)</label>
          <input
            type="number"
            className="form-input"
            value={sheetData.sheet_width}
            onChange={(e) => handleChange('sheet_width', e.target.value)}
            min="100"
            step="10"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Hauteur (mm)</label>
          <input
            type="number"
            className="form-input"
            value={sheetData.sheet_height}
            onChange={(e) => handleChange('sheet_height', e.target.value)}
            min="100"
            step="10"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Épaisseur (mm)</label>
          <input
            type="number"
            className="form-input"
            value={sheetData.thickness}
            onChange={(e) => handleChange('thickness', e.target.value)}
            min="0.5"
            step="0.5"
          />
          <span className="form-hint">
            {'<'} 15mm → Laser · ≥ 15mm → Plasma
          </span>
        </div>

        <div className="form-group">
          <label className="form-label">Marge tôle (mm)</label>
          <input
            type="number"
            className="form-input"
            value={sheetData.sheet_margin}
            onChange={(e) => handleChange('sheet_margin', e.target.value)}
            min="0"
            step="1"
          />
          <span className="form-hint">Zone de serrage / bords</span>
        </div>
      </div>

      <div className="kerf-section">
        <div className="form-group" style={{ flex: 1 }}>
          <label className="form-label">
            Kerf — Espacement inter-pièces (mm)
          </label>
          <div className="kerf-input-row">
            <input
              type="range"
              className="form-range"
              value={sheetData.kerf}
              onChange={(e) => handleChange('kerf', e.target.value)}
              min="0"
              max="20"
              step="0.5"
            />
            <input
              type="number"
              className="form-input kerf-number"
              value={sheetData.kerf}
              onChange={(e) => handleChange('kerf', e.target.value)}
              min="0"
              max="20"
              step="0.5"
            />
          </div>
          <span className="form-hint">
            Suggestion {cutType}: {suggestedKerf}mm
            {sheetData.kerf !== suggestedKerf && (
              <button
                className="hint-btn"
                onClick={() => onUpdate({ ...sheetData, kerf: suggestedKerf })}
              >
                Appliquer
              </button>
            )}
          </span>
        </div>
      </div>

      <div className="sheet-summary">
        <div className="summary-item">
          <span className="summary-label">Surface totale</span>
          <span className="summary-value">
            {((sheetData.sheet_width * sheetData.sheet_height) / 1e6).toFixed(2)} m²
          </span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Zone utile</span>
          <span className="summary-value">
            {(((sheetData.sheet_width - 2 * sheetData.sheet_margin) *
              (sheetData.sheet_height - 2 * sheetData.sheet_margin)) / 1e6).toFixed(2)} m²
          </span>
        </div>
      </div>
    </div>
  );
}
