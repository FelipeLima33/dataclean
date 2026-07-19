import React from 'react';

export const MapPlaceholder = ({ title }) => {
  return (
    <div className="card" style={{ marginBottom: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px', backgroundColor: '#0f172a', border: '1px dashed #334155' }}>
      <h3 style={{ color: '#64748b', marginBottom: '1rem' }}>{title}</h3>
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '1rem' }}>
        <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon>
        <line x1="9" y1="3" x2="9" y2="18"></line>
        <line x1="15" y1="6" x2="15" y2="21"></line>
      </svg>
      <p style={{ color: '#94a3b8', fontSize: '14px', textAlign: 'center' }}>
        Mapa geográfico será implementado futuramente.
      </p>
    </div>
  );
};

export const WordCloudPlaceholder = ({ title }) => {
  return (
    <div className="card" style={{ marginBottom: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px', backgroundColor: '#0f172a', border: '1px dashed #334155' }}>
      <h3 style={{ color: '#64748b', marginBottom: '1rem' }}>{title}</h3>
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '1rem' }}>
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
      <p style={{ color: '#94a3b8', fontSize: '14px', textAlign: 'center' }}>
        Nuvem de palavras (Wordcloud) será implementada futuramente.
      </p>
    </div>
  );
};
