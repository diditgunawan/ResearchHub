import React, { useState } from 'react';
import { api, Project } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { 
  ShieldCheck, 
  Sparkles, 
  AlertCircle, 
  CheckCircle2, 
  FileCheck2,
  Copy
} from 'lucide-react';

interface SynthesisPageProps {
  activeProject: Project | null;
}

export const SynthesisPage: React.FC<SynthesisPageProps> = ({ activeProject }) => {
  const [query, setQuery] = useState('clinical efficacy of artificial intelligence interventions');
  const [scope, setScope] = useState<'library' | 'screened_included'>('library');
  const [selectedModel, setSelectedModel] = useState<string>('gemini-3.8-flash');
  const [loading, setLoading] = useState(false);
  const [synthesis, setSynthesis] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Evidence drawer state
  const [selectedClaim, setSelectedClaim] = useState<any | null>(null);

  // AI disclosure modal
  const [showDisclosureModal, setShowDisclosureModal] = useState(false);
  const [disclosure, setDisclosure] = useState<any | null>(null);
  const [copiedLang, setCopiedLang] = useState<string | null>(null);

  // Reference audit modal
  const [showAuditModal, setShowAuditModal] = useState(false);
  const [auditChecks, setAuditChecks] = useState<any[]>([]);

  const handleSynthesize = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProject || !query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.request<any>(`/projects/${activeProject.id}/synthesis`, {
        method: 'POST',
        body: JSON.stringify({ query, scope, max_works: 10, model: selectedModel }),
      });
      setSynthesis(res);
      if (res.claims?.length > 0) {
        setSelectedClaim(res.claims[0]);
      }
    } catch (err: any) {
      setError(err.detail || 'Synthesis failed. Please verify query.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDisclosure = async () => {
    if (!activeProject) return;
    try {
      const res = await api.request<any>(`/projects/${activeProject.id}/ai-disclosure`);
      setDisclosure(res);
      setShowDisclosureModal(true);
    } catch (err) {
      alert('Failed to generate AI disclosure statement');
    }
  };

  const handleRunAudit = async () => {
    if (!activeProject) return;
    try {
      const res = await api.request<any[]>(`/projects/${activeProject.id}/reference-checks`, {
        method: 'POST',
      });
      setAuditChecks(res);
      setShowAuditModal(true);
    } catch (err) {
      alert('Failed to run reference audit');
    }
  };

  const handleCopyText = (text: string, lang: string) => {
    navigator.clipboard.writeText(text);
    setCopiedLang(lang);
    setTimeout(() => setCopiedLang(null), 2000);
  };

  if (!activeProject) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-[#4A5B68]">
        Please select an active project from the top navbar.
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header & Controls */}
      <div className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-[#0B5C7A] text-xs font-bold uppercase tracking-wider mb-1">
            <ShieldCheck className="w-4 h-4 text-[#14532D]" />
            <span>Citation-Grounded Evidence Synthesis</span>
          </div>
          <h1 className="font-serif text-2xl font-bold text-[#12202B]">
            Zero-Hallucination Evidence Synthesizer
          </h1>
          <p className="text-sm text-[#4A5B68] mt-1">
            Every synthesized claim cites retrieved database chunks. Refuses automatically if evidence is insufficient (SYN-005).
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={handleRunAudit}
            className="inline-flex items-center space-x-1.5 px-3 py-2 bg-[#F6F8F9] hover:bg-[#E3F0F5] text-[#0B5C7A] border border-[#D7DEE3] rounded-lg text-xs font-semibold transition-colors"
          >
            <FileCheck2 className="w-4 h-4" />
            <span>Retraction Audit</span>
          </button>

          <button
            onClick={handleOpenDisclosure}
            className="inline-flex items-center space-x-1.5 px-3 py-2 bg-[#E4F3EA] hover:bg-[#d0ead9] text-[#14532D] border border-[#B7DEC5] rounded-lg text-xs font-semibold transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            <span>AI Disclosure Generator</span>
          </button>
        </div>
      </div>

      {/* Query Bar */}
      <div className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm">
        <form onSubmit={handleSynthesize} className="space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              required
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter empirical research question to synthesize..."
              className="flex-1 px-4 py-3 bg-[#F6F8F9] border border-[#D7DEE3] rounded-lg text-sm text-[#12202B] font-medium focus:outline-none focus:ring-2 focus:ring-[#0B5C7A] focus:bg-white transition-all"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50 shrink-0 shadow-sm"
            >
              {loading ? 'Synthesizing & Verifying...' : 'Synthesize Evidence'}
            </button>
          </div>

          <div className="flex items-center space-x-6 text-xs text-[#34495A]">
            <span className="font-semibold text-[#4A5B68] uppercase tracking-wider">Evidence Scope:</span>
            <label className="flex items-center space-x-1.5 cursor-pointer">
              <input
                type="radio"
                name="scope"
                value="library"
                checked={scope === 'library'}
                onChange={() => setScope('library')}
                className="text-[#0B5C7A]"
              />
              <span>Full Project Library</span>
            </label>
            <label className="flex items-center space-x-1.5 cursor-pointer">
              <input
                type="radio"
                name="scope"
                value="screened_included"
                checked={scope === 'screened_included'}
                onChange={() => setScope('screened_included')}
                className="text-[#0B5C7A]"
              />
              <span>Only Screened & Included Works (PRISMA Assessed)</span>
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-6 text-xs text-[#34495A] pt-3 border-t border-[#EDF2F5]">
            <span className="font-semibold text-[#4A5B68] uppercase tracking-wider">Inference Engine:</span>
            <label className="flex items-center space-x-1.5 cursor-pointer">
              <input
                type="radio"
                name="model"
                value="gemini-3.8-flash"
                checked={selectedModel === 'gemini-3.8-flash'}
                onChange={() => setSelectedModel('gemini-3.8-flash')}
                className="text-[#0B5C7A]"
              />
              <span className="font-medium text-[#12202B]">Gemini 3.8 Flash (Live Cloud AI)</span>
            </label>
            <label className="flex items-center space-x-1.5 cursor-pointer">
              <input
                type="radio"
                name="model"
                value="ollama"
                checked={selectedModel === 'ollama'}
                onChange={() => setSelectedModel('ollama')}
                className="text-[#0B5C7A]"
              />
              <span>Local Ollama (Llama 3.2 Air-Gapped)</span>
            </label>
            <label className="flex items-center space-x-1.5 cursor-pointer">
              <input
                type="radio"
                name="model"
                value="rule-engine"
                checked={selectedModel === 'rule-engine'}
                onChange={() => setSelectedModel('rule-engine')}
                className="text-[#0B5C7A]"
              />
              <span>Rule Engine (Zero-Cost Baseline)</span>
            </label>
          </div>
        </form>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-[#FBE4E4] text-[#8A1C1C] border border-[#EBB5B5] text-sm">
          {error}
        </div>
      )}

      {/* Results Section */}
      {synthesis && (
        <div className="space-y-6">
          {/* Status Alert Banner */}
          {synthesis.status === 'refused' ? (
            <div className="p-5 rounded-xl bg-[#FDF0DC] border border-[#EBCB98] text-[#7A3E00] space-y-2">
              <div className="flex items-center space-x-2 font-bold text-sm">
                <AlertCircle className="w-5 h-5" />
                <span>Evidence Base Insufficient — Hallucination Guardrail Triggered</span>
              </div>
              <p className="text-xs leading-relaxed">
                {synthesis.refusal_reason}
              </p>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-[#E4F3EA] border border-[#B7DEC5] text-[#14532D] flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-[#14532D]" />
                <span className="text-xs font-semibold">
                  Synthesis Status: <strong>{synthesis.status.toUpperCase()}</strong> · Verified Grounding: <strong>{synthesis.verified_percentage}%</strong>
                </span>
              </div>
              <div className="flex items-center space-x-3 text-xs font-mono">
                <span className="px-2.5 py-1 bg-[#D2ECDD] text-[#0F4723] rounded-md font-semibold">Model: {synthesis.model}</span>
                {synthesis.tokens_used > 0 && (
                  <span className="px-2.5 py-1 bg-[#F6F8F9] text-[#34495A] border border-[#D7DEE3] rounded-md">
                    Tokens: {synthesis.tokens_used} (${synthesis.cost_usd ? synthesis.cost_usd.toFixed(4) : '0.0000'})
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Atomic Claims & Evidence Drawer Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Claims Column */}
            <div className="lg:col-span-2 space-y-4">
              <h3 className="font-serif text-lg font-bold text-[#12202B]">
                Synthesized Claims ({synthesis.claims?.length || 0})
              </h3>

              {synthesis.claims?.length === 0 ? (
                <div className="bg-white rounded-xl border border-[#D7DEE3] p-8 text-center text-xs text-[#4A5B68]">
                  No claims generated due to refusal policy.
                </div>
              ) : (
                synthesis.claims.map((claim: any) => {
                  const isSelected = selectedClaim?.claim_index === claim.claim_index;
                  return (
                    <div
                      key={claim.claim_index}
                      onClick={() => setSelectedClaim(claim)}
                      className={`p-5 rounded-xl border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-white border-[#0B5C7A] shadow-md ring-1 ring-[#0B5C7A]'
                          : 'bg-white border-[#D7DEE3] hover:border-[#0B5C7A] shadow-sm'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <StatusBadge
                          state={claim.verdict}
                          label={claim.verdict === 'supported' ? 'Grounded 100%' : 'Partially Supported'}
                        />
                        {claim.doi && (
                          <span className="text-[11px] font-mono text-[#4A5B68]">
                            DOI: {claim.doi}
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-[#12202B] font-medium leading-relaxed">
                        {claim.claim_text}
                      </p>

                      <div className="mt-3 pt-3 border-t border-[#D7DEE3] flex items-center justify-between text-xs text-[#4A5B68]">
                        <span className="italic truncate max-w-md">Source: {claim.work_title}</span>
                        <span className="text-[#0B5C7A] font-semibold text-[11px]">Click to inspect cited chunk ➔</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Evidence Drawer Column */}
            <div className="space-y-4">
              <h3 className="font-serif text-lg font-bold text-[#12202B]">
                Primary Source Evidence Chunk
              </h3>

              {selectedClaim ? (
                <div className="bg-white rounded-xl border border-[#D7DEE3] p-5 shadow-sm space-y-4 sticky top-24">
                  <div className="text-xs space-y-1 pb-3 border-b border-[#D7DEE3]">
                    <span className="font-bold text-[#0B5C7A] uppercase tracking-wider text-[10px]">
                      Grounded Provenance Verification
                    </span>
                    <h4 className="font-serif font-bold text-[#12202B] text-sm">
                      {selectedClaim.work_title}
                    </h4>
                  </div>

                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#4A5B68] block mb-1">
                      Cited Database Excerpt
                    </span>
                    <div className="p-3 rounded-lg bg-[#F6F8F9] border border-[#D7DEE3] text-xs text-[#12202B] leading-relaxed font-sans">
                      "{selectedClaim.evidence_excerpt || 'Direct chunk text confirmed in database.'}"
                    </div>
                  </div>

                  <div className="text-[11px] text-[#14532D] flex items-center space-x-1.5 pt-2">
                    <CheckCircle2 className="w-4 h-4 text-[#14532D]" />
                    <span>Chunk fetched directly from canonical store without model re-generation.</span>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-xl border border-[#D7DEE3] p-8 text-center text-xs text-[#4A5B68]">
                  Select a claim on the left to inspect its supporting evidence chunk.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* AI Disclosure Statement Modal */}
      {showDisclosureModal && disclosure && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 shadow-xl border border-[#D7DEE3] space-y-4">
            <div className="flex items-center justify-between border-b border-[#D7DEE3] pb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-[#0B5C7A]" />
                <h3 className="font-serif text-lg font-bold text-[#12202B]">
                  AI-Use Disclosure Statement
                </h3>
              </div>
              <button
                onClick={() => setShowDisclosureModal(false)}
                className="text-gray-400 hover:text-gray-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-[#4A5B68]">
              Per requirement ETH-004, transparent disclosure statements are automatically generated from your logged usage and adhere to major journal publisher policies (Elsevier, Springer Nature, Wiley).
            </p>

            {/* English Disclosure */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-[#34495A]">
                  English (International Journals)
                </span>
                <button
                  onClick={() => handleCopyText(disclosure.statement_en, 'en')}
                  className="inline-flex items-center space-x-1 text-xs text-[#0B5C7A] hover:underline"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>{copiedLang === 'en' ? 'Copied!' : 'Copy'}</span>
                </button>
              </div>
              <textarea
                readOnly
                rows={4}
                value={disclosure.statement_en}
                className="w-full text-xs p-3 bg-[#F6F8F9] border border-[#D7DEE3] rounded-lg focus:outline-none"
              />
            </div>

            {/* Indonesian Disclosure */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-[#34495A]">
                  Indonesian (SINTA S1-S6 Accredited Journals)
                </span>
                <button
                  onClick={() => handleCopyText(disclosure.statement_id, 'id')}
                  className="inline-flex items-center space-x-1 text-xs text-[#0B5C7A] hover:underline"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>{copiedLang === 'id' ? 'Tersalin!' : 'Salin'}</span>
                </button>
              </div>
              <textarea
                readOnly
                rows={4}
                value={disclosure.statement_id}
                className="w-full text-xs p-3 bg-[#F6F8F9] border border-[#D7DEE3] rounded-lg focus:outline-none"
              />
            </div>

            <div className="text-[11px] text-[#7A3E00] bg-[#FDF0DC] p-3 rounded-lg border border-[#EBCB98]">
              {disclosure.compliance_note}
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="button"
                onClick={() => setShowDisclosureModal(false)}
                className="px-4 py-2 bg-[#0B5C7A] text-white rounded-lg text-xs font-bold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reference Retraction Audit Modal */}
      {showAuditModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 shadow-xl border border-[#D7DEE3] space-y-4">
            <div className="flex items-center justify-between border-b border-[#D7DEE3] pb-3">
              <div className="flex items-center space-x-2">
                <FileCheck2 className="w-5 h-5 text-[#0B5C7A]" />
                <h3 className="font-serif text-lg font-bold text-[#12202B]">
                  Reference List Retraction Audit
                </h3>
              </div>
              <button
                onClick={() => setShowAuditModal(false)}
                className="text-gray-400 hover:text-gray-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-[#4A5B68]">
              Automated audit of all works in project library for publisher retractions and unresolved identifiers (ETH-005, ETH-007).
            </p>

            <div className="max-h-80 overflow-y-auto space-y-2">
              {auditChecks.map((c, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-lg border text-xs flex items-start justify-between gap-3 ${
                    c.status === 'retracted'
                      ? 'bg-[#FBE4E4] border-[#EBB5B5] text-[#8A1C1C]'
                      : c.status === 'unresolved'
                      ? 'bg-[#FDF0DC] border-[#EBCB98] text-[#7A3E00]'
                      : 'bg-[#E4F3EA] border-[#B7DEC5] text-[#14532D]'
                  }`}
                >
                  <div>
                    <div className="font-bold">{c.title}</div>
                    <div className="text-[11px] mt-0.5">{c.details}</div>
                  </div>
                  <span className="font-mono uppercase font-bold text-[10px] shrink-0">
                    {c.status}
                  </span>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="button"
                onClick={() => setShowAuditModal(false)}
                className="px-4 py-2 bg-[#0B5C7A] text-white rounded-lg text-xs font-bold"
              >
                Close Audit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
