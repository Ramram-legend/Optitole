'use client';

/**
 * NestingCanvas — Interactive SVG visualization of the nesting result.
 * Shows the sheet, margins, placed pieces with labels, and unplaced pieces.
 * Supports zoom (scroll wheel) and pan (drag).
 */

import { useRef, useState, useCallback, useEffect } from 'react';

// Distinct colors for pieces (industrial palette)
const PIECE_COLORS = [
  'hsl(25, 85%, 55%)',   // burnt orange
  'hsl(200, 70%, 50%)',  // steel blue
  'hsl(140, 60%, 45%)',  // industrial green
  'hsl(280, 55%, 55%)',  // violet
  'hsl(45, 80%, 50%)',   // amber
  'hsl(340, 65%, 50%)',  // crimson
  'hsl(170, 60%, 45%)',  // teal
  'hsl(15, 75%, 45%)',   // rust
  'hsl(220, 65%, 55%)',  // cobalt
  'hsl(60, 70%, 45%)',   // olive gold
];

function getColorForPiece(id, index) {
  // Same ID = same color, otherwise cycle
  const hash = id.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  return PIECE_COLORS[(hash + index) % PIECE_COLORS.length];
}

export default function NestingCanvas({ result, sheetData }) {
  const svgRef = useRef(null);
  const [viewBox, setViewBox] = useState(null);
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [hoveredPiece, setHoveredPiece] = useState(null);

  const sw = sheetData.sheet_width;
  const sh = sheetData.sheet_height;
  const margin = sheetData.sheet_margin;
  const padding = 60;

  // Initialize viewBox
  useEffect(() => {
    setViewBox({
      x: -padding,
      y: -padding,
      w: sw + padding * 2,
      h: sh + padding * 2,
    });
  }, [sw, sh, padding]);

  // Zoom handler
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    if (!viewBox) return;

    const factor = e.deltaY > 0 ? 1.1 : 0.9;
    const svgEl = svgRef.current;
    const rect = svgEl.getBoundingClientRect();

    // Mouse position in SVG coords
    const mx = viewBox.x + (e.clientX - rect.left) / rect.width * viewBox.w;
    const my = viewBox.y + (e.clientY - rect.top) / rect.height * viewBox.h;

    const newW = viewBox.w * factor;
    const newH = viewBox.h * factor;

    setViewBox({
      x: mx - (mx - viewBox.x) * factor,
      y: my - (my - viewBox.y) * factor,
      w: newW,
      h: newH,
    });
  }, [viewBox]);

  // Pan handlers
  const handleMouseDown = useCallback((e) => {
    if (e.button !== 0) return;
    setIsPanning(true);
    setPanStart({ x: e.clientX, y: e.clientY });
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!isPanning || !viewBox) return;
    const svgEl = svgRef.current;
    const rect = svgEl.getBoundingClientRect();

    const dx = (e.clientX - panStart.x) / rect.width * viewBox.w;
    const dy = (e.clientY - panStart.y) / rect.height * viewBox.h;

    setViewBox(prev => ({
      ...prev,
      x: prev.x - dx,
      y: prev.y - dy,
    }));
    setPanStart({ x: e.clientX, y: e.clientY });
  }, [isPanning, panStart, viewBox]);

  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
  }, []);

  // Reset zoom
  const resetView = () => {
    setViewBox({
      x: -padding,
      y: -padding,
      w: sw + padding * 2,
      h: sh + padding * 2,
    });
  };

  if (!viewBox) return null;

  const hasResult = result && result.placed_pieces && result.placed_pieces.length > 0;

  return (
    <div className="canvas-container">
      <div className="canvas-toolbar">
        <span className="label-text">PREVIEW</span>
        <div className="canvas-controls">
          <button className="canvas-btn" onClick={resetView} title="Reset zoom">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M2 2h4M2 2v4M14 14h-4M14 14v-4M14 2h-4M14 2v4M2 14h4M2 14v-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
          {hasResult && (
            <span className="canvas-info">
              {result.placed_pieces.length} placed piece{result.placed_pieces.length > 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      <svg
        ref={svgRef}
        className="nesting-svg"
        viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isPanning ? 'grabbing' : 'grab' }}
      >
        {/* Background grid pattern */}
        <defs>
          <pattern id="grid" width="100" height="100" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="100" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
            <line x1="0" y1="0" x2="100" y2="0" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          </pattern>
          <pattern id="gridFine" width="50" height="50" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="50" stroke="rgba(255,255,255,0.015)" strokeWidth="0.5" />
            <line x1="0" y1="0" x2="50" y2="0" stroke="rgba(255,255,255,0.015)" strokeWidth="0.5" />
          </pattern>
        </defs>

        {/* Sheet background */}
        <rect
          x={0} y={0} width={sw} height={sh}
          fill="rgba(255,255,255,0.02)"
          stroke="rgba(255,255,255,0.4)"
          strokeWidth={sw * 0.002}
          rx={2}
        />
        <rect x={0} y={0} width={sw} height={sh} fill="url(#grid)" />
        <rect x={0} y={0} width={sw} height={sh} fill="url(#gridFine)" />

        {/* Margin border */}
        {margin > 0 && (
          <rect
            x={margin} y={margin}
            width={sw - 2 * margin} height={sh - 2 * margin}
            fill="none"
            stroke="rgba(0,200,255,0.2)"
            strokeWidth={sw * 0.001}
            strokeDasharray={`${sw * 0.008} ${sw * 0.004}`}
          />
        )}

        {/* Placed pieces */}
        {hasResult && result.placed_pieces.map((piece, idx) => {
          const color = getColorForPiece(piece.id, idx);
          const isHovered = hoveredPiece === idx;
          const fontSize = Math.min(piece.width, piece.height) * 0.12;
          const clampedFontSize = Math.max(8, Math.min(fontSize, 30));

          return (
            <g
              key={`${piece.id}-${idx}`}
              onMouseEnter={() => setHoveredPiece(idx)}
              onMouseLeave={() => setHoveredPiece(null)}
              style={{ transition: 'opacity 0.2s' }}
              opacity={hoveredPiece !== null && !isHovered ? 0.5 : 1}
            >
              {/* Piece rectangle */}
              <rect
                x={piece.x} y={piece.y}
                width={piece.width} height={piece.height}
                fill={color}
                fillOpacity={isHovered ? 0.35 : 0.2}
                stroke={color}
                strokeWidth={isHovered ? sw * 0.002 : sw * 0.001}
                rx={1}
              />

              {/* Piece label */}
              <text
                x={piece.x + piece.width / 2}
                y={piece.y + piece.height / 2 - clampedFontSize * 0.3}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="rgba(255,255,255,0.9)"
                fontSize={clampedFontSize}
                fontWeight="600"
                fontFamily="var(--font-body)"
              >
                {piece.id}
              </text>

              {/* Dimensions */}
              <text
                x={piece.x + piece.width / 2}
                y={piece.y + piece.height / 2 + clampedFontSize * 0.7}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="rgba(255,255,255,0.5)"
                fontSize={clampedFontSize * 0.65}
                fontFamily="var(--font-body)"
              >
                {piece.width}×{piece.height}{piece.rotated ? ' ↻' : ''}
              </text>
            </g>
          );
        })}

        {/* Dimension annotations */}
        {/* Width */}
        <text
          x={sw / 2} y={-padding * 0.4}
          textAnchor="middle"
          fill="rgba(255,255,255,0.4)"
          fontSize={Math.max(14, sw * 0.012)}
          fontFamily="var(--font-body)"
        >
          {sw} mm
        </text>
        {/* Height */}
        <text
          x={-padding * 0.4} y={sh / 2}
          textAnchor="middle"
          fill="rgba(255,255,255,0.4)"
          fontSize={Math.max(14, sh * 0.012)}
          fontFamily="var(--font-body)"
          transform={`rotate(-90, ${-padding * 0.4}, ${sh / 2})`}
        >
          {sh} mm
        </text>

        {/* Empty state */}
        {!hasResult && (
          <text
            x={sw / 2} y={sh / 2}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="rgba(255,255,255,0.15)"
            fontSize={Math.max(20, sw * 0.02)}
            fontFamily="var(--font-body)"
            fontWeight="600"
          >
            Click "Calculate" to start nesting
          </text>
        )}
      </svg>

      {/* Hovered piece tooltip */}
      {hasResult && hoveredPiece !== null && result.placed_pieces[hoveredPiece] && (
        <div className="canvas-tooltip">
          <strong>{result.placed_pieces[hoveredPiece].label}</strong>
          <span>{result.placed_pieces[hoveredPiece].width}×{result.placed_pieces[hoveredPiece].height} mm</span>
          <span>Position: ({result.placed_pieces[hoveredPiece].x}, {result.placed_pieces[hoveredPiece].y})</span>
          {result.placed_pieces[hoveredPiece].rotated && <span className="rotated-badge">↻ Rotated 90°</span>}
        </div>
      )}
    </div>
  );
}
