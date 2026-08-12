'use client';

/**
 * PieceManager — Add, edit, delete pieces to be nested on the sheet.
 */

import { useState } from 'react';

const PRESETS = [
  { label: 'Standard Gusset', width: 200, height: 150 },
  { label: 'Plate 300×200', width: 300, height: 200 },
  { label: 'Stiffener 150×100', width: 150, height: 100 },
  { label: 'Sheet 500×400', width: 500, height: 400 },
  { label: 'Spacer 250×80', width: 250, height: 80 },
];

let pieceCounter = 0;

export default function PieceManager({ pieces, onUpdate }) {
  const [newPiece, setNewPiece] = useState({
    label: '',
    width: '',
    height: '',
    quantity: 1,
    allow_rotation: true,
  });

  const addPiece = () => {
    if (!newPiece.label || !newPiece.width || !newPiece.height) return;

    pieceCounter++;
    const piece = {
      id: `P-${String(pieceCounter).padStart(3, '0')}`,
      label: newPiece.label,
      width: parseFloat(newPiece.width),
      height: parseFloat(newPiece.height),
      quantity: parseInt(newPiece.quantity) || 1,
      allow_rotation: newPiece.allow_rotation,
    };

    onUpdate([...pieces, piece]);
    setNewPiece({ label: '', width: '', height: '', quantity: 1, allow_rotation: true });
  };

  const addPreset = (preset) => {
    pieceCounter++;
    const piece = {
      id: `P-${String(pieceCounter).padStart(3, '0')}`,
      label: preset.label,
      width: preset.width,
      height: preset.height,
      quantity: 1,
      allow_rotation: true,
    };
    onUpdate([...pieces, piece]);
  };

  const removePiece = (index) => {
    onUpdate(pieces.filter((_, i) => i !== index));
  };

  const updateQuantity = (index, qty) => {
    const updated = [...pieces];
    updated[index] = { ...updated[index], quantity: Math.max(1, parseInt(qty) || 1) };
    onUpdate(updated);
  };

  const toggleRotation = (index) => {
    const updated = [...pieces];
    updated[index] = { ...updated[index], allow_rotation: !updated[index].allow_rotation };
    onUpdate(updated);
  };

  const totalInstances = pieces.reduce((sum, p) => sum + p.quantity, 0);
  const totalArea = pieces.reduce((sum, p) => sum + p.width * p.height * p.quantity, 0);

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <rect x="3" y="3" width="6" height="6" rx="1" stroke="var(--accent)" strokeWidth="1.5" />
            <rect x="11" y="3" width="6" height="4" rx="1" stroke="var(--accent)" strokeWidth="1.5" />
            <rect x="3" y="11" width="5" height="6" rx="1" stroke="var(--accent)" strokeWidth="1.5" />
            <rect x="10" y="9" width="7" height="8" rx="1" stroke="var(--accent)" strokeWidth="1.5" />
          </svg>
        </div>
        <h2 className="card-title">Pieces to Cut</h2>
        {pieces.length > 0 && (
          <span className="piece-count">{totalInstances} piece{totalInstances > 1 ? 's' : ''}</span>
        )}
      </div>

      {/* Presets */}
      <div className="presets-section">
        <span className="label-text">PRESETS</span>
        <div className="presets-grid">
          {PRESETS.map((preset, i) => (
            <button
              key={i}
              className="preset-btn"
              onClick={() => addPreset(preset)}
            >
              <span className="preset-name">{preset.label}</span>
              <span className="preset-dims">{preset.width}×{preset.height}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Manual add */}
      <div className="add-piece-section">
        <span className="label-text">ADD MANUALLY</span>
        <div className="add-piece-form">
          <input
            type="text"
            className="form-input"
            placeholder="Piece name"
            value={newPiece.label}
            onChange={(e) => setNewPiece({ ...newPiece, label: e.target.value })}
            onKeyDown={(e) => e.key === 'Enter' && addPiece()}
          />
          <div className="add-piece-dims">
            <input
              type="number"
              className="form-input"
              placeholder="Width"
              value={newPiece.width}
              onChange={(e) => setNewPiece({ ...newPiece, width: e.target.value })}
              min="1"
            />
            <span className="dim-separator">×</span>
            <input
              type="number"
              className="form-input"
              placeholder="Height"
              value={newPiece.height}
              onChange={(e) => setNewPiece({ ...newPiece, height: e.target.value })}
              min="1"
            />
          </div>
          <div className="add-piece-options">
            <div className="quantity-control">
              <label className="form-label">Qty</label>
              <input
                type="number"
                className="form-input qty-input"
                value={newPiece.quantity}
                onChange={(e) => setNewPiece({ ...newPiece, quantity: e.target.value })}
                min="1"
              />
            </div>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={newPiece.allow_rotation}
                onChange={(e) => setNewPiece({ ...newPiece, allow_rotation: e.target.checked })}
              />
              <span>90° Rotation</span>
            </label>
          </div>
          <button className="btn btn-add" onClick={addPiece}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <line x1="8" y1="3" x2="8" y2="13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              <line x1="3" y1="8" x2="13" y2="8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            Add
          </button>
        </div>
      </div>

      {/* Piece list */}
      {pieces.length > 0 && (
        <div className="piece-list">
          <span className="label-text">PIECE LIST</span>
          {pieces.map((piece, index) => (
            <div key={piece.id + index} className="piece-item">
              <div className="piece-info">
                <span className="piece-id">{piece.id}</span>
                <span className="piece-label">{piece.label}</span>
                <span className="piece-dims">{piece.width}×{piece.height} mm</span>
              </div>
              <div className="piece-actions">
                <button
                  className={`rotation-toggle ${piece.allow_rotation ? 'active' : ''}`}
                  onClick={() => toggleRotation(index)}
                  title={piece.allow_rotation ? 'Rotation enabled' : 'Rotation disabled'}
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M11 5a5 5 0 10-1.5 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                    <polyline points="11,2 11,5 8,5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>
                <div className="qty-inline">
                  <button className="qty-btn" onClick={() => updateQuantity(index, piece.quantity - 1)}>−</button>
                  <span className="qty-value">{piece.quantity}</span>
                  <button className="qty-btn" onClick={() => updateQuantity(index, piece.quantity + 1)}>+</button>
                </div>
                <button className="btn-remove" onClick={() => removePiece(index)}>
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <line x1="3" y1="3" x2="11" y2="11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                    <line x1="11" y1="3" x2="3" y2="11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
          <div className="piece-list-summary">
            <span>{totalInstances} total instance{totalInstances > 1 ? 's' : ''}</span>
            <span>Area: {(totalArea / 1e6).toFixed(3)} m²</span>
          </div>
        </div>
      )}
    </div>
  );
}
