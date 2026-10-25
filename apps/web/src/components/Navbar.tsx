import React from 'react';
import { User, Project } from '../api/client';
import { GitFork, Search, ShieldCheck, LogOut, FolderKanban } from 'lucide-react';

interface NavbarProps {
  user: User | null;
  projects: Project[];
  activeProject: Project | null;
  onSelectProject: (project: Project) => void;
  onLogout: () => void;
  activeTab: string;
  onSelectTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  user,
  projects,
  activeProject,
  onSelectProject,
  onLogout,
  activeTab,
  onSelectTab,
}) => {
  return (
    <header className="bg-white border-b border-[#D7DEE3] sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 cursor-pointer" onClick={() => onSelectTab('dashboard')}>
            <div className="w-9 h-9 rounded-lg bg-[#0B5C7A] flex items-center justify-center text-white font-bold text-lg">
              RF
            </div>
            <div>
              <span className="font-serif text-xl font-bold tracking-tight text-[#12202B]">ResearchForge</span>
              <span className="ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-[#E3F0F5] text-[#0B4A63]">
                Grounded v0.1
              </span>
            </div>
          </div>

          {/* Project Selector */}
          {user && (
            <div className="flex items-center space-x-2 pl-4 border-l border-[#D7DEE3]">
              <FolderKanban className="w-4 h-4 text-[#4A5B68]" />
              <select
                value={activeProject?.id || ''}
                onChange={(e) => {
                  const p = projects.find((proj) => proj.id === e.target.value);
                  if (p) onSelectProject(p);
                }}
                className="text-sm bg-white border border-[#D7DEE3] rounded-md px-2.5 py-1 text-[#12202B] font-medium focus:outline-none focus:ring-1 focus:ring-[#0B5C7A]"
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.role})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        {user && (
          <nav className="flex items-center space-x-1">
            <button
              onClick={() => onSelectTab('dashboard')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'dashboard'
                  ? 'bg-[#E3F0F5] text-[#0B4A63]'
                  : 'text-[#4A5B68] hover:text-[#12202B] hover:bg-[#F6F8F9]'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => onSelectTab('search')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'search'
                  ? 'bg-[#E3F0F5] text-[#0B4A63]'
                  : 'text-[#4A5B68] hover:text-[#12202B] hover:bg-[#F6F8F9]'
              }`}
            >
              <Search className="w-4 h-4" />
              <span>Search Works</span>
            </button>
            <button
              onClick={() => onSelectTab('library')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'library'
                  ? 'bg-[#E3F0F5] text-[#0B4A63]'
                  : 'text-[#4A5B68] hover:text-[#12202B] hover:bg-[#F6F8F9]'
              }`}
            >
              <FolderKanban className="w-4 h-4" />
              <span>Library</span>
            </button>
            <button
              onClick={() => onSelectTab('screening')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'screening'
                  ? 'bg-[#E3F0F5] text-[#0B4A63]'
                  : 'text-[#4A5B68] hover:text-[#12202B] hover:bg-[#F6F8F9]'
              }`}
            >
              <Search className="w-4 h-4" />
              <span>Screening</span>
            </button>
            <button
              onClick={() => onSelectTab('synthesis')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'synthesis'
                  ? 'bg-[#E3F0F5] text-[#0B4A63]'
                  : 'text-[#4A5B68] hover:text-[#12202B] hover:bg-[#F6F8F9]'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Grounded Synthesis</span>
            </button>
            <button
              onClick={() => onSelectTab('lineage')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'lineage'
                  ? 'bg-[#E3F0F5] text-[#0B4A63]'
                  : 'text-[#4A5B68] hover:text-[#12202B] hover:bg-[#F6F8F9]'
              }`}
            >
              <GitFork className="w-4 h-4" />
              <span>Lineage DAG</span>
            </button>
            <button
              onClick={() => onSelectTab('journals')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'journals'
                  ? 'bg-[#E3F0F5] text-[#0B4A63]'
                  : 'text-[#4A5B68] hover:text-[#12202B] hover:bg-[#F6F8F9]'
              }`}
            >
              <FolderKanban className="w-4 h-4" />
              <span>Journals</span>
            </button>
          </nav>
        )}

        {/* User Info & Actions */}
        {user ? (
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm font-medium text-[#12202B]">{user.email}</div>
              <div className="text-xs text-[#4A5B68]">Lead Researcher</div>
            </div>
            <button
              onClick={onLogout}
              className="p-2 text-[#4A5B68] hover:text-[#8A1C1C] hover:bg-[#FBE4E4] rounded-md transition-colors"
              title="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="text-sm text-[#4A5B68]">Not authenticated</div>
        )}
      </div>
    </header>
  );
};
