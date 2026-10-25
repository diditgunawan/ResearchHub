import React, { useState } from 'react';
import { api, Project } from '../api/client';
import { Search, Plus, Check, ExternalLink, Filter, Clock } from 'lucide-react';

interface SearchPageProps {
  activeProject: Project | null;
}

export const SearchPage: React.FC<SearchPageProps> = ({ activeProject }) => {
  const [query, setQuery] = useState('large language models systematic review');
  const [yearFrom, setYearFrom] = useState<number | undefined>(2020);
  const [yearTo, setYearTo] = useState<number | undefined>(2026);
  const [oaOnly, setOaOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [sourceStatus, setSourceStatus] = useState<any[]>([]);
  const [addedIds, setAddedIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.searchWorks(query, yearFrom, yearTo, oaOnly);
      setResults(res.items);
      setSourceStatus(res.source_status);
    } catch (err: any) {
      setError(err.detail || 'Federated search failed. Please verify query.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToLibrary = async (item: any) => {
    if (!activeProject) {
      alert('Please select or create an active project first.');
      return;
    }
    try {
      await api.addToLibrary(activeProject.id, item.doi || item.title);
      setAddedIds((prev) => new Set(prev).add(item.doi || item.title));
    } catch (err) {
      alert('Failed to add work to library');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Search Header */}
      <div className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm">
        <h1 className="font-serif text-2xl font-bold text-[#12202B] mb-1">
          Federated Scholarly Search
        </h1>
        <p className="text-sm text-[#4A5B68] mb-6">
          Query OpenAlex, Crossref, and PubMed simultaneously with verified open metadata provenance.
        </p>

        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="w-5 h-5 absolute left-3.5 top-3.5 text-[#4A5B68]" />
              <input
                type="text"
                required
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search by keywords, research questions, or title..."
                className="w-full pl-11 pr-4 py-3 bg-[#F6F8F9] border border-[#D7DEE3] rounded-lg text-sm text-[#12202B] font-medium focus:outline-none focus:ring-2 focus:ring-[#0B5C7A] focus:bg-white transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50 shadow-sm shrink-0"
            >
              {loading ? 'Searching Sources...' : 'Search Works'}
            </button>
          </div>

          {/* Filters Row */}
          <div className="flex flex-wrap items-center gap-4 pt-2 text-xs text-[#34495A]">
            <div className="flex items-center space-x-1.5 font-medium">
              <Filter className="w-3.5 h-3.5 text-[#0B5C7A]" />
              <span>Filters:</span>
            </div>
            <div className="flex items-center space-x-2">
              <label>From Year:</label>
              <input
                type="number"
                value={yearFrom || ''}
                onChange={(e) => setYearFrom(e.target.value ? Number(e.target.value) : undefined)}
                placeholder="2020"
                className="w-20 px-2 py-1 border border-[#D7DEE3] rounded bg-white text-xs"
              />
            </div>
            <div className="flex items-center space-x-2">
              <label>To Year:</label>
              <input
                type="number"
                value={yearTo || ''}
                onChange={(e) => setYearTo(e.target.value ? Number(e.target.value) : undefined)}
                placeholder="2026"
                className="w-20 px-2 py-1 border border-[#D7DEE3] rounded bg-white text-xs"
              />
            </div>
            <label className="flex items-center space-x-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={oaOnly}
                onChange={(e) => setOaOnly(e.target.checked)}
                className="rounded border-[#D7DEE3] text-[#0B5C7A] focus:ring-[#0B5C7A]"
              />
              <span>Open Access Only</span>
            </label>
          </div>
        </form>
      </div>

      {/* Source Status Bar */}
      {sourceStatus.length > 0 && (
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xs font-semibold text-[#4A5B68] uppercase tracking-wider">Source Status:</span>
          {sourceStatus.map((s) => (
            <div
              key={s.source}
              className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
                s.status === 'ok'
                  ? 'bg-[#E4F3EA] text-[#14532D] border-[#B7DEC5]'
                  : 'bg-[#FDF0DC] text-[#7A3E00] border-[#EBCB98]'
              }`}
            >
              <Clock className="w-3 h-3" />
              <span className="font-semibold uppercase">{s.source}</span>
              <span>•</span>
              <span>{s.latency_ms} ms</span>
              <span>({s.items_count} records)</span>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-[#FBE4E4] text-[#8A1C1C] border border-[#EBB5B5] text-sm">
          {error}
        </div>
      )}

      {/* Results List */}
      <div className="space-y-4">
        {results.map((item, idx) => {
          const isAdded = addedIds.has(item.doi || item.title);
          return (
            <div
              key={idx}
              className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm hover:border-[#0B5C7A] transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                  <h3 className="font-serif text-lg font-bold text-[#12202B] leading-snug">
                    {item.title}
                  </h3>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[#4A5B68]">
                    {item.authors && item.authors.length > 0 && (
                      <span className="font-medium text-[#12202B]">
                        {item.authors.map((a: any) => a.name).slice(0, 3).join(', ')}
                        {item.authors.length > 3 ? ' et al.' : ''}
                      </span>
                    )}
                    {item.venue?.name && <span>{item.venue.name}</span>}
                    {item.year && <span className="font-semibold text-[#0B5C7A]">{item.year}</span>}
                    {item.doi && (
                      <span className="font-mono text-gray-500">DOI: {item.doi}</span>
                    )}
                  </div>

                  {item.abstract && (
                    <p className="text-sm text-[#34495A] line-clamp-3 leading-relaxed pt-1">
                      {item.abstract}
                    </p>
                  )}

                  <div className="flex items-center space-x-3 pt-2">
                    {item.doi && (
                      <a
                        href={`https://doi.org/${item.doi}`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center space-x-1 text-xs font-semibold text-[#0B5C7A] hover:underline"
                      >
                        <span>View Publisher DOI</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                    {item.oa_url && (
                      <a
                        href={item.oa_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center space-x-1 text-xs font-semibold text-[#14532D] hover:underline"
                      >
                        <span>Open Access PDF</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => handleAddToLibrary(item)}
                  disabled={isAdded}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold shrink-0 transition-colors ${
                    isAdded
                      ? 'bg-[#E4F3EA] text-[#14532D] border border-[#B7DEC5]'
                      : 'bg-[#E3F0F5] hover:bg-[#d0e5ed] text-[#0B4A63] border border-[#B5D5E2]'
                  }`}
                >
                  {isAdded ? (
                    <>
                      <Check className="w-4 h-4" />
                      <span>Added to Library</span>
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4" />
                      <span>Add to Library</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
