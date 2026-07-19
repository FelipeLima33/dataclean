import React, { useEffect } from 'react';

const MainLayout = ({ 
  children, 
  currentStep, 
  maxStepVisited,
  onStepClick, 
  onNext, 
  onPrev,
  error,
  theme,
  toggleTheme,
}) => {
  const steps = [
    { id: 1, label: 'Upload' },
    { id: 2, label: 'Diagnóstico' },
    { id: 3, label: 'Sugestões IA' },
    { id: 4, label: 'Gráficos' },
    { id: 5, label: 'Resultado' }
  ];

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [currentStep]);

  return (
    <div className="layout-container">
      <header className="header">
        <h1>DataClean</h1>
        <button 
          className="theme-toggle-btn" 
          onClick={toggleTheme} 
          aria-label="Alternar tema"
          title={theme === 'light' ? 'Mudar para tema escuro' : 'Mudar para tema claro'}
        >
          {theme === 'light' ? (
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
          ) : (
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
          )}
        </button>
        <div className="progress-bar">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <button
                className={`step-indicator ${currentStep === step.id ? 'active' : ''} ${currentStep > step.id ? 'completed' : ''}`}
                onClick={() => onStepClick(step.id)}
                disabled={step.id > maxStepVisited}
              >
                <div className="step-circle">{step.id}</div>
                <span>{step.label}</span>
              </button>
              {index < steps.length - 1 && (
                <div className={`step-line ${currentStep > step.id ? 'active' : ''}`}></div>
              )}
            </React.Fragment>
          ))}
        </div>
      </header>

      <main className="main-content">
        {error && (
          <div style={{
            margin: '0 0 1.5rem',
            padding: '0.75rem 1rem',
            borderRadius: '0.5rem',
            background: 'rgba(239,68,68,0.12)',
            border: '1px solid #ef4444',
            color: '#fca5a5',
            fontSize: '0.875rem',
          }}>
            ⚠ {error}
          </div>
        )}
        {children}
      </main>

      <footer className="footer">
        <button 
          className="btn btn-secondary" 
          onClick={onPrev}
          disabled={currentStep === 1}
        >
          Voltar
        </button>
        <button 
          className="btn btn-primary" 
          onClick={onNext}
          disabled={currentStep === steps.length}
        >
          {currentStep === steps.length - 1 ? 'Finalizar' : 'Continuar'}
        </button>
      </footer>
    </div>
  );
};

export default MainLayout;
