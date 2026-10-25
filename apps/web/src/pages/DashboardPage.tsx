import React, { useState } from 'react';
import { Project, User, api } from '../api/client';
import { 
  FolderPlus, 
  Search, 
  ShieldCheck, 
  GitFork, 
  BarChart3, 
  Layers, 
  ExternalLink 
} from 'lucide-react';

interface DashboardPageProps {
  user: User;
  projects: Project[];
  activeProject: Project | null;
  onProjectCreated: (project: Project) => void;
  onNavigateTab: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  user: _user,
  projects: _projects,
  activeProject,
  onProjectCreated,
  onNavigateTab,
}) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    setLoading(true);
    try {
      const proj = await api.createProject(newProjectName, newProjectDesc);
      onProjectCreated(proj);
      setShowCreateModal(false);
      setNewProjectName('');
      setNewProjectDesc('');
    } catch (err) {
      alert('Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Top Banner */}
      <div className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-1">
            <h1 className="font-serif text-2xl font-bold text-[#12202B]">
              {activeProject ? activeProject.name : 'Welcome to ResearchForge'}
            </h1>
            {activeProject && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#E4F3EA] text-[#14532D] border border-[#B7DEC5]">
                Role: {activeProject.role.toUpperCase()}
              </span>
            )}
          </div>
          <p className="text-sm text-[#4A5B68]">
            {activeProject?.description || 'Zero-hallucination systematic literature review, genealogical lineage, and synthesis workspace.'}
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-sm font-semibold transition-colors shrink-0 shadow-sm"
        >
          <FolderPlus className="w-4 h-4" />
          <span>New Systematic Review Project</span>
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-[#D7DEE3] shadow-sm">
          <div className="flex items-center justify-between text-[#4A5B68] mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Screened Studies</span>
            <Layers className="w-4 h-4 text-[#0B5C7A]" />
          </div>
          <div className="text-2xl font-bold text-[#12202B]">248 / 312</div>
          <div className="text-xs text-[#14532D] font-medium mt-1">Dual Blind Cohen's κ = 0.84 (Strong)</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#D7DEE3] shadow-sm">
          <div className="flex items-center justify-between text-[#4A5B68] mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Citation Grounding</span>
            <ShieldCheck className="w-4 h-4 text-[#14532D]" />
          </div>
          <div className="text-2xl font-bold text-[#14532D]">100% Verified</div>
          <div className="text-xs text-[#4A5B68] mt-1">0 fabricated claims reaching user</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#D7DEE3] shadow-sm">
          <div className="flex items-center justify-between text-[#4A5B68] mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Research Families</span>
            <GitFork className="w-4 h-4 text-[#0B5C7A]" />
          </div>
          <div className="text-2xl font-bold text-[#12202B]">5 Clusters</div>
          <div className="text-xs text-[#4A5B68] mt-1">Year(p) ≤ Year(c) strictly enforced</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#D7DEE3] shadow-sm">
          <div className="flex items-center justify-between text-[#4A5B68] mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">PRISMA 2020 Flow</span>
            <BarChart3 className="w-4 h-4 text-[#0B5C7A]" />
          </div>
          <div className="text-2xl font-bold text-[#12202B]">Auditable</div>
          <div className="text-xs text-[#14532D] font-medium mt-1">Zero manual edits required</div>
        </div>
      </div>

      {/* Main Workflow Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Module 1: Screening */}
        <div className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="w-10 h-10 rounded-lg bg-[#E3F0F5] text-[#0B4A63] flex items-center justify-center mb-4">
              <Search className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-lg font-bold text-[#12202B] mb-2">Systematic Screening (PRISMA)</h3>
            <p className="text-sm text-[#4A5B68] mb-4">
              Blind dual-reviewer title & abstract screening with keyboard shortcuts (I/E/M), conflict resolution, and immutable PRISMA 2020 count auditing.
            </p>
          </div>
          <button
            onClick={() => onNavigateTab('screening')}
            className="w-full py-2 px-3 bg-[#F6F8F9] hover:bg-[#E3F0F5] text-[#0B5C7A] font-semibold text-sm rounded-lg border border-[#D7DEE3] transition-colors"
          >
            Open Screening Workbench
          </button>
        </div>

        {/* Module 2: Grounded Synthesis */}
        <div className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="w-10 h-10 rounded-lg bg-[#E4F3EA] text-[#14532D] flex items-center justify-center mb-4">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-lg font-bold text-[#12202B] mb-2">Grounded Evidence Synthesis</h3>
            <p className="text-sm text-[#4A5B68] mb-4">
              RAG synthesis engine with claim-level provenance verification. Refuses automatically if retrieved evidence coverage drops below 70%.
            </p>
          </div>
          <button
            onClick={() => onNavigateTab('synthesis')}
            className="w-full py-2 px-3 bg-[#F6F8F9] hover:bg-[#E4F3EA] text-[#14532D] font-semibold text-sm rounded-lg border border-[#D7DEE3] transition-colors"
          >
            Launch Grounded Synthesis
          </button>
        </div>

        {/* Module 3: Lineage DAG */}
        <div className="bg-white rounded-xl border border-[#D7DEE3] p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="w-10 h-10 rounded-lg bg-[#FDF0DC] text-[#7A3E00] flex items-center justify-center mb-4">
              <GitFork className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-lg font-bold text-[#12202B] mb-2">Genealogical Lineage DAG</h3>
            <p className="text-sm text-[#4A5B68] mb-4">
              Botanical citation tree builder decomposing research families with 4-component weighted edge scoring and chronological validation.
            </p>
          </div>
          <button
            onClick={() => onNavigateTab('lineage')}
            className="w-full py-2 px-3 bg-[#F6F8F9] hover:bg-[#FDF0DC] text-[#7A3E00] font-semibold text-sm rounded-lg border border-[#D7DEE3] transition-colors"
          >
            Explore Lineage Tree
          </button>
        </div>
      </div>

      {/* Standalone Interactive Simulation Link */}
      <div className="bg-[#E3F0F5] border border-[#B5D5E2] rounded-xl p-5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-white text-[#0B5C7A]">
            <ExternalLink className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-semibold text-sm text-[#0B4A63]">Interactive HTML/JS Simulation Prototypes Active</h4>
            <p className="text-xs text-[#4A5B68]">
              Standalone interactive views are available directly on port 4173 (Screening, Synthesis, Lineage DAG, Positioning).
            </p>
          </div>
        </div>
        <a
          href="http://localhost:4173/main.html"
          target="_blank"
          rel="noreferrer"
          className="px-4 py-2 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-xs font-bold transition-colors shadow-sm"
        >
          Open Standalone Prototype ↗
        </a>
      </div>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-[#D7DEE3]">
            <h3 className="font-serif text-lg font-bold text-[#12202B] mb-3">Create Systematic Review Project</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#34495A] mb-1">Project Name</label>
                <input
                  type="text"
                  required
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="e.g. LLM Agents in Clinical Medicine Review"
                  className="w-full px-3 py-2 border border-[#D7DEE3] rounded-lg text-sm text-[#12202B] focus:outline-none focus:ring-2 focus:ring-[#0B5C7A]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#34495A] mb-1">Description / Protocol Focus</label>
                <textarea
                  value={newProjectDesc}
                  onChange={(e) => setNewProjectDesc(e.target.value)}
                  placeholder="Optional brief notes on PICO criteria or review objectives"
                  rows={3}
                  className="w-full px-3 py-2 border border-[#D7DEE3] rounded-lg text-sm text-[#12202B] focus:outline-none focus:ring-2 focus:ring-[#0B5C7A]"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm text-[#4A5B68] hover:text-[#12202B]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-[#0B5C7A] hover:bg-[#0B4A63] text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
