import React, { useState, useRef, useEffect } from 'react';
import MainLayout from './layouts/MainLayout';
import Step1Upload from './pages/Step1Upload';
import Step2Diagnostic from './pages/Step2Diagnostic';
import Step3Suggestions from './pages/Step3Suggestions';
import Step4Charts from './pages/Step4Charts';
import Step5Result from './pages/Step5Result';

const API_BASE = ''; // vite proxy repassa /api/* → http://localhost:8000

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [maxStepVisited, setMaxStepVisited] = useState(1);

  // ── Theme state ───────────────────────────────────────────────────────────
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const initialTheme = prefersDark ? 'dark' : 'light';
      setTheme(initialTheme);
      document.documentElement.setAttribute('data-theme', initialTheme);
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };


  // ── Real data states ──────────────────────────────────────────────────────
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const loadingTimerRef = useRef(null);
  const [error, setError] = useState(null);

  // Filled by POST /api/clean/resolve-ambiguous
  const [diagnostics, setDiagnostics] = useState(null);
  const [providerUsed, setProviderUsed] = useState(null);

  // Flat list: one entry per ambiguity group (column + variants + canonical)
  const [suggestions, setSuggestions] = useState([]);

  // Filled by POST /api/clean/apply-decisions
  const [finalResult, setFinalResult] = useState(null);
  const [previewRows, setPreviewRows] = useState([]);
  const [datasetId, setDatasetId] = useState(null);

  // ── Navigation helpers ────────────────────────────────────────────────────
  const goToStep = (id) => {
    setCurrentStep(id);
    setMaxStepVisited((prev) => Math.max(prev, id));
  };

  const handleNext = () => {
    if (currentStep < 5) goToStep(currentStep + 1);
  };

  const handlePrev = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleStepClick = (stepId) => {
    if (stepId <= maxStepVisited) setCurrentStep(stepId);
  };

  // ── API calls ─────────────────────────────────────────────────────────────
  function startLoadingWithEscalation() {
    setLoading(true);
    setLoadingMessage('Processando...');
    // Após 5 s sem resposta, avisa que um provedor alternativo está sendo usado
    loadingTimerRef.current = setTimeout(() => {
      setLoadingMessage(
        'Processando com um provedor alternativo, isso pode levar até 30 segundos...'
      );
    }, 5000);
  }

  function stopLoading() {
    setLoading(false);
    setLoadingMessage('');
    if (loadingTimerRef.current) {
      clearTimeout(loadingTimerRef.current);
      loadingTimerRef.current = null;
    }
  }

  async function handleUpload() {
    if (!file) return;
    startLoadingWithEscalation();
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE}/api/clean/resolve-ambiguous`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || `Erro ${res.status}`);
      }

      const data = await res.json();
      setDiagnostics(data.diagnostics);
      setProviderUsed(data.provider_used);
      setDatasetId(data.dataset_id);

      // Flatten ai_decisions (grouped by column) into a simple list
      const flat = [];
      const aiDecisions = data.ai_decisions || {};
      for (const [column, groups] of Object.entries(aiDecisions)) {
        groups.forEach((group, i) => {
          flat.push({
            id: `${column}-${i}`,
            column,
            variants: group.variants,
            suggestedCanonical: group.canonical,
            shouldMerge: group.should_merge,
            finalValue: group.canonical,
            status: 'pending', // pending | approved | edited | rejected
          });
        });
      }
      setSuggestions(flat);

      // Advance to Diagnostic screen
      goToStep(2);
    } catch (e) {
      setError(e.message);
    } finally {
      stopLoading();
    }
  }

  function setSuggestionStatus(id, status) {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status } : s))
    );
  }

  function handleApproveAll() {
    setSuggestions((prev) =>
      prev.map((s) => ({ ...s, status: 'approved' }))
    );
  }

  function setSuggestionValue(id, value) {
    setSuggestions((prev) =>
      prev.map((s) =>
        s.id === id ? { ...s, finalValue: value, status: 'edited' } : s
      )
    );
  }

  async function handleApplyDecisions() {
    startLoadingWithEscalation();
    setError(null);

    try {
      console.log('SNAPSHOT suggestions no momento do apply:', 
        JSON.stringify(suggestions.map(s => ({ id: s.id, status: s.status })), null, 2));
      const decisions = suggestions.map((s) => ({
        column: s.column,
        variants: s.variants,
        status: s.status === 'pending' ? 'rejected' : s.status,
        final_value: s.finalValue,
      }));

      const formData = new FormData();
      formData.append('file', file);
      formData.append('decisions', JSON.stringify(decisions));
      formData.append('dataset_id', datasetId);

      const res = await fetch(`${API_BASE}/api/clean/apply-decisions`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || `Erro ${res.status}`);
      }

      const data = await res.json();
      setFinalResult(data);
      setPreviewRows(data.cleaned_preview || []);
      setDatasetId(data.dataset_id); // Save dataset ID for charts

      // Advance to Charts screen (step 4)
      goToStep(4);
    } catch (e) {
      setError(e.message);
    } finally {
      stopLoading();
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Step1Upload
            file={file}
            setFile={setFile}
            onUpload={handleUpload}
            loading={loading}
            loadingMessage={loadingMessage}
          />
        );
      case 2:
        return (
          <Step2Diagnostic
            diagnostics={diagnostics}
            onNext={() => goToStep(3)}
          />
        );
      case 3:
        return (
          <Step3Suggestions
            suggestions={suggestions}
            onSetStatus={setSuggestionStatus}
            onSetValue={setSuggestionValue}
            onApply={handleApplyDecisions}
            onApproveAll={handleApproveAll}
            loading={loading}
            loadingMessage={loadingMessage}
          />
        );
      case 4:
        return (
          <Step4Charts
            datasetId={datasetId}
            onNext={() => goToStep(5)}
          />
        );
      case 5:
        return (
          <Step5Result
            finalResult={finalResult}
            previewRows={previewRows}
            datasetId={datasetId}
          />
        );
      default:
        return (
          <Step1Upload
            file={file}
            setFile={setFile}
            onUpload={handleUpload}
            loading={loading}
          />
        );
    }
  };

  return (
    <MainLayout
      currentStep={currentStep}
      maxStepVisited={maxStepVisited}
      onNext={handleNext}
      onPrev={handlePrev}
      onStepClick={handleStepClick}
      error={error}
      theme={theme}
      toggleTheme={toggleTheme}
    >
      {renderCurrentStep()}
    </MainLayout>
  );
}

export default App;
