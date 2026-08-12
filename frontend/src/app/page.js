'use client';

/**
 * SNETH Nesting Module — Main Application Page
 * Orchestrates all components: SheetForm, PieceManager, NestingCanvas, ResultPanel
 */

import { useState, useCallback, useEffect } from 'react';
import Header from '@/components/Header';
import SheetForm from '@/components/SheetForm';
import PieceManager from '@/components/PieceManager';
import NestingCanvas from '@/components/NestingCanvas';
import ResultPanel from '@/components/ResultPanel';
import { previewNesting, downloadDXF } from '@/lib/api';

export default function Home() {
  // ── State ──
  const [sheetData, setSheetData] = useState({
    sheet_width: 2500,
    sheet_height: 1250,
    thickness: 10,
    kerf: 5,
    sheet_margin: 10,
  });

  const [pieces, setPieces] = useState([]);
  const [result, setResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState(null);

  // ── Handlers ──
  const handleCalculate = useCallback(async () => {
    if (pieces.length === 0) {
      setError('Add at least one piece before calculating.');
      return;
    }

    setIsCalculating(true);
    setError(null);

    try {
      const requestBody = {
        ...sheetData,
        pieces: pieces,
      };

      const nestResult = await previewNesting(requestBody);
      setResult(nestResult);
    } catch (err) {
      setError(err.message || 'Error calculating nesting.');
      console.error('Nesting error:', err);
    } finally {
      setIsCalculating(false);
    }
  }, [sheetData, pieces]);

  const handleDownloadDXF = useCallback(async () => {
    if (pieces.length === 0) return;

    setIsDownloading(true);
    setError(null);

    try {
      const requestBody = {
        ...sheetData,
        pieces: pieces,
      };

      await downloadDXF(requestBody);
    } catch (err) {
      setError(err.message || 'Error generating DXF file.');
      console.error('DXF error:', err);
    } finally {
      setIsDownloading(false);
    }
  }, [sheetData, pieces]);

  const dismissError = () => setError(null);

  // Auto-dismiss errors after 6 seconds
  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => setError(null), 6000);
    return () => clearTimeout(timer);
  }, [error]);

  return (
    <>
      <Header />

      <main className="app-layout">
        {/* ── Left Sidebar ── */}
        <div className="sidebar">
          <SheetForm sheetData={sheetData} onUpdate={setSheetData} />
          <PieceManager pieces={pieces} onUpdate={setPieces} />

          {/* Calculate Button */}
          <div className="action-bar">
            <button
              className="btn btn-primary"
              onClick={handleCalculate}
              disabled={isCalculating || pieces.length === 0}
            >
              {isCalculating ? (
                <>
                  <span className="spinner"></span>
                  Calculating...
                </>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <rect x="2" y="2" width="14" height="14" rx="2" stroke="currentColor" strokeWidth="1.5" fill="none" />
                    <rect x="5" y="5" width="4" height="3" rx="0.5" fill="currentColor" opacity="0.7" />
                    <rect x="5" y="10" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.7" />
                    <rect x="10" y="5" width="3" height="8" rx="0.5" fill="currentColor" opacity="0.7" />
                  </svg>
                  Calculate Nesting
                </>
              )}
            </button>
          </div>
        </div>

        {/* ── Main Canvas Area ── */}
        <div className="main-area">
          <NestingCanvas result={result} sheetData={sheetData} />
        </div>

        {/* ── Bottom Result Panel ── */}
        {result && (
          <ResultPanel
            result={result}
            onDownloadDXF={handleDownloadDXF}
            isDownloading={isDownloading}
          />
        )}
      </main>

      {/* ── Error Toast ── */}
      {error && (
        <div className="error-toast">
          <span>⚠ {error}</span>
          <button onClick={dismissError}>✕</button>
        </div>
      )}
    </>
  );
}
