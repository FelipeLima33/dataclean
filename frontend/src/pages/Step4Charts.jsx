import React, { useEffect, useState } from 'react';
import BarChart from '../components/charts/BarChart';
import Histogram from '../components/charts/Histogram';
import BoxPlot from '../components/charts/BoxPlot';
import CorrelationHeatmap from '../components/charts/CorrelationHeatmap';
import Timeline from '../components/charts/Timeline';
import DataQualityChart from '../components/charts/DataQualityChart';
import BeforeAfterChart from '../components/charts/BeforeAfterChart';
import { MapPlaceholder, WordCloudPlaceholder } from '../components/charts/Placeholders';

const Step4Charts = ({ datasetId, onNext }) => {
  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!datasetId) {
      setError("Nenhum dataset disponível para análise.");
      setLoading(false);
      return;
    }

    const fetchCharts = async () => {
      try {
        const res = await fetch(`/api/charts/${datasetId}`);
        if (!res.ok) {
          throw new Error('Falha ao carregar gráficos.');
        }
        const data = await res.json();
        setCharts(data.charts || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCharts();
  }, [datasetId]);

  const renderChart = (chart) => {
    switch (chart.type) {
      case 'barras':
        return <BarChart key={chart.id} data={chart.data} title={chart.title} />;
      case 'histograma':
        return <Histogram key={chart.id} data={chart.data} title={chart.title} />;
      case 'boxplot':
        return <BoxPlot key={chart.id} data={chart.data} title={chart.title} />;
      case 'heatmap_correlacao':
        return <CorrelationHeatmap key={chart.id} data={chart.data} columns={chart.columns} title={chart.title} />;
      case 'linha_temporal':
        return <Timeline key={chart.id} data={chart.data} title={chart.title} />;
      case 'grafico_qualidade_dados':
        return <DataQualityChart key={chart.id} data={chart.data} percentual_nulo={chart.percentual_nulo} title={chart.title} />;
      case 'before_after':
        return <BeforeAfterChart key={chart.id} data={chart.data} title={chart.title} />;
      case 'mapa':
        return <MapPlaceholder key={chart.id} title={chart.title} />;
      case 'wordcloud':
        return <WordCloudPlaceholder key={chart.id} title={chart.title} />;
      default:
        return null;
    }
  };

  return (
    <div className="step-container">
      <h2>4. Visualizações Automáticas</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Insights gerados automaticamente a partir dos seus dados limpos.</p>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ animation: 'spin 1s linear infinite', margin: '0 auto 1rem' }}>
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
          <p>Analisando o dataset e gerando gráficos...</p>
        </div>
      ) : error ? (
        <div style={{ padding: '1.5rem', backgroundColor: 'transparent', border: '1px solid var(--danger)', borderRadius: '8px', color: 'var(--danger)' }}>
          <p>⚠ {error}</p>
        </div>
      ) : (
        <div className="charts-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
          {charts.map(renderChart)}
        </div>
      )}

      <button
        className="btn btn-primary"
        onClick={onNext}
        style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        disabled={loading}
      >
        Ver Relatório Final →
      </button>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default Step4Charts;
