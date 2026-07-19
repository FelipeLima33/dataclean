import React, { useState, useEffect } from 'react';

const Step5Result = ({ finalResult, previewRows, datasetId }) => {
  const [narrative, setNarrative] = useState(null);
  const [loadingNarrative, setLoadingNarrative] = useState(false);
  const [narrativeProvider, setNarrativeProvider] = useState(null);

  useEffect(() => {
    if (datasetId) {
      setLoadingNarrative(true);
      fetch(`/api/narrative/${datasetId}`)
        .then(res => res.json())
        .then(data => {
          setNarrative(data.narrative);
          setNarrativeProvider(data.provider_used);
        })
        .catch(err => {
          console.error(err);
          setNarrative("Sua planilha foi limpa com sucesso, mas não foi possível gerar o resumo detalhado automático.");
        })
        .finally(() => setLoadingNarrative(false));
    }
  }, [datasetId]);

  // If no real result yet, fall back to placeholder UI
  const hasResult = finalResult && finalResult.diagnostics;

  const rowsTotal        = hasResult ? finalResult.rows_total : '—';
  const inconsistencies  = hasResult ? (finalResult.diagnostics.text_inconsistencies_resolved ?? 0) : '—';
  const rowsBefore       = hasResult ? (finalResult.diagnostics.rows_before ?? '—') : '—';
  const duplicatesRemoved = hasResult ? (finalResult.diagnostics.duplicates_removed ?? 0) : '—';

  const handleDownload = () => {
    if (!finalResult?.download_url) return;
    window.open(`/api${finalResult.download_url}`, '_blank');
  };

  return (
    <div className="step-container">
      <h2>5. Relatório Final</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Sua planilha está limpa e pronta para uso!</p>

      {/* Narrative Section */}
      <div className="card" style={{ marginBottom: '1.5rem', backgroundColor: 'var(--surface-hover)', border: '1px solid var(--border)' }}>
        <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)' }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          Resumo Executivo (IA)
        </h3>
        
        {loadingNarrative ? (
          <div style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
             <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ animation: 'spin 1s linear infinite' }}>
              <path d="M21 12a9 9 0 1 1-6.219-8.56" />
            </svg>
            A IA está redigindo o seu resumo executivo...
          </div>
        ) : narrative ? (
          <>
            <p style={{ color: 'var(--text-color)', lineHeight: '1.6', fontSize: '1.05rem', margin: 0 }}>
              {narrative}
            </p>
          </>
        ) : (
           <p style={{ color: 'var(--text-muted)', margin: 0 }}>Resumo não disponível.</p>
        )}
      </div>

      {/* Summary metrics */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>Métricas (Antes vs Depois)</h3>
        <div style={{ display: 'flex', gap: '2rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
          <div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Linhas Antes</p>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--danger)' }}>{rowsBefore}</p>
          </div>
          <div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Linhas Depois</p>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)' }}>{rowsTotal}</p>
          </div>
          <div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Duplicatas Removidas</p>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)' }}>{duplicatesRemoved}</p>
          </div>
          <div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Inconsistências Resolvidas</p>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)' }}>{inconsistencies}</p>
          </div>
        </div>
      </div>

      {/* Preview table */}
      {previewRows && previewRows.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Preview do Dataset Limpo</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  {Object.keys(previewRows[0]).map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewRows.map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).map((val, j) => (
                      <td key={j}>{String(val)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="download-actions">
        <button
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          onClick={handleDownload}
          disabled={!finalResult?.download_url}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Baixar Planilha Limpa (CSV)
        </button>
        <button className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }} disabled>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          Gerar Relatório PDF
        </button>
      </div>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default Step5Result;
