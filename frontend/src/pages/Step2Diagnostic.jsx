import React from 'react';

const Step2Diagnostic = ({ diagnostics, onNext }) => {
  // Build resolved / pending items from real API response
  const resolved = diagnostics
    ? [
        { type: 'Linhas Duplicadas', count: diagnostics.duplicates_removed ?? 0, status: 'Resolvido', color: 'var(--success)' },
        { type: 'Valores Ausentes', count: diagnostics.missing_values_filled ?? 0, status: 'Preenchido (Média/Moda)', color: 'var(--success)' },
        { type: 'Outliers', count: diagnostics.outliers_flagged ?? 0, status: 'Marcado', color: 'var(--success)' },
      ]
    : [];

  const pending = diagnostics
    ? [
        { type: 'Inconsistências de Texto', count: diagnostics.text_inconsistencies_found ?? 0, status: 'Revisão Necessária', color: 'var(--warning)' },
      ]
    : [];

  const rowsBefore = diagnostics?.rows_before ?? '—';
  const rowsAfter  = diagnostics?.rows_after  ?? '—';

  return (
    <div className="step-container">
      <h2>2. Diagnóstico Automático</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Analisamos seu arquivo e resolvemos os problemas mais comuns automaticamente.</p>

      {/* Row counts */}
      <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card" style={{ flex: 1, padding: '1rem', textAlign: 'center' }}>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Linhas antes</p>
          <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{rowsBefore}</p>
        </div>
        <div className="card" style={{ flex: 1, padding: '1rem', textAlign: 'center' }}>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Linhas depois</p>
          <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{rowsAfter}</p>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1.5rem', color: 'var(--success)' }}>Resolvidos Automaticamente</h3>
        <div className="diagnostic-grid">
          {resolved.map((item, idx) => (
            <div key={idx} className="diagnostic-item card" style={{ marginBottom: 0, padding: '1.5rem', borderLeft: `4px solid ${item.color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{item.type}</span>
                <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', borderRadius: '1rem', border: `1px solid ${item.color}`, color: item.color }}>{item.status}</span>
              </div>
              <div className="diagnostic-count">{item.count}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginTop: '2rem', border: '1px solid var(--warning)' }}>
        <h3 style={{ marginBottom: '1.5rem', color: 'var(--warning)' }}>Requer Sua Atenção</h3>
        <div className="diagnostic-grid">
          {pending.map((item, idx) => (
            <div key={idx} className="diagnostic-item card" style={{ marginBottom: 0, padding: '1.5rem', borderLeft: `4px solid ${item.color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{item.type}</span>
                <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', borderRadius: '1rem', border: `1px solid ${item.color}`, color: item.color }}>{item.status}</span>
              </div>
              <div className="diagnostic-count">{item.count}</div>
            </div>
          ))}
        </div>
      </div>



      <button
        className="btn btn-primary"
        onClick={onNext}
        style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
      >
        Ver sugestões da IA →
      </button>
    </div>
  );
};

export default Step2Diagnostic;
