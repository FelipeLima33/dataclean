import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from 'recharts';

const CorrelationHeatmap = ({ data, columns, title }) => {
  // Map columns to numeric indices
  const colIndex = columns.reduce((acc, col, idx) => {
    acc[col] = idx;
    return acc;
  }, {});

  const plotData = data.map(d => ({
    xIndex: colIndex[d.x],
    yIndex: colIndex[d.y],
    x: d.x,
    y: d.y,
    value: d.value,
    // Use absolute value for circle size
    z: Math.abs(d.value)
  }));

  const renderTooltip = (props) => {
    const { active, payload } = props;
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{ backgroundColor: '#1e293b', padding: '10px', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc', fontSize: '12px' }}>
          <p><strong>{data.x}</strong> vs <strong>{data.y}</strong></p>
          <p style={{ color: data.value >= 0 ? '#34d399' : '#f87171' }}>
            Correlação: {data.value.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card" style={{ marginBottom: '1.5rem' }}>
      <h3 style={{ marginBottom: '1rem', color: '#64748b' }}>{title}</h3>
      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis 
              type="number" 
              dataKey="xIndex" 
              name="x" 
              domain={[0, columns.length - 1]}
              tickFormatter={(val) => columns[val]}
              tick={{ fontSize: 12, fill: '#94a3b8' }}
              tickCount={columns.length}
            />
            <YAxis 
              type="number" 
              dataKey="yIndex" 
              name="y" 
              domain={[0, columns.length - 1]}
              tickFormatter={(val) => columns[val]}
              tick={{ fontSize: 12, fill: '#94a3b8' }}
              tickCount={columns.length}
            />
            <ZAxis type="number" dataKey="z" range={[50, 400]} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} content={renderTooltip} />
            <Scatter data={plotData} fill="#818cf8" shape="circle" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <p style={{ fontSize: '12px', color: '#64748b', textAlign: 'center', marginTop: '10px' }}>
        Tamanho do círculo indica força da correlação.
      </p>
    </div>
  );
};

export default CorrelationHeatmap;
