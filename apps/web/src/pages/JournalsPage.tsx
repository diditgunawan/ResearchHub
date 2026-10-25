import React, { useState, useEffect } from 'react';
import { Search, Sliders, ExternalLink, AlertCircle } from 'lucide-react';

interface Journal {
  id: string;
  openalex_id?: string;
  issn_l?: string;
  issns: string[];
  title: string;
  publisher?: string;
  country?: string;
  scope_text?: string;
  languages: string[];
  is_oa: boolean;
  in_doaj: boolean;
  apc_usd?: number;
  apc_note?: string;
  scopus_quartile?: string;
  sinta_rank?: string;
  guidelines_url?: string;
  data_as_of: string;
  provenance: Record<string, any>;
  recent_articles: { title: string; doi: string; year: number }[];
  keywords: string[];
  is_stale: boolean;
}

interface MatchRecommendation {
  journal: Journal;
  match_score: number;
  score_breakdown: {
    semantic_score: number;
    keyword_score: number;
    citation_affinity: number;
    composite_score: number;
  };
  similar_recent_articles: { title: string; doi: string; year: number }[];
  quality_signals: Record<string, any>;
}

interface ChecklistItem {
  item: string;
  requirement: string;
  source_url?: string;
  is_verifiable: boolean;
  status: string;
}

export const JournalsPage: React.FC = () => {
  const [journals, setJournals] = useState<Journal[]>([]);
  const [activeTab, setActiveTab] = useState<'directory' | 'matcher'>('matcher');

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedQuartile, setSelectedQuartile] = useState<string>('');
  const [selectedSinta, setSelectedSinta] = useState<string>('');
  const [requireOa, setRequireOa] = useState(false);
  const [requireDoaj, setRequireDoaj] = useState(false);
  const [maxApc, setMaxApc] = useState<number | undefined>(undefined);

  // Manuscript Matcher states
  const [msTitle, setMsTitle] = useState('');
  const [msAbstract, setMsAbstract] = useState('');
  const [matchingLoading, setMatchingLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<MatchRecommendation[]>([]);
  const [disclaimer, setDisclaimer] = useState<string>('');

  // Checklist modal state
  const [checklistModal, setChecklistModal] = useState<{
    open: boolean;
    journalTitle: string;
    items: ChecklistItem[];
    guidelinesUrl?: string;
  }>({ open: false, journalTitle: '', items: [] });

  const loadJournals = async () => {
    try {
      let url = '/journals?';
      if (searchQuery) url += `query=${encodeURIComponent(searchQuery)}&`;
      if (selectedQuartile) url += `quartiles=${selectedQuartile}&`;
      if (selectedSinta) url += `sinta_ranks=${selectedSinta}&`;
      if (requireOa) url += `require_oa=true&`;
      if (requireDoaj) url += `require_doaj=true&`;
      if (maxApc !== undefined) url += `max_apc_usd=${maxApc}&`;

      const res = await fetch(url);
      if (res.ok) {
        setJournals(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadJournals();
  }, [selectedQuartile, selectedSinta, requireOa, requireDoaj, maxApc]);

  const handleMatchManuscript = async () => {
    if (!msTitle || !msAbstract) return;
    setMatchingLoading(true);
    try {
      const res = await fetch('/journals/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: msTitle,
          abstract: msAbstract,
          quartiles: selectedQuartile ? [selectedQuartile] : undefined,
          sinta_ranks: selectedSinta ? [selectedSinta] : undefined,
          require_oa: requireOa ? true : undefined,
          require_doaj: requireDoaj ? true : undefined,
          max_apc_usd: maxApc,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data.recommendations || []);
        setDisclaimer(data.disclaimer);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setMatchingLoading(false);
    }
  };

  const handleOpenChecklist = async (journal: Journal) => {
    try {
      const res = await fetch(`/journals/${journal.id}/checklist`);
      if (res.ok) {
        const data = await res.json();
        setChecklistModal({
          open: true,
          journalTitle: journal.title,
          items: data.items,
          guidelinesUrl: data.guidelines_url,
        });
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="pb-6 border-b border-[#D7DEE3] mb-6 flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-serif font-bold text-[#12202B]">Journal Fit Matching & Verification</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#E3F0F5] text-[#0B4A63]">
              JRN-001..012 Compliant
            </span>
          </div>
          <p className="text-sm text-[#4A5B68] mt-1">
            Ground-truth indexing verification (DOAJ, Scopus, SINTA), APC transparency, and 3-component fit scoring.
          </p>
        </div>

        <div className="mt-4 md:mt-0 flex space-x-2">
          <button
            onClick={() => setActiveTab('matcher')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'matcher' ? 'bg-[#0B5C7A] text-white' : 'bg-white border border-[#D7DEE3] text-[#4A5B68]'
            }`}
          >
            Manuscript Matcher
          </button>
          <button
            onClick={() => setActiveTab('directory')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'directory' ? 'bg-[#0B5C7A] text-white' : 'bg-white border border-[#D7DEE3] text-[#4A5B68]'
            }`}
          >
            Browse Directory ({journals.length})
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Col: Filter Sidebar */}
        <div className="lg:col-span-1 bg-white p-5 rounded-lg border border-[#D7DEE3] h-fit space-y-5">
          <div className="flex items-center space-x-2 pb-3 border-b border-[#D7DEE3]">
            <Sliders className="w-4 h-4 text-[#0B5C7A]" />
            <h3 className="font-serif font-bold text-sm text-[#12202B]">Hard Scope Filters</h3>
          </div>

          {/* Scopus Quartile */}
          <div>
            <label className="block text-xs font-bold text-[#12202B] mb-2">Scopus Quartile</label>
            <div className="grid grid-cols-4 gap-1.5">
              {['Q1', 'Q2', 'Q3', 'Q4'].map((q) => (
                <button
                  key={q}
                  onClick={() => setSelectedQuartile(selectedQuartile === q ? '' : q)}
                  className={`py-1 text-xs font-bold rounded border transition-colors ${
                    selectedQuartile === q
                      ? 'bg-[#0B5C7A] text-white border-[#0B5C7A]'
                      : 'border-[#D7DEE3] text-[#4A5B68] hover:bg-gray-50'
                  }`}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* SINTA Rank */}
          <div>
            <label className="block text-xs font-bold text-[#12202B] mb-2">Indonesia SINTA Rank</label>
            <div className="grid grid-cols-3 gap-1.5">
              {['S1', 'S2', 'S3', 'S4', 'S5', 'S6'].map((s) => (
                <button
                  key={s}
                  onClick={() => setSelectedSinta(selectedSinta === s ? '' : s)}
                  className={`py-1 text-xs font-bold rounded border transition-colors ${
                    selectedSinta === s
                      ? 'bg-[#0B5C7A] text-white border-[#0B5C7A]'
                      : 'border-[#D7DEE3] text-[#4A5B68] hover:bg-gray-50'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* OA & Indexing Toggles */}
          <div className="space-y-2 pt-2 border-t border-[#D7DEE3]">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={requireOa}
                onChange={(e) => setRequireOa(e.target.checked)}
                className="rounded border-[#D7DEE3] text-[#0B5C7A]"
              />
              <span className="text-xs font-medium text-[#12202B]">Only Open Access (OA)</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={requireDoaj}
                onChange={(e) => setRequireDoaj(e.target.checked)}
                className="rounded border-[#D7DEE3] text-[#0B5C7A]"
              />
              <span className="text-xs font-medium text-[#12202B]">DOAJ Indexed</span>
            </label>
          </div>

          {/* Max APC Filter */}
          <div className="pt-2 border-t border-[#D7DEE3]">
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-bold text-[#12202B]">Max APC (USD)</label>
              <span className="text-xs font-mono text-[#0B5C7A]">
                {maxApc === undefined ? 'Any' : maxApc === 0 ? 'No APC ($0)' : `$${maxApc}`}
              </span>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setMaxApc(maxApc === 0 ? undefined : 0)}
                className={`px-2.5 py-1 text-xs rounded border ${
                  maxApc === 0 ? 'bg-[#0B5C7A] text-white' : 'border-[#D7DEE3]'
                }`}
              >
                Zero APC
              </button>
              <button
                onClick={() => setMaxApc(maxApc === 2000 ? undefined : 2000)}
                className={`px-2.5 py-1 text-xs rounded border ${
                  maxApc === 2000 ? 'bg-[#0B5C7A] text-white' : 'border-[#D7DEE3]'
                }`}
              >
                ≤ $2k
              </button>
              <button
                onClick={() => setMaxApc(undefined)}
                className="px-2 py-1 text-xs text-gray-500 hover:underline"
              >
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Right 3 Cols: Content Pages */}
        <div className="lg:col-span-3 space-y-6">
          {activeTab === 'matcher' ? (
            <div>
              {/* Matcher Input Card */}
              <div className="bg-white p-6 rounded-lg border border-[#D7DEE3] mb-6">
                <h3 className="font-serif font-bold text-base text-[#12202B] mb-2">Match Your Manuscript</h3>
                <p className="text-xs text-[#4A5B68] mb-4">
                  Computes 3-component fit scores: Semantic Fit (60%) + Topic Alignment (25%) + Citation Affinity (15%).
                  Max 6,000 characters.
                </p>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-[#12202B] mb-1">Title</label>
                    <input
                      type="text"
                      value={msTitle}
                      onChange={(e) => setMsTitle(e.target.value)}
                      placeholder="Enter manuscript title..."
                      className="w-full text-sm border border-[#D7DEE3] rounded-md px-3 py-2 focus:ring-1 focus:ring-[#0B5C7A]"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#12202B] mb-1">Abstract</label>
                    <textarea
                      rows={5}
                      value={msAbstract}
                      onChange={(e) => setMsAbstract(e.target.value)}
                      placeholder="Paste abstract..."
                      className="w-full text-sm border border-[#D7DEE3] rounded-md px-3 py-2 focus:ring-1 focus:ring-[#0B5C7A]"
                    />
                    <div className="text-right text-xs text-gray-400 mt-1">
                      {msTitle.length + msAbstract.length} / 6,000 chars
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <button
                      onClick={handleMatchManuscript}
                      disabled={matchingLoading || !msTitle || !msAbstract}
                      className="px-5 py-2 bg-[#0B5C7A] text-white rounded-md text-sm font-semibold hover:bg-[#08455C] disabled:opacity-50"
                    >
                      {matchingLoading ? 'Analyzing Scope Match...' : 'Find Matching Journals'}
                    </button>
                  </div>
                </div>
              </div>

              {/* Match Results */}
              {recommendations.length > 0 && (
                <div>
                  {/* Disclaimer banner */}
                  <div className="p-3.5 bg-[#FFF5E5] border border-[#FAD899] rounded-lg text-xs text-[#8A5200] mb-4 flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{disclaimer}</span>
                  </div>

                  <div className="space-y-4">
                    {recommendations.map((rec, idx) => (
                      <div key={idx} className="bg-white rounded-lg border border-[#D7DEE3] p-5 shadow-sm">
                        <div className="flex items-start justify-between pb-3 border-b border-[#D7DEE3]">
                          <div>
                            <div className="flex items-center space-x-2">
                              <h4 className="font-serif font-bold text-lg text-[#12202B]">{rec.journal.title}</h4>
                              {rec.journal.scopus_quartile && (
                                <span className="text-xs font-bold px-2 py-0.5 rounded bg-[#E3F0F5] text-[#0B4A63]">
                                  {rec.journal.scopus_quartile}
                                </span>
                              )}
                              {rec.journal.sinta_rank && (
                                <span className="text-xs font-bold px-2 py-0.5 rounded bg-[#E5F3E8] text-[#1F5429]">
                                  SINTA {rec.journal.sinta_rank}
                                </span>
                              )}
                              {rec.journal.is_oa && (
                                <span className="text-xs font-bold px-2 py-0.5 rounded bg-gray-100 text-gray-700">
                                  OPEN ACCESS
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-[#4A5B68] mt-1">
                              Publisher: {rec.journal.publisher} · Country: {rec.journal.country} · ISSN:{' '}
                              {rec.journal.issn_l || 'N/A'}
                            </div>
                          </div>

                          <div className="text-right">
                            <div className="text-xl font-bold text-[#0B5C7A]">
                              {Math.round(rec.match_score * 100)}%
                            </div>
                            <div className="text-xs text-gray-500">Fit Index</div>
                          </div>
                        </div>

                        {/* 3-Component Score Breakdown */}
                        <div className="grid grid-cols-3 gap-2 py-3 bg-[#F6F8F9] rounded-md px-3 my-3 text-xs">
                          <div>
                            <span className="text-gray-500">Semantic Fit (60%):</span>{' '}
                            <span className="font-semibold">
                              {Math.round(rec.score_breakdown.semantic_score * 100)}%
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500">Keyword Alignment (25%):</span>{' '}
                            <span className="font-semibold">
                              {Math.round(rec.score_breakdown.keyword_score * 100)}%
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500">Citation Affinity (15%):</span>{' '}
                            <span className="font-semibold">
                              {Math.round(rec.score_breakdown.citation_affinity * 100)}%
                            </span>
                          </div>
                        </div>

                        {/* Similar Recent Articles (JRN-007) */}
                        <div className="mt-3">
                          <div className="text-xs font-bold text-[#12202B] mb-1">
                            Similar Recent Articles with Ground-Truth DOIs:
                          </div>
                          <ul className="space-y-1 text-xs">
                            {rec.similar_recent_articles.map((art, aIdx) => (
                              <li key={aIdx} className="flex items-center space-x-1.5 text-[#4A5B68]">
                                <ExternalLink className="w-3 h-3 text-[#0B5C7A] shrink-0" />
                                <span className="line-clamp-1">{art.title}</span>
                                <span className="font-mono text-gray-400">({art.doi})</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Footer & Action Buttons */}
                        <div className="flex items-center justify-between pt-4 border-t border-[#D7DEE3] mt-4 text-xs">
                          <div className="flex items-center space-x-3 text-gray-500">
                            <span>
                              APC:{' '}
                              {rec.journal.apc_usd !== null && rec.journal.apc_usd !== undefined
                                ? rec.journal.apc_usd === 0
                                ? 'Free / None'
                                : `$${rec.journal.apc_usd}`
                                : 'Subscription / Unknown'}
                            </span>
                            <span>·</span>
                            <span>Data Freshness: {rec.journal.data_as_of}</span>
                          </div>

                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleOpenChecklist(rec.journal)}
                              className="px-3 py-1 bg-white border border-[#0B5C7A] text-[#0B5C7A] rounded font-medium hover:bg-[#E3F0F5]"
                            >
                              Submission Checklist
                            </button>
                            {rec.journal.guidelines_url && (
                              <a
                                href={rec.journal.guidelines_url}
                                target="_blank"
                                rel="noreferrer"
                                className="px-3 py-1 bg-[#0B5C7A] text-white rounded font-medium hover:bg-[#08455C] flex items-center space-x-1"
                              >
                                <span>Author Guidelines</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Directory Browse View */
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-lg border border-[#D7DEE3] flex items-center space-x-3">
                <Search className="w-4 h-4 text-[#4A5B68]" />
                <input
                  type="text"
                  placeholder="Search journals by title, scope keywords, or publisher..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && loadJournals()}
                  className="w-full text-sm focus:outline-none"
                />
                <button
                  onClick={loadJournals}
                  className="px-4 py-1.5 bg-[#0B5C7A] text-white rounded text-xs font-semibold"
                >
                  Search
                </button>
              </div>

              <div className="space-y-3">
                {journals.map((j) => (
                  <div key={j.id} className="bg-white p-4 rounded-lg border border-[#D7DEE3]">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <h4 className="font-serif font-bold text-base text-[#12202B]">{j.title}</h4>
                          {j.scopus_quartile && (
                            <span className="text-xs font-bold px-2 py-0.5 rounded bg-[#E3F0F5] text-[#0B4A63]">
                              {j.scopus_quartile}
                            </span>
                          )}
                          {j.sinta_rank && (
                            <span className="text-xs font-bold px-2 py-0.5 rounded bg-[#E5F3E8] text-[#1F5429]">
                              SINTA {j.sinta_rank}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-[#4A5B68] mt-1 line-clamp-2">{j.scope_text}</p>
                      </div>

                      <button
                        onClick={() => handleOpenChecklist(j)}
                        className="px-3 py-1 text-xs border border-[#0B5C7A] text-[#0B5C7A] rounded hover:bg-[#E3F0F5] font-semibold"
                      >
                        Checklist
                      </button>
                    </div>

                    <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100 mt-3">
                      <div>
                        APC: {j.apc_usd === 0 ? 'Free' : j.apc_usd ? `$${j.apc_usd}` : 'Subscription'} · Verified
                        Source: {j.provenance?.source || 'OpenAlex'}
                      </div>
                      <div className="flex items-center space-x-2">
                        {j.is_stale && <span className="text-amber-600 font-bold">Stale (&gt;12 mos)</span>}
                        <span>Fresh as of {j.data_as_of}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Submission Checklist Modal */}
      {checklistModal.open && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full p-6 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#D7DEE3] mb-4">
              <h3 className="font-serif font-bold text-lg text-[#12202B]">
                Submission Checklist: {checklistModal.journalTitle}
              </h3>
              <button
                onClick={() => setChecklistModal({ open: false, journalTitle: '', items: [] })}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {checklistModal.items.map((item, idx) => (
                <div key={idx} className="p-3 rounded-lg border border-[#D7DEE3] bg-[#FBFDFD] text-xs">
                  <div className="flex items-center justify-between font-bold text-[#12202B] mb-1">
                    <span>{item.item}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${
                        item.status === 'verified'
                          ? 'bg-[#E5F3E8] text-[#1F5429]'
                          : 'bg-[#FFF5E5] text-[#8A5200]'
                      }`}
                    >
                      {item.status === 'verified' ? 'Verified Item' : 'Verify Manually'}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-2">{item.requirement}</p>
                  {item.source_url && (
                    <a
                      href={item.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-[#0B5C7A] hover:underline flex items-center space-x-1"
                    >
                      <span>Authoritative Rule Source</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-4 border-t border-[#D7DEE3] mt-4">
              <button
                onClick={() => setChecklistModal({ open: false, journalTitle: '', items: [] })}
                className="px-4 py-2 bg-[#0B5C7A] text-white rounded-md text-sm font-medium"
              >
                Close Checklist
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
