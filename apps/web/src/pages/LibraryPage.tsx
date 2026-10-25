import React, { useState, useEffect } from 'react';
import { api, Project } from '../api/client';
import { Upload, FileText, CheckCircle2 } from 'lucide-react';

interface LibraryPageProps {
  activeProject: Project | null;
}

export const LibraryPage: React.FC<LibraryPageProps> = ({ activeProject }) => {
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFormat, setImportFormat] = useState<'ris' | 'bibtex' | 'csv'>('ris');
  const [importContent, setImportContent] = useState('');
  const [importReport, setImportReport] = useState<any | null>(null);
  const [importing, setImporting] = useState(false);

  const fetchItems = async () => {
    if (!activeProject) return;
    setLoading(true);
    try {
      const res = await api.getLibraryItems(activeProject.id);
      setItems(res.items);
      setTotal(res.total);
    } catch (err) {
      // Empty or error state
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [activeProject]);

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProject || !importContent.trim()) return;
    setImporting(true);
    setImportReport(null);
    try {
      const res = await api.importReferences(activeProject.id, importFormat, importContent);
      setImportReport(res.report);
      fetchItems();
    } catch (err: any) {
      alert(err.detail || 'Import failed');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl font-bold text-[#12202B]">
            Project Library & Collections
          </h1>
          <p className="text-sm text-[#4A5B68] mt-1">
            {activeProject ? `${activeProject.name} — ${total} works registered` : 'Select a project to view library'}
          </p>
        </div>

        {activeProject && (
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowImportModal(true)}
              className="inline-flex items-center space-x-1.5 px-3 py-2 bg-[#E3F0F5] hover:bg-[#d0e5ed] text-[#0B4A63] border border-[#B5D5E2] rounded-lg text-xs font-semibold transition-colors shadow-sm"
            >
              <Upload className="w-4 h-4" />
              <span>Import References (RIS/BibTeX/CSV)</span>
            </button>

            <div className="flex items-center space-x-1 border border-[#D7DEE3] rounded-lg p-1 bg-[#F6F8F9]">
              <span className="text-xs font-semibold text-[#4A5B68] px-2">Export:</span>
              <a
                href={api.getExportUrl(activeProject.id, 'bibtex')}
                download
                className="px-2 py-1 text-xs font-medium text-[#0B5C7A] hover:bg-white rounded transition-colors"
              >
                BibTeX
              </a>
              <a
                href={api.getExportUrl(activeProject.id, 'ris')}
                download
                className="px-2 py-1 text-xs font-medium text-[#0B5C7A] hover:bg-white rounded transition-colors"
              >
                RIS
              </a>
              <a
                href={api.getExportUrl(activeProject.id, 'csv')}
                download
                className="px-2 py-1 text-xs font-medium text-[#0B5C7A] hover:bg-white rounded transition-colors"
              >
                CSV
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Items Table */}
      <div className="bg-white rounded-xl border border-[#D7DEE3] overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-8 text-center text-sm text-[#4A5B68]">Loading library works...</div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <FileText className="w-8 h-8 text-[#8695A1] mx-auto" />
            <h3 className="font-serif text-base font-bold text-[#12202B]">Library is Empty</h3>
            <p className="text-sm text-[#4A5B68] max-w-md mx-auto">
              Search OpenAlex & Crossref or import existing RIS, BibTeX, or CSV bibliographies to populate your project evidence base.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="bg-[#F6F8F9] border-b border-[#D7DEE3] text-xs font-semibold text-[#34495A]">
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4 w-28">Year</th>
                  <th className="py-3 px-4 w-48">Venue</th>
                  <th className="py-3 px-4 w-48">DOI</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#D7DEE3]">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-[#F6F8F9]/50 transition-colors">
                    <td className="py-3.5 px-4 font-medium text-[#12202B]">
                      {item.title}
                    </td>
                    <td className="py-3.5 px-4 text-[#4A5B68]">{item.year || '—'}</td>
                    <td className="py-3.5 px-4 text-[#4A5B68] truncate max-w-xs">{item.venue || '—'}</td>
                    <td className="py-3.5 px-4 font-mono text-xs text-[#0B5C7A]">
                      {item.doi ? (
                        <a
                          href={`https://doi.org/${item.doi}`}
                          target="_blank"
                          rel="noreferrer"
                          className="hover:underline"
                        >
                          {item.doi}
                        </a>
                      ) : (
                        '—'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 shadow-xl border border-[#D7DEE3] space-y-4">
            <div className="flex items-center justify-between border-b border-[#D7DEE3] pb-3">
              <h3 className="font-serif text-lg font-bold text-[#12202B]">
                Import Bibliographic Records
              </h3>
              <button
                onClick={() => {
                  setShowImportModal(false);
                  setImportReport(null);
                }}
                className="text-gray-400 hover:text-gray-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleImport} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#34495A] mb-1">
                  Format Type
                </label>
                <div className="flex space-x-4 text-xs font-medium">
                  {(['ris', 'bibtex', 'csv'] as const).map((fmt) => (
                    <label key={fmt} className="flex items-center space-x-1.5 cursor-pointer">
                      <input
                        type="radio"
                        name="format"
                        value={fmt}
                        checked={importFormat === fmt}
                        onChange={() => setImportFormat(fmt)}
                        className="text-[#0B5C7A]"
                      />
                      <span className="uppercase">{fmt}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#34495A] mb-1">
                  Paste Raw File Text / Entries
                </label>
                <textarea
                  required
                  rows={8}
                  value={importContent}
                  onChange={(e) => setImportContent(e.target.value)}
                  placeholder={
                    importFormat === 'ris'
                      ? 'TY  - JOUR\nTI  - Systematic Review Example\nAU  - Smith, J.\nPY  - 2024\nER  -'
                      : importFormat === 'bibtex'
                      ? '@article{ref1,\n  title = {Systematic Review Example},\n  author = {Smith, J.},\n  year = {2024}\n}'
                      : 'Title,Authors,Year,Venue,DOI\nSystematic Review Example,Smith J,2024,Journal of AI,10.1234/5678'
                  }
                  className="w-full font-mono text-xs p-3 border border-[#D7DEE3] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0B5C7A]"
                />
              </div>

              {importReport && (
                <div className="p-4 rounded-lg bg-[#E4F3EA] border border-[#B7DEC5] text-xs space-y-1">
                  <div className="flex items-center space-x-1.5 font-bold text-[#14532D]">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Import Complete: {importReport.imported} imported, {importReport.skipped} skipped</span>
                  </div>
                  {importReport.errors?.length > 0 && (
                    <div className="text-[#8A1C1C] pt-1">
                      {importReport.errors.map((err: any, i: number) => (
                        <div key={i}>• Line {err.line}: {err.reason}</div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowImportModal(false);
                    setImportReport(null);
                  }}
                  className="px-4 py-2 text-sm text-[#4A5B68] hover:text-[#12202B]"
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={importing}
                  className="px-4 py-2 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                >
                  {importing ? 'Processing Records...' : 'Execute Import'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
