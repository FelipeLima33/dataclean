import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = ['#10b981', '#f43f5e'];

const DataQualityChart = ({ data, percentual_nulo, title }) => {
  return (
    <div className="card" style={{ marginBottom: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <h3 style={{ marginBottom: '1rem', color: '#64748b', alignSelf: 'flex-start' }}>{title}</h3>
      <div style={{ position: 'relative', width: '100%', height: 250 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              innerRadius={60}
              outerRadius={90}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc' }}
            />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
        {/* Center Text */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -60%)',
          textAlign: 'center'
        }}>
          <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold', color: percentual_nulo > 0 ? '#f43f5e' : '#10b981' }}>
            {percentual_nulo}%
          </p>
          <p style={{ margin: 0, fontSize: '0.7rem', color: '#94a3b8' }}>Ausentes</p>
        </div>
      </div>
    </div>
  );
};

export default DataQualityChart;
