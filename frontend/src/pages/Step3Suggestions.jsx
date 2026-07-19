import React, { useState } from 'react';

const Step3Suggestions = ({ suggestions, onSetStatus, onSetValue, onApply, onApproveAll, loading, loadingMessage }) => {
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');

  const handleEditClick = (id, currentValue) => {
    setEditingId(id);
    setEditValue(currentValue);
  };

  const handleSaveEdit = (id) => {
    onSetValue(id, editValue);
    setEditingId(null);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
  };

  const approvedCount = suggestions.filter((s) =>
    ['approved', 'edited'].includes(s.status)
  ).length;

  if (suggestions.length === 0) {
    return (
      <div className="step-container">
        <h2>3. Revisão de Sugestões da IA</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
          Nenhuma ambiguidade de texto encontrada nesta planilha.
        </p>
        <button
          className="btn btn-primary"
          onClick={onApply}
          disabled={loading}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          {loading ? 'Aplicando...' : 'Continuar →'}
        </button>
        {loading && loadingMessage && (
          <p style={{ marginTop: '0.75rem', fontSize: '0.82rem', color: 'var(--text-muted)', textAlign: 'center', animation: 'fadeIn 0.4s ease' }}>
            ⏳ {loadingMessage}
          </p>
        )}
        <style>{`@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }`}</style>
      </div>
    );
  }


  return (
    <div className="step-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.5rem' }}>
        <h2 style={{ margin: 0 }}>3. Revisão de Sugestões da IA</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {approvedCount}/{suggestions.length} decididos
          </span>
          <button 
            className="btn btn-action btn-success" 
            onClick={onApproveAll}
            title="Aprovar todas as sugestões com o valor sugerido"
          >
            Aprovar todos
          </button>
        </div>
      </div>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
        Nossa IA encontrou algumas inconsistências de texto. Por favor, aprove, edite ou rejeite as sugestões.
      </p>

      <div className="suggestion-list">
        {suggestions.map((item) => {
          const isApproved = item.status === 'approved';
          const isRejected = item.status === 'rejected';
          const isEdited   = item.status === 'edited';
          const isEditing  = editingId === item.id;

          return (
            <div key={item.id} className="suggestion-item">
              <div className="suggestion-details">
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Coluna: {item.column}
                </span>

                {/* Variants row */}
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0.25rem 0' }}>
                  Variações: {item.variants.join(' / ')}
                </div>

                {isEditing ? (
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '0.5rem' }}>
                    <span style={{ color: 'var(--danger)', textDecoration: 'line-through' }}>"{item.suggestedCanonical}"</span>
                    <span>→</span>
                    <input
                      type="text"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      style={{ padding: '0.25rem 0.5rem', borderRadius: '0.25rem', border: '1px solid var(--border)', background: 'var(--bg-color)', color: 'var(--text-color)' }}
                      autoFocus
                    />
                  </div>
                ) : (
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginTop: '0.5rem' }}>
                    {!isRejected && (
                      <>
                        <span style={{ color: 'var(--danger)', textDecoration: 'line-through' }}>"{item.variants[0]}"</span>
                        <span>→</span>
                        <span style={{ color: 'var(--success)', fontWeight: 'bold' }}>
                          "{isEdited ? item.finalValue : item.suggestedCanonical}"
                        </span>
                        {isEdited && <span style={{ fontSize: '0.75rem', color: 'var(--primary)' }}>(editado)</span>}
                      </>
                    )}
                    {isRejected && (
                      <span style={{ color: 'var(--text-muted)' }}>Mantém original (rejeitado)</span>
                    )}
                  </div>
                )}
              </div>

              <div className="suggestion-actions">
                {isEditing ? (
                  <>
                    <button className="btn btn-action btn-success" onClick={() => handleSaveEdit(item.id)}>Salvar</button>
                    <button className="btn btn-action btn-secondary" onClick={handleCancelEdit}>Cancelar</button>
                  </>
                ) : (
                  <>
                    <button
                      className={`btn btn-action btn-success ${isApproved ? 'active' : ''}`}
                      onClick={() => onSetStatus(item.id, 'approved')}
                    >
                      Aprovar
                    </button>

                    <button
                      className={`btn btn-action btn-warning ${isEdited ? 'active' : ''}`}
                      onClick={() => handleEditClick(item.id, item.finalValue)}
                    >
                      Editar
                    </button>

                    <button
                      className={`btn btn-action btn-danger ${isRejected ? 'active' : ''}`}
                      onClick={() => onSetStatus(item.id, 'rejected')}
                    >
                      Rejeitar
                    </button>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <button
        className="btn btn-primary"
        onClick={onApply}
        disabled={loading}
        style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
      >
        {loading && (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ animation: 'spin 1s linear infinite' }}>
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
        )}
        {loading ? 'Aplicando...' : 'Aplicar decisões →'}
      </button>

      {loading && loadingMessage && (
        <p style={{
          marginTop: '0.75rem',
          fontSize: '0.82rem',
          color: 'var(--text-muted)',
          textAlign: 'center',
          animation: 'fadeIn 0.4s ease',
        }}>
          ⏳ {loadingMessage}
        </p>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
};

export default Step3Suggestions;
