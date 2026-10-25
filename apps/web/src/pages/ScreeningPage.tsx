import React, { useState, useEffect, useCallback } from 'react';
import { api, Project } from '../api/client';
import { 
  Check, 
  X, 
  HelpCircle, 
  Layers, 
  AlertTriangle, 
  Scale, 
  FileText,
  Keyboard,
  ShieldAlert
} from 'lucide-react';

interface ScreeningPageProps {
  activeProject: Project | null;
}

export const ScreeningPage: React.FC<ScreeningPageProps> = ({ activeProject }) => {
  const [protocol, setProtocol] = useState<any | null>(null);
  const [queue, setQueue] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [stage, setStage] = useState<'title_abstract' | 'full_text'>('title_abstract');
  
  // Exclusion reasons
  const [reasons, setReasons] = useState<any[]>([]);
  const [showExcludeModal, setShowExcludeModal] = useState(false);
  const [selectedReason, setSelectedReason] = useState('WRONG_POPULATION');
  const [excludeNotes, setExcludeNotes] = useState('');

  // Agreement and PRISMA stats
  const [agreement, setAgreement] = useState<any | null>(null);
  const [prisma, setPrisma] = useState<any | null>(null);
  const [conflicts, setConflicts] = useState<any[]>([]);

  // Protocol creation
  const [showProtocolModal, setShowProtocolModal] = useState(false);
  const [newQuestion, setNewQuestion] = useState('What is the clinical efficacy and safety of LLM agents in healthcare?');
  const [newInclusion, setNewInclusion] = useState('Empirical clinical trials, peer-reviewed, human subjects');
  const [newExclusion, setNewExclusion] = useState('Editorials, animal models, non-English studies');

  const loadScreeningData = async () => {
    if (!activeProject) return;
    setLoading(true);
    try {
      // 1. Fetch protocol
      const p = await api.request<any>(`/projects/${activeProject.id}/protocols`);
      setProtocol(p);

      // 2. Fetch exclusion reasons
      const r = await api.request<any[]>(`/projects/${activeProject.id}/exclusion-reasons`);
      setReasons(r);

      // 3. Fetch screening queue
      const q = await api.request<any[]>(`/projects/${activeProject.id}/screening/queue?stage=${stage}`);
      setQueue(q);
      setCurrentIndex(0);

      // 4. Fetch Cohen's Kappa agreement
      const agree = await api.request<any>(`/projects/${activeProject.id}/screening/agreement?stage=${stage}`);
      setAgreement(agree);

      // 5. Fetch PRISMA counts
      const pr = await api.request<any>(`/projects/${activeProject.id}/prisma`);
      setPrisma(pr);

      // 6. Fetch conflicts
      const conf = await api.request<any[]>(`/projects/${activeProject.id}/screening/conflicts?stage=${stage}`);
      setConflicts(conf);
    } catch (err) {
      // Empty or error state
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScreeningData();
  }, [activeProject, stage]);

  const handleDecision = async (verdict: 'include' | 'exclude' | 'maybe', reasonCode?: string, notes?: string) => {
    if (!activeProject || queue.length === 0) return;
    const currentItem = queue[currentIndex];

    try {
      await api.request(`/projects/${activeProject.id}/screening/decisions`, {
        method: 'POST',
        body: JSON.stringify({
          work_id: currentItem.work_id,
          stage,
          verdict,
          reason_code: reasonCode,
          notes,
        }),
      });

      // Advance queue
      if (currentIndex + 1 < queue.length) {
        setCurrentIndex(currentIndex + 1);
      } else {
        // Re-fetch when batch is completed
        loadScreeningData();
      }
    } catch (err: any) {
      alert(err.detail || 'Failed to submit screening decision');
    }
  };

  const handleCreateProtocol = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProject) return;
    try {
      const p = await api.request<any>(`/projects/${activeProject.id}/protocols`, {
        method: 'POST',
        body: JSON.stringify({
          question: newQuestion,
          pico: { P: 'Patients', I: 'LLM Agents', C: 'Control', O: 'Outcomes' },
          inclusion_criteria: newInclusion,
          exclusion_criteria: newExclusion,
        }),
      });
      setProtocol(p);
      setShowProtocolModal(false);
      loadScreeningData();
    } catch (err: any) {
      alert(err.detail || 'Failed to initialize protocol');
    }
  };

  // Keyboard shortcut listener (SCR-017)
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (showExcludeModal || showProtocolModal || queue.length === 0) return;
      const key = e.key.toLowerCase();
      if (key === 'i') {
        handleDecision('include');
      } else if (key === 'e') {
        setShowExcludeModal(true);
      } else if (key === 'm') {
        handleDecision('maybe');
      }
    },
    [showExcludeModal, showProtocolModal, queue, currentIndex, activeProject]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (!activeProject) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-[#4A5B68]">
        Please select an active project from the top navbar.
      </div>
    );
  }

  const currentWork = queue[currentIndex];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Top Protocol & Agreement Bar */}
      <div className="bg-white rounded-xl border border-[#D7DEE3] p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <div className="flex items-center space-x-1 border border-[#D7DEE3] rounded-lg p-0.5 bg-[#F6F8F9] text-xs font-semibold">
              <button
                onClick={() => setStage('title_abstract')}
                className={`px-2.5 py-1 rounded-md transition-colors ${
                  stage === 'title_abstract' ? 'bg-white text-[#0B5C7A] shadow-sm' : 'text-[#4A5B68] hover:text-[#12202B]'
                }`}
              >
                Title & Abstract
              </button>
              <button
                onClick={() => setStage('full_text')}
                className={`px-2.5 py-1 rounded-md transition-colors ${
                  stage === 'full_text' ? 'bg-white text-[#0B5C7A] shadow-sm' : 'text-[#4A5B68] hover:text-[#12202B]'
                }`}
              >
                Full-Text
              </button>
            </div>
            <span className="text-gray-300">•</span>
            {protocol ? (
              <span className="text-xs text-[#14532D] font-medium">Protocol v{protocol.version} Active</span>
            ) : (
              <span className="text-xs text-[#8A1C1C] font-semibold">Protocol v1 Required</span>
            )}
          </div>
          <h2 className="font-serif text-lg font-bold text-[#12202B]">
            {protocol ? protocol.question : 'No review protocol registered yet'}
          </h2>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          {!protocol ? (
            <button
              onClick={() => setShowProtocolModal(true)}
              className="px-4 py-2 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-xs font-bold transition-colors"
            >
              Initialize Protocol v1
            </button>
          ) : (
            <div className="flex items-center space-x-2">
              {agreement && (
                <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-[#E3F0F5] border border-[#B5D5E2] rounded-lg text-xs font-medium text-[#0B4A63]">
                  <Scale className="w-4 h-4 text-[#0B5C7A]" />
                  <span>
                    Cohen's κ: <strong>{agreement.cohen_kappa !== null ? agreement.cohen_kappa : 'N/A'}</strong> ({agreement.interpretation})
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Screening Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Screening Card */}
        <div className="lg:col-span-2 space-y-4">
          {loading ? (
            <div className="bg-white rounded-xl border border-[#D7DEE3] p-12 text-center text-sm text-[#4A5B68]">
              Loading screening workbench...
            </div>
          ) : !protocol ? (
            <div className="bg-white rounded-xl border border-[#D7DEE3] p-12 text-center space-y-3">
              <ShieldAlert className="w-8 h-8 text-[#8A1C1C] mx-auto" />
              <h3 className="font-serif text-lg font-bold text-[#12202B]">Screening is Disabled</h3>
              <p className="text-sm text-[#4A5B68] max-w-md mx-auto">
                Per requirement SCR-001, screening cannot commence until a versioned systematic review protocol is defined.
              </p>
              <button
                onClick={() => setShowProtocolModal(true)}
                className="mt-2 px-4 py-2 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-xs font-semibold"
              >
                Create Protocol v1
              </button>
            </div>
          ) : queue.length === 0 ? (
            <div className="bg-white rounded-xl border border-[#D7DEE3] p-12 text-center space-y-3">
              <FileText className="w-8 h-8 text-[#14532D] mx-auto" />
              <h3 className="font-serif text-lg font-bold text-[#12202B]">Queue Completed!</h3>
              <p className="text-sm text-[#4A5B68] max-w-md mx-auto">
                You have reviewed all available records in this stage. Check the PRISMA diagram or conflict queue for disagreements.
              </p>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm space-y-6">
              {/* Progress Tracker */}
              <div className="flex items-center justify-between text-xs text-[#4A5B68] pb-3 border-b border-[#D7DEE3]">
                <span className="font-medium">
                  Reviewing Item <strong>{currentIndex + 1}</strong> of <strong>{queue.length}</strong>
                </span>
                <div className="flex items-center space-x-1 font-mono text-xs text-[#0B5C7A]">
                  <Keyboard className="w-3.5 h-3.5" />
                  <span>Keys: [I] Include · [E] Exclude · [M] Maybe</span>
                </div>
              </div>

              {/* Work Content */}
              <div className="space-y-4">
                <h3 className="font-serif text-xl font-bold text-[#12202B] leading-snug">
                  {currentWork.title}
                </h3>

                <div className="flex flex-wrap items-center gap-3 text-xs text-[#4A5B68]">
                  {currentWork.year && <span className="font-semibold text-[#0B5C7A]">{currentWork.year}</span>}
                  {currentWork.venue && <span>{currentWork.venue}</span>}
                  {currentWork.doi && (
                    <a
                      href={`https://doi.org/${currentWork.doi}`}
                      target="_blank"
                      rel="noreferrer"
                      className="font-mono text-gray-500 hover:text-[#0B5C7A] underline"
                    >
                      DOI: {currentWork.doi}
                    </a>
                  )}
                </div>

                <div className="pt-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#34495A] mb-2">Abstract</h4>
                  <p className="text-sm text-[#12202B] leading-relaxed bg-[#F6F8F9] p-4 rounded-lg border border-[#D7DEE3] max-h-72 overflow-y-auto">
                    {currentWork.abstract || 'No abstract available for this record.'}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-[#D7DEE3]">
                <button
                  onClick={() => handleDecision('include')}
                  className="flex items-center justify-center space-x-2 py-3 px-4 bg-[#E4F3EA] hover:bg-[#d0ead9] text-[#14532D] border border-[#B7DEC5] rounded-xl font-bold text-sm transition-all shadow-sm"
                >
                  <Check className="w-5 h-5" />
                  <span>Include [I]</span>
                </button>

                <button
                  onClick={() => setShowExcludeModal(true)}
                  className="flex items-center justify-center space-x-2 py-3 px-4 bg-[#FBE4E4] hover:bg-[#f7d2d2] text-[#8A1C1C] border border-[#EBB5B5] rounded-xl font-bold text-sm transition-all shadow-sm"
                >
                  <X className="w-5 h-5" />
                  <span>Exclude [E]</span>
                </button>

                <button
                  onClick={() => handleDecision('maybe')}
                  className="flex items-center justify-center space-x-2 py-3 px-4 bg-[#FDF0DC] hover:bg-[#fae2c0] text-[#7A3E00] border border-[#EBCB98] rounded-xl font-bold text-sm transition-all shadow-sm"
                >
                  <HelpCircle className="w-5 h-5" />
                  <span>Maybe [M]</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: PRISMA 2020 Flow Summary */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-[#D7DEE3] p-5 shadow-sm space-y-4">
            <div className="flex items-center space-x-2 text-[#0B5C7A]">
              <Layers className="w-5 h-5" />
              <h3 className="font-serif text-base font-bold text-[#12202B]">
                PRISMA 2020 Flow Counts
              </h3>
            </div>

            {prisma ? (
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-lg bg-[#F6F8F9] border border-[#D7DEE3] flex justify-between items-center">
                  <span className="text-[#34495A]">1. Records Identified</span>
                  <strong className="text-sm font-bold text-[#12202B]">{prisma.boxes.identified}</strong>
                </div>

                <div className="p-3 rounded-lg bg-[#F6F8F9] border border-[#D7DEE3] flex justify-between items-center">
                  <span className="text-[#34495A]">2. Duplicates Removed</span>
                  <strong className="text-sm font-bold text-[#8A1C1C]">{prisma.boxes.duplicates_removed}</strong>
                </div>

                <div className="p-3 rounded-lg bg-[#F6F8F9] border border-[#D7DEE3] flex justify-between items-center">
                  <span className="text-[#34495A]">3. Records Screened (TA)</span>
                  <strong className="text-sm font-bold text-[#0B5C7A]">{prisma.boxes.records_screened}</strong>
                </div>

                <div className="p-3 rounded-lg bg-[#F6F8F9] border border-[#D7DEE3] flex justify-between items-center">
                  <span className="text-[#34495A]">4. Excluded at TA</span>
                  <strong className="text-sm font-bold text-[#8A1C1C]">{prisma.boxes.excluded_ta}</strong>
                </div>

                <div className="p-3 rounded-lg bg-[#E3F0F5] border border-[#B5D5E2] flex justify-between items-center text-[#0B4A63]">
                  <span>5. Reports Assessed (FT)</span>
                  <strong className="text-sm font-bold">{prisma.boxes.reports_assessed_ft}</strong>
                </div>

                <div className="p-3 rounded-lg bg-[#E4F3EA] border border-[#B7DEC5] flex justify-between items-center text-[#14532D]">
                  <span className="font-bold">6. Studies Included</span>
                  <strong className="text-base font-bold">{prisma.boxes.studies_included}</strong>
                </div>

                {prisma.reconciliation.ok ? (
                  <div className="text-[11px] text-[#14532D] flex items-center space-x-1 pt-1">
                    <span>✓ PRISMA count arithmetic reconciled 100%</span>
                  </div>
                ) : (
                  <div className="text-[11px] text-[#8A1C1C] pt-1">
                    ⚠ Reconciliation discrepancy detected
                  </div>
                )}
              </div>
            ) : (
              <div className="text-xs text-[#4A5B68]">PRISMA data loading...</div>
            )}
          </div>

          {/* Conflict Alert Box */}
          {conflicts.length > 0 && (
            <div className="bg-[#FDF0DC] border border-[#EBCB98] rounded-xl p-4 text-xs space-y-2">
              <div className="flex items-center space-x-1.5 font-bold text-[#7A3E00]">
                <AlertTriangle className="w-4 h-4" />
                <span>{conflicts.length} Review Disagreements Detected</span>
              </div>
              <p className="text-[#7A3E00]">
                Reviewers have submitted diverging verdicts. Project owner must resolve conflicts to close the stage.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Exclusion Reason Modal */}
      {showExcludeModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-[#D7DEE3] space-y-4">
            <h3 className="font-serif text-lg font-bold text-[#12202B]">
              Select Controlled Exclusion Reason
            </h3>
            <p className="text-xs text-[#4A5B68]">
              Per requirement SCR-005, all exclusion decisions must cite a verified reason code for PRISMA auditing.
            </p>

            <div className="space-y-2">
              {reasons.map((r) => (
                <label
                  key={r.code}
                  className={`flex items-start space-x-3 p-3 rounded-lg border cursor-pointer text-xs transition-colors ${
                    selectedReason === r.code
                      ? 'bg-[#E3F0F5] border-[#0B5C7A] text-[#0B4A63]'
                      : 'border-[#D7DEE3] hover:bg-[#F6F8F9]'
                  }`}
                >
                  <input
                    type="radio"
                    name="reason"
                    value={r.code}
                    checked={selectedReason === r.code}
                    onChange={() => setSelectedReason(r.code)}
                    className="mt-0.5 text-[#0B5C7A]"
                  />
                  <div>
                    <div className="font-semibold">{r.code}</div>
                    <div className="text-[#4A5B68] mt-0.5">{r.label}</div>
                  </div>
                </label>
              ))}
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#34495A] mb-1">
                Optional Reviewer Notes
              </label>
              <textarea
                value={excludeNotes}
                onChange={(e) => setExcludeNotes(e.target.value)}
                placeholder="Specific reasons for exclusion..."
                rows={2}
                className="w-full text-xs p-2.5 border border-[#D7DEE3] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0B5C7A]"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                onClick={() => setShowExcludeModal(false)}
                className="px-4 py-2 text-xs text-[#4A5B68] hover:text-[#12202B]"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowExcludeModal(false);
                  handleDecision('exclude', selectedReason, excludeNotes);
                }}
                className="px-4 py-2 bg-[#8A1C1C] hover:bg-[#721717] text-white rounded-lg text-xs font-bold transition-colors"
              >
                Confirm Exclusion
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Protocol Creation Modal */}
      {showProtocolModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl border border-[#D7DEE3] space-y-4">
            <h3 className="font-serif text-lg font-bold text-[#12202B]">
              Define Review Protocol (v1)
            </h3>
            <form onSubmit={handleCreateProtocol} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-[#34495A] mb-1">
                  Primary Research Question
                </label>
                <input
                  type="text"
                  required
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  className="w-full p-2.5 border border-[#D7DEE3] rounded-lg focus:ring-2 focus:ring-[#0B5C7A]"
                />
              </div>

              <div>
                <label className="block font-semibold text-[#34495A] mb-1">
                  Inclusion Criteria
                </label>
                <textarea
                  rows={2}
                  value={newInclusion}
                  onChange={(e) => setNewInclusion(e.target.value)}
                  className="w-full p-2.5 border border-[#D7DEE3] rounded-lg focus:ring-2 focus:ring-[#0B5C7A]"
                />
              </div>

              <div>
                <label className="block font-semibold text-[#34495A] mb-1">
                  Exclusion Criteria
                </label>
                <textarea
                  rows={2}
                  value={newExclusion}
                  onChange={(e) => setNewExclusion(e.target.value)}
                  className="w-full p-2.5 border border-[#D7DEE3] rounded-lg focus:ring-2 focus:ring-[#0B5C7A]"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowProtocolModal(false)}
                  className="px-4 py-2 text-gray-500"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#0B5C7A] text-white font-bold rounded-lg"
                >
                  Activate Protocol
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
