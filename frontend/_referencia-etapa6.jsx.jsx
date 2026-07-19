import { useState } from "react";
import {
  Upload as UploadIcon,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Pencil,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Loader2,
  Check,
} from "lucide-react";

// Ajuste isso pra URL do seu backend em produção quando fizer o deploy
const API_BASE = "http://localhost:8000";

const SCREENS = [
  { id: 1, label: "Upload" },
  { id: 2, label: "Diagnóstico" },
  { id: 3, label: "Sugestões IA" },
  { id: 4, label: "Resultado" },
];

export default function DataCleanApp() {
  const [screen, setScreen] = useState(1);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Resposta de /api/clean/resolve-ambiguous
  const [diagnostics, setDiagnostics] = useState(null);
  const [previewRows, setPreviewRows] = useState([]);
  const [providerUsed, setProviderUsed] = useState(null);

  // Sugestões viram uma lista achatada (uma entrada por grupo),
  // fácil de renderizar e de atualizar o status individualmente
  const [suggestions, setSuggestions] = useState([]);

  // Resultado final, depois de aplicar as decisões
  const [finalResult, setFinalResult] = useState(null);

  const goTo = (id) => setScreen(id);

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/clean/resolve-ambiguous`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || `Erro ${res.status}`);
      }

      const data = await res.json();
      setDiagnostics(data.diagnostics);
      setProviderUsed(data.provider_used);

      // Achata ai_decisions (agrupado por coluna) numa lista simples
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
            status: "pending", // pending | approved | edited | rejected
          });
        });
      }
      setSuggestions(flat);
      setScreen(2);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function setSuggestionStatus(id, status) {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status } : s))
    );
  }

  function setSuggestionValue(id, value) {
    setSuggestions((prev) =>
      prev.map((s) =>
        s.id === id ? { ...s, finalValue: value, status: "edited" } : s
      )
    );
  }

  async function handleApplyDecisions() {
    setLoading(true);
    setError(null);

    try {
      const decisions = suggestions.map((s) => ({
        column: s.column,
        variants: s.variants,
        status: s.status === "pending" ? "rejected" : s.status,
        final_value: s.finalValue,
      }));

      const formData = new FormData();
      formData.append("file", file);
      formData.append("decisions", JSON.stringify(decisions));

      const res = await fetch(`${API_BASE}/api/clean/apply-decisions`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || `Erro ${res.status}`);
      }

      const data = await res.json();
      setFinalResult(data);
      setPreviewRows(data.cleaned_preview);
      setScreen(4);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const approvedCount = suggestions.filter((s) =>
    ["approved", "edited"].includes(s.status)
  ).length;

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900 flex flex-col">
      <header className="border-b border-neutral-200 bg-white">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center gap-2 mb-4">
            <FileSpreadsheet size={20} className="text-neutral-700" />
            <span className="font-semibold tracking-tight">DataClean</span>
            <span className="text-xs text-neutral-400 ml-2">
              conectado ao backend real
            </span>
          </div>
          <nav className="flex items-center">
            {SCREENS.map((s, i) => (
              <div key={s.id} className="flex items-center flex-1 last:flex-none">
                <div className="flex items-center gap-2 text-sm">
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium shrink-0 ${screen === s.id
                        ? "bg-neutral-900 text-white"
                        : screen > s.id
                          ? "bg-emerald-100 text-emerald-700"
                          : "border border-neutral-300 text-neutral-400"
                      }`}
                  >
                    {screen > s.id ? <Check size={12} /> : s.id}
                  </span>
                  <span
                    className={
                      screen === s.id ? "text-neutral-900 font-medium" : "text-neutral-400"
                    }
                  >
                    {s.label}
                  </span>
                </div>
                {i < SCREENS.length - 1 && (
                  <div className="flex-1 h-px bg-neutral-200 mx-3" />
                )}
              </div>
            ))}
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto px-6 py-10">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg p-4">
            {error}
          </div>
        )}

        {screen === 1 && (
          <ScreenUpload
            file={file}
            setFile={setFile}
            onUpload={handleUpload}
            loading={loading}
          />
        )}

        {screen === 2 && diagnostics && (
          <ScreenDiagnostico
            diagnostics={diagnostics}
            providerUsed={providerUsed}
            onNext={() => setScreen(3)}
          />
        )}

        {screen === 3 && (
          <ScreenSugestoes
            suggestions={suggestions}
            setStatus={setSuggestionStatus}
            setValue={setSuggestionValue}
            approvedCount={approvedCount}
            onApply={handleApplyDecisions}
            loading={loading}
          />
        )}

        {screen === 4 && finalResult && (
          <ScreenResultado result={finalResult} previewRows={previewRows} />
        )}
      </main>
    </div>
  );
}

function Card({ children, className = "" }) {
  return (
    <div className={`bg-white border border-neutral-200 rounded-lg ${className}`}>
      {children}
    </div>
  );
}

function ScreenUpload({ file, setFile, onUpload, loading }) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">1. Upload da planilha</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Envie um arquivo CSV ou Excel para começar o diagnóstico real.
        </p>
      </div>

      <label className="block border-2 border-dashed border-neutral-300 rounded-lg py-16 flex flex-col items-center justify-center gap-3 text-neutral-500 cursor-pointer hover:border-neutral-400 hover:bg-neutral-50 transition-colors">
        <input
          type="file"
          accept=".csv,.xlsx"
          className="hidden"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <UploadIcon size={28} />
        <p className="text-sm">
          {file ? file.name : "Clique para selecionar um arquivo"}
        </p>
        <p className="text-xs text-neutral-400">.csv, .xlsx</p>
      </label>

      <button
        onClick={onUpload}
        disabled={!file || loading}
        className="flex items-center gap-2 text-sm px-4 py-2 rounded-md bg-neutral-900 text-white disabled:opacity-30 hover:bg-neutral-800"
      >
        {loading && <Loader2 size={16} className="animate-spin" />}
        {loading ? "Processando..." : "Diagnosticar e limpar"}
      </button>
    </div>
  );
}

function ScreenDiagnostico({ diagnostics, providerUsed, onNext }) {
  const items = [
    { label: "Linhas antes", value: diagnostics.rows_before },
    { label: "Linhas depois", value: diagnostics.rows_after },
    { label: "Duplicatas removidas", value: diagnostics.duplicates_removed },
    { label: "Valores ausentes preenchidos", value: diagnostics.missing_values_filled },
    { label: "Outliers marcados", value: diagnostics.outliers_flagged },
    { label: "Inconsistências de texto", value: diagnostics.text_inconsistencies_found },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">2. Diagnóstico</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Resultado real da limpeza determinística.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {items.map((item) => (
          <Card key={item.label} className="p-4">
            <p className="text-xs text-neutral-500 mb-1">{item.label}</p>
            <p className="text-2xl font-semibold">{item.value}</p>
          </Card>
        ))}
      </div>

      {diagnostics.text_inconsistencies_found > 0 && (
        <Card className="p-4 flex items-center gap-3">
          <Sparkles size={16} className="text-neutral-500 shrink-0" />
          <p className="text-sm text-neutral-600">
            {diagnostics.text_inconsistencies_found} inconsistências revisadas
            pela IA
            {providerUsed && <> (provedor: <strong>{providerUsed}</strong>)</>} —
            vamos revisar cada uma na próxima tela.
          </p>
        </Card>
      )}

      <button
        onClick={onNext}
        className="flex items-center gap-2 text-sm px-4 py-2 rounded-md bg-neutral-900 text-white hover:bg-neutral-800"
      >
        Ver sugestões da IA <ArrowRight size={16} />
      </button>
    </div>
  );
}

function ScreenSugestoes({ suggestions, setStatus, setValue, approvedCount, onApply, loading }) {
  if (suggestions.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-xl font-semibold">3. Sugestões da IA</h1>
        <Card className="p-6 text-center text-sm text-neutral-500">
          Nenhuma ambiguidade de texto encontrada nesta planilha.
        </Card>
        <button
          onClick={onApply}
          className="flex items-center gap-2 text-sm px-4 py-2 rounded-md bg-neutral-900 text-white hover:bg-neutral-800"
        >
          Continuar <ArrowRight size={16} />
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">3. Sugestões da IA</h1>
          <p className="text-sm text-neutral-500 mt-1">
            Aprove, edite ou rejeite cada grupo de variações.
          </p>
        </div>
        <span className="text-xs text-neutral-400">
          {approvedCount}/{suggestions.length} decididos
        </span>
      </div>

      <div className="space-y-3">
        {suggestions.map((s) => (
          <Card key={s.id} className="p-4">
            <div className="flex items-center justify-between gap-4">
              <div className="min-w-0 flex-1">
                <p className="text-xs text-neutral-400 mb-1">
                  Coluna "{s.column}" — variações encontradas
                </p>
                <p className="text-sm text-neutral-600 truncate">
                  {s.variants.join(" / ")}
                </p>
                <p className="text-xs text-neutral-400 mt-2 mb-1">
                  Valor final {s.status === "edited" && "(editado)"}
                </p>
                <input
                  value={s.finalValue}
                  onChange={(e) => setValue(s.id, e.target.value)}
                  className="text-sm font-medium border border-neutral-200 rounded px-2 py-1 w-full max-w-xs"
                />
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => setStatus(s.id, "approved")}
                  className={`w-8 h-8 rounded-md flex items-center justify-center border ${s.status === "approved"
                      ? "bg-emerald-600 border-emerald-600 text-white"
                      : "border-neutral-300 text-neutral-400 hover:bg-neutral-50"
                    }`}
                  title="Aprovar"
                >
                  <CheckCircle2 size={16} />
                </button>
                <button
                  className={`w-8 h-8 rounded-md flex items-center justify-center border ${s.status === "edited"
                      ? "bg-blue-600 border-blue-600 text-white"
                      : "border-neutral-300 text-neutral-400"
                    }`}
                  title="Editado no campo ao lado"
                >
                  <Pencil size={16} />
                </button>
                <button
                  onClick={() => setStatus(s.id, "rejected")}
                  className={`w-8 h-8 rounded-md flex items-center justify-center border ${s.status === "rejected"
                      ? "bg-red-500 border-red-500 text-white"
                      : "border-neutral-300 text-neutral-400 hover:bg-neutral-50"
                    }`}
                  title="Rejeitar (mantém original)"
                >
                  <XCircle size={16} />
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <button
        onClick={onApply}
        disabled={loading}
        className="flex items-center gap-2 text-sm px-4 py-2 rounded-md bg-neutral-900 text-white disabled:opacity-30 hover:bg-neutral-800"
      >
        {loading && <Loader2 size={16} className="animate-spin" />}
        {loading ? "Aplicando..." : "Aplicar decisões"}
        {!loading && <ArrowRight size={16} />}
      </button>
    </div>
  );
}

function ScreenResultado({ result, previewRows }) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">4. Resultado</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Dataset final, com suas decisões aplicadas.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card className="p-4">
          <p className="text-xs text-neutral-400 mb-1">Total de linhas</p>
          <p className="text-2xl font-semibold">{result.rows_total}</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-neutral-400 mb-1">Inconsistências resolvidas</p>
          <p className="text-2xl font-semibold">
            {result.diagnostics.text_inconsistencies_resolved}
          </p>
        </Card>
      </div>

      <Card className="p-4">
        <p className="text-xs text-neutral-400 mb-3">Preview do dataset limpo</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-neutral-400 border-b border-neutral-200">
                {previewRows[0] &&
                  Object.keys(previewRows[0]).map((col) => (
                    <th key={col} className="py-2 pr-4 font-medium">
                      {col}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody>
              {previewRows.map((row, i) => (
                <tr key={i} className="border-b border-neutral-100 last:border-0">
                  {Object.values(row).map((val, j) => (
                    <td key={j} className="py-2 pr-4">
                      {String(val)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <p className="text-xs text-neutral-400">
        Gráficos e narrativa automática chegam nas próximas etapas (7 e 8).
      </p>
    </div>
  );
}
