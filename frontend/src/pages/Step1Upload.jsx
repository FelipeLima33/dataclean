import React from 'react';

const Step1Upload = ({ file, setFile, onUpload, loading, loadingMessage }) => {
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  };

  return (
    <div className="step-container">
      <h2>1. Faça upload do seu arquivo</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Arraste e solte uma planilha (CSV ou Excel) para começar a limpeza.</p>
      
      <label
        className="drag-drop-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        style={{ cursor: 'pointer', display: 'block' }}
      >
        <input
          type="file"
          accept=".csv,.xlsx"
          style={{ display: 'none' }}
          onChange={(e) => setFile(e.target.files[0])}
        />
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ margin: '0 auto 1rem', display: 'block', color: 'var(--text-muted)' }}>
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        <h3 style={{ color: 'var(--text-color)' }}>{file ? file.name : 'Arraste seu arquivo aqui'}</h3>
        <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          {file ? `${(file.size / 1024).toFixed(1)} KB — clique para trocar` : 'ou clique para selecionar do computador'}
        </p>
      </label>

      <button
        className="btn btn-primary"
        onClick={onUpload}
        disabled={!file || loading}
        style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
      >
        {loading && (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ animation: 'spin 1s linear infinite' }}>
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
        )}
        {loading ? 'Processando...' : 'Diagnosticar e limpar'}
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

export default Step1Upload;
