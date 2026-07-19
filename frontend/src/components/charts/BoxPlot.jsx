import React from 'react';

const BoxPlot = ({ data, title }) => {
  if (!data || data.length === 0) return null;
  
  const stat = data[0]; // { min, q1, median, q3, max, lower_fence, upper_fence, outliers }
  const range = stat.max - stat.min || 1;
  
  const toPct = (val) => ((val - stat.min) / range) * 100;
  
  const q1Pct = toPct(stat.q1);
  const q3Pct = toPct(stat.q3);
  const medPct = toPct(stat.median);
  const minPct = toPct(stat.lower_fence);
  const maxPct = toPct(stat.upper_fence);

  return (
    <div className="card" style={{ marginBottom: '1.5rem' }}>
      <h3 style={{ marginBottom: '1rem', color: '#64748b' }}>{title}</h3>
      <div style={{ padding: '2rem 1rem', height: '150px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        
        {/* Axis labels */}
        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>
          <span>{stat.min.toFixed(1)}</span>
          <span>{stat.max.toFixed(1)}</span>
        </div>

        {/* Boxplot container */}
        <div style={{ position: 'relative', width: '100%', height: '40px' }}>
          
          {/* Main line (whiskers) */}
          <div style={{ 
            position: 'absolute', 
            top: '50%', 
            left: `${minPct}%`, 
            right: `${100 - maxPct}%`, 
            height: '2px', 
            background: '#94a3b8', 
            transform: 'translateY(-50%)' 
          }} />
          
          {/* Left Whisker cap */}
          <div style={{ position: 'absolute', top: '25%', bottom: '25%', left: `${minPct}%`, width: '2px', background: '#94a3b8' }} />
          
          {/* Right Whisker cap */}
          <div style={{ position: 'absolute', top: '25%', bottom: '25%', left: `${maxPct}%`, width: '2px', background: '#94a3b8' }} />

          {/* Box (Q1 to Q3) */}
          <div style={{ 
            position: 'absolute', 
            top: '10%', 
            bottom: '10%', 
            left: `${q1Pct}%`, 
            width: `${q3Pct - q1Pct}%`, 
            background: '#34d399', 
            opacity: 0.8,
            border: '2px solid #059669',
            borderRadius: '4px'
          }} />

          {/* Median line */}
          <div style={{ position: 'absolute', top: '10%', bottom: '10%', left: `${medPct}%`, width: '2px', background: '#064e3b' }} />

          {/* Outliers */}
          {stat.outliers.map((val, idx) => (
            <div key={idx} style={{ 
              position: 'absolute', 
              top: '50%', 
              left: `${toPct(val)}%`, 
              width: '6px', 
              height: '6px', 
              background: '#ef4444', 
              borderRadius: '50%', 
              transform: 'translate(-50%, -50%)' 
            }} title={`Outlier: ${val.toFixed(2)}`} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default BoxPlot;
