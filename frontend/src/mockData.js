export const mockPreviewData = {
  columns: ['ID', 'Nome Cliente', 'Cidade', 'Valor Compra', 'Data'],
  rows: [
    { id: 1, nome: 'João Silva', cidade: 'Belem', valor: '150.00', data: '2023-01-15' },
    { id: 2, nome: 'Maria Santos', cidade: 'BELÉM', valor: '200.50', data: '2023-01-16' },
    { id: 3, nome: 'Carlos Souza', cidade: 'belém', valor: '99.90', data: '2023-01-17' },
    { id: 4, nome: 'Ana Lima', cidade: 'São Paulo', valor: '350.00', data: '2023-01-18' },
    { id: 5, nome: 'Pedro Paulo', cidade: 'Sao Paulo', valor: '350.00', data: '2023-01-18' },
  ]
};

export const mockDiagnostic = {
  resolved: [
    { type: 'Linhas Duplicadas', count: 12, status: 'Resolvido', color: '#10b981' },
    { type: 'Valores Ausentes', count: 5, status: 'Preenchido (Média/Moda)', color: '#10b981' },
    { type: 'Outliers', count: 3, status: 'Ajustado', color: '#10b981' },
  ],
  pending: [
    { type: 'Inconsistências de Texto', count: 4, status: 'Revisão Necessária', color: '#f59e0b' },
  ]
};

export const mockSuggestions = [
  { id: 's1', column: 'Cidade', original: 'Belem', suggestion: 'Belém' },
  { id: 's2', column: 'Cidade', original: 'BELÉM', suggestion: 'Belém' },
  { id: 's3', column: 'Cidade', original: 'belém', suggestion: 'Belém' },
  { id: 's4', column: 'Cidade', original: 'Sao Paulo', suggestion: 'São Paulo' },
];

export const mockChartData = [
  { category: 'Eletrônicos', total: 15000 },
  { category: 'Móveis', total: 12000 },
  { category: 'Vestuário', total: 8000 },
  { category: 'Alimentos', total: 5000 },
  { category: 'Livros', total: 3000 },
];

export const mockResultNarrative = `
  A análise do arquivo revelou um total de 24 problemas na estrutura dos dados originais. 
  Foram removidas 12 linhas duplicadas e 5 valores ausentes foram preenchidos utilizando 
  técnicas estatísticas adequadas. Além disso, identificamos 3 valores atípicos (outliers) 
  que foram ajustados para manter a consistência da distribuição.
  
  Graças à sua revisão, 4 inconsistências de texto nas colunas de categoria e cidade 
  foram padronizadas com sucesso. O dataset agora está 100% limpo e pronto para 
  análises avançadas e modelagem de machine learning.
`;
